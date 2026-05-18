"""Unit tests for the post-1.0.6 in-process updater finalize flow.

We can't easily exercise the GitHub-network or PyInstaller-bootloader paths
from a test, so we focus on the deterministic pieces: arg parsing, the
.new.exe -> .exe swap on disk, and the wait-for-PID-to-die helper using a
real short-lived subprocess so the WinAPI path actually gets exercised.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

from tracker import updater


@pytest.fixture(autouse=True)
def _silence_update_log(monkeypatch):
    """Evita que los tests escriban en %LOCALAPPDATA%\\IsaacTracker\\update.log."""
    monkeypatch.setattr(updater, "_update_log_path", lambda: None)


@pytest.fixture
def _fast_retries(monkeypatch):
    """Acorta los delays del retry de finalize_swap para que los tests no esperen segundos."""
    monkeypatch.setattr(updater, "_FINALIZE_RETRY_DELAYS", (0.0,) * 6)


def test_parse_finalize_pid_returns_pid_when_flag_present():
    argv = ["IsaacTracker.new.exe", "--finalize-update", "12345"]
    assert updater.parse_finalize_pid(argv) == 12345


def test_parse_finalize_pid_returns_none_when_flag_missing():
    assert updater.parse_finalize_pid(["IsaacTracker.exe"]) is None
    assert updater.parse_finalize_pid([]) is None


def test_parse_finalize_pid_returns_none_when_value_missing():
    assert updater.parse_finalize_pid(["IsaacTracker.exe", "--finalize-update"]) is None


def test_parse_finalize_pid_returns_none_when_value_not_int():
    assert updater.parse_finalize_pid(["foo", "--finalize-update", "notanumber"]) is None


def test_parse_finalize_pid_ignores_unrelated_args():
    argv = ["foo", "--something-else", "x", "--finalize-update", "42", "--more"]
    assert updater.parse_finalize_pid(argv) == 42


def test_finalize_swap_renames_new_exe_to_exe(tmp_path):
    new_exe = tmp_path / updater.NEW_EXE_NAME
    new_exe.write_bytes(b"new contents")
    old_exe = tmp_path / updater.EXE_NAME
    old_exe.write_bytes(b"old contents")

    assert updater._finalize_swap(tmp_path) is True

    assert not new_exe.exists()
    assert old_exe.exists()
    assert old_exe.read_bytes() == b"new contents"


def test_finalize_swap_works_when_old_exe_absent(tmp_path):
    new_exe = tmp_path / updater.NEW_EXE_NAME
    new_exe.write_bytes(b"fresh")

    assert updater._finalize_swap(tmp_path) is True

    assert not new_exe.exists()
    assert (tmp_path / updater.EXE_NAME).read_bytes() == b"fresh"


def test_finalize_swap_is_noop_when_new_exe_absent(tmp_path):
    # Simulates the safety case where the finalize thread is invoked but the
    # .new.exe got cleaned up or never existed (e.g. user ran the flag manually).
    assert updater._finalize_swap(tmp_path) is True
    assert not (tmp_path / updater.NEW_EXE_NAME).exists()
    assert not (tmp_path / updater.EXE_NAME).exists()


def test_finalize_swap_removes_legacy_bat(tmp_path):
    (tmp_path / updater.NEW_EXE_NAME).write_bytes(b"new")
    legacy = tmp_path / updater.LEGACY_SWAP_SCRIPT_NAME
    legacy.write_text("@echo off\r\n")

    assert updater._finalize_swap(tmp_path) is True
    assert not legacy.exists()


def test_wait_for_pid_to_die_returns_true_when_process_exits():
    # Spawn a real short-lived subprocess. Sleep 0.2 s, then exit. Wait up to
    # 5 s. On both Windows (WaitForSingleObject) and POSIX (os.kill polling),
    # we should observe the exit and return True.
    proc = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(0.2)"]
    )
    try:
        start = time.monotonic()
        assert updater._wait_for_pid_to_die(proc.pid, 5.0) is True
        elapsed = time.monotonic() - start
        assert elapsed < 4.0, f"Wait took unexpectedly long: {elapsed:.2f}s"
    finally:
        proc.wait(timeout=5)


def test_wait_for_pid_to_die_returns_false_on_timeout():
    proc = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(3)"]
    )
    try:
        assert updater._wait_for_pid_to_die(proc.pid, 0.3) is False
    finally:
        proc.terminate()
        proc.wait(timeout=5)


def test_wait_for_pid_to_die_returns_true_for_nonexistent_pid():
    # A PID that almost certainly doesn't exist. Both backends should report
    # the process as gone.
    assert updater._wait_for_pid_to_die(999_999_999, 0.5) is True


def test_finalize_pending_update_swaps_after_old_pid_exits(tmp_path):
    (tmp_path / updater.NEW_EXE_NAME).write_bytes(b"freshly downloaded")
    (tmp_path / updater.EXE_NAME).write_bytes(b"about to be overwritten")

    proc = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(0.1)"]
    )
    try:
        ok = updater.finalize_pending_update(proc.pid, exe_dir=tmp_path)
    finally:
        proc.wait(timeout=5)
    assert ok is True
    assert not (tmp_path / updater.NEW_EXE_NAME).exists()
    assert (tmp_path / updater.EXE_NAME).read_bytes() == b"freshly downloaded"


def test_finalize_pending_update_bails_when_exe_dir_unknown(monkeypatch):
    monkeypatch.setattr(updater, "_exe_dir", lambda: None)
    # Should not raise; just return False since we can't act.
    assert updater.finalize_pending_update(123) is False


@pytest.mark.parametrize(
    "candidate,current,expected",
    [
        ("1.0.7", "1.0.6", True),
        ("v1.0.7", "1.0.6", True),
        ("1.0.6", "1.0.6", False),
        ("1.0.5", "1.0.6", False),
        ("garbage", "1.0.6", False),
        ("1.0.7", "garbage", False),
    ],
)
def test_is_newer(candidate, current, expected):
    assert updater._is_newer(candidate, current) is expected


# ===== Retry de _finalize_swap (cubre el bug del bloqueo transitorio de Defender) =====

def test_finalize_swap_retries_when_replace_fails_then_succeeds(tmp_path, monkeypatch, _fast_retries):
    """Defender bloquea el primer intento; el segundo funciona. Antes del fix esto
    devolvía False y dejaba ambos archivos en disco."""
    (tmp_path / updater.EXE_NAME).write_bytes(b"old")
    (tmp_path / updater.NEW_EXE_NAME).write_bytes(b"new")

    real_replace = os.replace
    calls = {"n": 0}

    def flaky_replace(src, dst):
        calls["n"] += 1
        if calls["n"] < 3:
            raise PermissionError("simulated Defender lock on IsaacTracker.exe")
        real_replace(src, dst)

    monkeypatch.setattr(updater.os, "replace", flaky_replace)

    assert updater._finalize_swap(tmp_path) is True
    assert calls["n"] == 3
    assert (tmp_path / updater.EXE_NAME).read_bytes() == b"new"
    assert not (tmp_path / updater.NEW_EXE_NAME).exists()


def test_finalize_swap_returns_false_when_all_retries_exhausted(tmp_path, monkeypatch, _fast_retries):
    """Si ningún intento consigue el rename, devolvemos False y dejamos los
    archivos como están — la auto-recuperación del próximo arranque debería
    reintentarlo."""
    (tmp_path / updater.EXE_NAME).write_bytes(b"old")
    (tmp_path / updater.NEW_EXE_NAME).write_bytes(b"new")

    def always_fail(src, dst):
        raise PermissionError("locked forever")

    monkeypatch.setattr(updater.os, "replace", always_fail)

    assert updater._finalize_swap(tmp_path) is False
    # Ambos archivos siguen en disco para que la próxima ejecución los rescate.
    assert (tmp_path / updater.EXE_NAME).read_bytes() == b"old"
    assert (tmp_path / updater.NEW_EXE_NAME).read_bytes() == b"new"


# ===== Auto-recuperación al arrancar =====

def test_maybe_recover_relaunches_when_pending_new_exe_exists(tmp_path, monkeypatch):
    """Existe un IsaacTracker.new.exe huérfano y estamos corriendo como el
    IsaacTracker.exe estable → debemos llamar al finalizer y pedir salida."""
    new_exe = tmp_path / updater.NEW_EXE_NAME
    new_exe.write_bytes(b"\0" * (updater._MIN_PLAUSIBLE_EXE_BYTES + 1))

    monkeypatch.setattr(updater, "_exe_path", lambda: tmp_path / updater.EXE_NAME)

    launched = {}

    def fake_launch(path, pid):
        launched["path"] = path
        launched["pid"] = pid

    monkeypatch.setattr(updater, "_launch_finalizer", fake_launch)

    assert updater.maybe_recover_pending_swap(exe_dir=tmp_path) is True
    assert launched["path"] == new_exe
    assert launched["pid"] == os.getpid()


def test_maybe_recover_ignores_tiny_partial_download(tmp_path, monkeypatch):
    """Una descarga parcial NO debe relanzarse: el binario incompleto
    crashearía al arrancar y dejaría al usuario sin app."""
    new_exe = tmp_path / updater.NEW_EXE_NAME
    new_exe.write_bytes(b"\0" * 1024)  # 1 KB, claramente parcial

    monkeypatch.setattr(updater, "_exe_path", lambda: tmp_path / updater.EXE_NAME)

    called = []
    monkeypatch.setattr(updater, "_launch_finalizer", lambda *a, **kw: called.append(a))

    assert updater.maybe_recover_pending_swap(exe_dir=tmp_path) is False
    assert called == []


def test_maybe_recover_is_noop_when_no_pending_new_exe(tmp_path, monkeypatch):
    monkeypatch.setattr(updater, "_exe_path", lambda: tmp_path / updater.EXE_NAME)
    called = []
    monkeypatch.setattr(updater, "_launch_finalizer", lambda *a, **kw: called.append(a))

    assert updater.maybe_recover_pending_swap(exe_dir=tmp_path) is False
    assert called == []


def test_maybe_recover_is_noop_when_running_from_new_exe(tmp_path, monkeypatch):
    """Si por alguna razón ya estamos corriendo desde el .new.exe (usuario lo
    abrió a mano), NO relanzamos otro .new.exe — sería un bucle infinito."""
    new_exe = tmp_path / updater.NEW_EXE_NAME
    new_exe.write_bytes(b"\0" * (updater._MIN_PLAUSIBLE_EXE_BYTES + 1))

    monkeypatch.setattr(updater, "_exe_path", lambda: new_exe)

    called = []
    monkeypatch.setattr(updater, "_launch_finalizer", lambda *a, **kw: called.append(a))

    assert updater.maybe_recover_pending_swap(exe_dir=tmp_path) is False
    assert called == []


def test_maybe_recover_is_noop_when_not_frozen(tmp_path, monkeypatch):
    """Cuando corremos desde fuente (no .exe), _exe_path devuelve None
    y no hacemos nada."""
    monkeypatch.setattr(updater, "_exe_path", lambda: None)
    called = []
    monkeypatch.setattr(updater, "_launch_finalizer", lambda *a, **kw: called.append(a))

    new_exe = tmp_path / updater.NEW_EXE_NAME
    new_exe.write_bytes(b"\0" * (updater._MIN_PLAUSIBLE_EXE_BYTES + 1))

    assert updater.maybe_recover_pending_swap(exe_dir=tmp_path) is False
    assert called == []
