"""Auto-update system: check GitHub for newer releases, download, swap.

Swap strategy (Windows): instead of killing ourselves and letting an external
.bat rename + relaunch us, we launch the freshly downloaded .new.exe directly
while the old process is still alive, passing ``--finalize-update <old-pid>``.
The new process starts up normally (so Defender has all the time it needs to
scan it), then in a background thread waits for the old PID to die, deletes
the old .exe, and renames itself from IsaacTracker.new.exe to IsaacTracker.exe.

This avoids the PyInstaller-onefile "Failed to load Python DLL" race that
appeared when a .bat tried to launch the .exe immediately after replacing it
on disk.

All failures (network, parse, missing assets, permission denied) are caught
and surfaced as a None return / mode="manual" hint rather than raised --- the
update path must never crash the app or surface an error to the user.
"""
from __future__ import annotations

import ctypes
import json
import logging
import os
import re
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser
from ctypes import wintypes
from pathlib import Path
from typing import Any, Callable, Sequence

from tracker._version import __version__

logger = logging.getLogger("tracker.updater")

GITHUB_REPO = "JesusSC22/isaac-tracker"
EXE_NAME = "IsaacTracker.exe"
NEW_EXE_NAME = "IsaacTracker.new.exe"
LEGACY_SWAP_SCRIPT_NAME = "_update.bat"
FINALIZE_FLAG = "--finalize-update"
USER_AGENT = f"IsaacTracker/{__version__}"
NETWORK_TIMEOUT = 5.0
DOWNLOAD_TIMEOUT = 60.0
FINALIZE_WAIT_TIMEOUT = 30.0
FINALIZE_POST_DOWNLOAD_GRACE = 1.0
# Reintentos del rename final. Defender (u otros AV) a veces escanea el
# IsaacTracker.exe viejo justo en el momento que el viejo proceso muere,
# lo que hace que el primer os.replace falle con "acceso denegado". Estos
# delays cubren ~10 s, suficiente para casi todos los bloqueos transitorios.
_FINALIZE_RETRY_DELAYS: tuple[float, ...] = (0.0, 0.5, 1.0, 1.5, 2.5, 4.0)
# Tamaño mínimo creíble para un IsaacTracker.exe completo. Por debajo de
# esto asumimos que el .new.exe es una descarga parcial y NO la usamos
# para auto-recuperación (lanzarla solo dejaría al usuario sin app).
_MIN_PLAUSIBLE_EXE_BYTES = 5 * 1024 * 1024

_SEMVER_RE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")


def _parse_version(s: str) -> tuple[int, int, int] | None:
    m = _SEMVER_RE.match(s.strip())
    if not m:
        return None
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)))


def _is_newer(candidate: str, current: str) -> bool:
    c = _parse_version(candidate)
    r = _parse_version(current)
    if c is None or r is None:
        return False
    return c > r


def _exe_path() -> Path | None:
    """Return the path to the running .exe, or None if running from source."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve()
    return None


def _exe_dir() -> Path | None:
    p = _exe_path()
    return p.parent if p else None


def can_self_update() -> bool:
    """True iff we are a frozen .exe and can write to our own directory."""
    d = _exe_dir()
    if d is None:
        return False
    try:
        return os.access(d, os.W_OK)
    except OSError:
        return False


def _fetch_latest_release() -> dict[str, Any] | None:
    """Hit GitHub releases API. Returns parsed JSON dict, or None on any error."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/vnd.github+json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=NETWORK_TIMEOUT) as resp:
            data = resp.read()
        return json.loads(data)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError, ValueError) as e:
        logger.info("Update check skipped: %s", e)
        return None


def check_for_update() -> dict[str, Any] | None:
    """Synchronous check. Returns dict with keys
        {version, asset_url, html_url, mode}
    if a newer version is available and the binary can be downloaded;
    None otherwise (no update, network error, malformed response, etc.).
    mode is "auto" if can_self_update() else "manual".
    """
    release = _fetch_latest_release()
    if not release:
        return None
    tag = release.get("tag_name") or ""
    if not _is_newer(tag, __version__):
        return None
    asset_url = None
    for asset in release.get("assets", []) or []:
        if asset.get("name") == EXE_NAME:
            asset_url = asset.get("browser_download_url")
            break
    if not asset_url:
        logger.info("Latest release %s has no %s asset", tag, EXE_NAME)
        return None
    return {
        "version": tag.lstrip("v"),
        "asset_url": asset_url,
        "html_url": release.get("html_url", ""),
        "mode": "auto" if can_self_update() else "manual",
    }


def check_for_update_async(on_result: Callable[[dict[str, Any] | None], None]) -> None:
    """Run check_for_update on a daemon thread; call on_result with the result."""
    def _run() -> None:
        try:
            on_result(check_for_update())
        except Exception:
            logger.exception("Update check raised unexpectedly")
            try:
                on_result(None)
            except Exception:
                pass
    threading.Thread(target=_run, daemon=True, name="updater-check").start()


def _download_to(url: str, dest: Path, on_progress: Callable[[int, int | None], None]) -> bool:
    """Stream URL to dest. on_progress(downloaded_bytes, total_or_None) per chunk.
    Returns True on success. On failure, deletes any partial file."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=DOWNLOAD_TIMEOUT) as resp:
            total_hdr = resp.headers.get("Content-Length")
            total = int(total_hdr) if total_hdr and total_hdr.isdigit() else None
            downloaded = 0
            chunk_size = 64 * 1024
            with open(dest, "wb") as f:
                while True:
                    chunk = resp.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    try:
                        on_progress(downloaded, total)
                    except Exception:
                        pass
        return True
    except Exception as e:
        logger.warning("Download failed: %s", e)
        try:
            if dest.exists():
                dest.unlink()
        except OSError:
            pass
        return False


def _launch_finalizer(new_exe: Path, old_pid: int) -> None:
    """Spawn the freshly downloaded .new.exe with the finalize flag, detached.

    The new process must outlive us, so we set CREATE_NEW_PROCESS_GROUP and
    close inherited handles. We do NOT pass DETACHED_PROCESS / CREATE_NO_WINDOW:
    a --windowed PyInstaller binary has no console, so console-control flags
    are unnecessary and (per MSDN) some are mutually exclusive in ways that
    have surprised this code before.
    """
    flags = 0
    if sys.platform == "win32":
        flags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200)
    subprocess.Popen(
        [str(new_exe), FINALIZE_FLAG, str(old_pid)],
        creationflags=flags,
        close_fds=True,
        cwd=str(new_exe.parent),
    )


def apply_update(asset_url: str, on_progress: Callable[[int, int | None], None]) -> dict[str, Any]:
    """Download new exe, launch it with finalize flag, ask caller to exit.

    Returns {"ok": True, "should_exit": True} on success (caller should close
    the app cleanly), or {"ok": False, "error": "<reason>"} on failure.
    On manual fallback (no write permission), returns {"ok": False, "fallback": "browser"}.
    """
    exe_dir = _exe_dir()
    if exe_dir is None:
        return {"ok": False, "error": "not-frozen"}
    if not can_self_update():
        return {"ok": False, "fallback": "browser"}
    dest = exe_dir / NEW_EXE_NAME
    # Clean up any stale partial download from a prior aborted attempt.
    if dest.exists():
        try:
            dest.unlink()
        except OSError:
            pass
    if not _download_to(asset_url, dest, on_progress):
        return {"ok": False, "error": "download-failed"}
    # Brief pause lets Defender finish its on-write scan of the freshly
    # created .exe before we hand it to CreateProcess. The download itself
    # already gave Defender most of the window; this is belt-and-suspenders.
    time.sleep(FINALIZE_POST_DOWNLOAD_GRACE)
    try:
        _launch_finalizer(dest, os.getpid())
    except OSError as e:
        logger.warning("Could not launch finalizer: %s", e)
        return {"ok": False, "error": "launch-finalizer-failed"}
    return {"ok": True, "should_exit": True}


def parse_finalize_pid(argv: Sequence[str]) -> int | None:
    """Extract the old PID from ``argv`` if ``--finalize-update <pid>`` is set.

    Returns None when the flag is missing or its argument is malformed.
    Accepts the flag anywhere after argv[0]; ignores everything else.
    """
    for i, token in enumerate(argv):
        if token == FINALIZE_FLAG and i + 1 < len(argv):
            try:
                return int(argv[i + 1])
            except (TypeError, ValueError):
                return None
    return None


def _wait_for_pid_to_die(pid: int, timeout_seconds: float) -> bool:
    """Block until ``pid`` exits or ``timeout_seconds`` elapses (Windows only).

    Returns True iff the process is gone by the time we return. If we cannot
    open the process (already exited, or no permission), we treat it as dead.
    """
    if sys.platform != "win32":
        # Non-Windows fallback: poll os.kill(pid, 0). Auto-update is Windows-only
        # in practice, but keep this branch so the function is unit-testable.
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                return True
            except PermissionError:
                return True
            time.sleep(0.1)
        try:
            os.kill(pid, 0)
            return False
        except (ProcessLookupError, PermissionError):
            return True

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    kernel32.WaitForSingleObject.restype = wintypes.DWORD
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL

    PROCESS_SYNCHRONIZE = 0x00100000
    WAIT_OBJECT_0 = 0x00000000

    h = kernel32.OpenProcess(PROCESS_SYNCHRONIZE, False, pid)
    if not h:
        return True
    try:
        timeout_ms = max(0, int(timeout_seconds * 1000))
        return kernel32.WaitForSingleObject(h, timeout_ms) == WAIT_OBJECT_0
    finally:
        kernel32.CloseHandle(h)


def _update_log_path() -> Path | None:
    """Return the path to the persistent updater log, or None if unavailable.

    On Windows we use ``%LOCALAPPDATA%\\IsaacTracker\\update.log``. Tests can
    redirect by overriding the ``LOCALAPPDATA`` environment variable.
    """
    try:
        if sys.platform == "win32":
            base = os.environ.get("LOCALAPPDATA")
            if not base:
                return None
            d = Path(base) / "IsaacTracker"
        else:
            d = Path.home() / ".isaac-tracker"
        d.mkdir(parents=True, exist_ok=True)
        return d / "update.log"
    except OSError:
        return None


def _ulog(msg: str) -> None:
    """Append a timestamped line to the persistent updater log. Best-effort.

    Keeps the file under ~256KB by truncating to the last 64KB when it grows.
    Independent of the stdlib logging config (which the app disables by
    default) so we always get a record of what the auto-update path did.
    """
    p = _update_log_path()
    if p is None:
        return
    try:
        if p.exists() and p.stat().st_size > 256 * 1024:
            with p.open("rb") as f:
                f.seek(-64 * 1024, os.SEEK_END)
                tail = f.read()
            p.write_bytes(tail)
        line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} v{__version__} pid={os.getpid()} {msg}\n"
        with p.open("a", encoding="utf-8") as f:
            f.write(line)
    except OSError:
        pass


def _finalize_swap(exe_dir: Path) -> bool:
    """Rename ``IsaacTracker.new.exe`` to ``IsaacTracker.exe`` in ``exe_dir``.

    Reintenta el rename varias veces para tolerar bloqueos transitorios de
    Windows Defender (u otros AV) que escanean el .exe viejo justo cuando el
    viejo proceso acaba de morir, lo que hace fallar el primer intento con
    "acceso denegado". También limpia el legado ``_update.bat`` heredado de
    versiones anteriores a 1.0.7.

    Returns True on success; False if every retry failed (en cuyo caso ambos
    archivos quedan en disco y el siguiente arranque debería reintentarlo
    vía :func:`maybe_recover_pending_swap`).
    """
    target = exe_dir / EXE_NAME
    source = exe_dir / NEW_EXE_NAME
    if not source.exists():
        # Nothing to swap (e.g. invoked manually with the flag). Treat as ok.
        return True
    last_err: OSError | None = None
    for delay in _FINALIZE_RETRY_DELAYS:
        if delay:
            time.sleep(delay)
        try:
            # os.replace atomically overwrites the old .exe if it still exists;
            # Windows allows renaming over a non-running .exe file just fine.
            os.replace(source, target)
            last_err = None
            break
        except OSError as e:
            last_err = e
            _ulog(f"finalize_swap retry: {e}")
    if last_err is not None:
        logger.warning("Finalize rename failed after retries: %s", last_err)
        _ulog(f"finalize_swap FAILED after {len(_FINALIZE_RETRY_DELAYS)} attempts: {last_err}")
        return False
    _ulog("finalize_swap ok")
    legacy_bat = exe_dir / LEGACY_SWAP_SCRIPT_NAME
    if legacy_bat.exists():
        try:
            legacy_bat.unlink()
        except OSError:
            pass
    return True


def finalize_pending_update(old_pid: int, exe_dir: Path | None = None) -> bool:
    """Wait for the old process to exit, then swap .new.exe -> .exe on disk.

    Returns True if the swap completed (or there was nothing to do); False if
    we timed out waiting for the old process or the rename itself failed.
    Safe to call when ``exe_dir`` doesn't contain a .new.exe (no-op).
    """
    if exe_dir is None:
        exe_dir = _exe_dir()
    if exe_dir is None:
        return False
    _ulog(f"finalize: waiting for old pid={old_pid}")
    died = _wait_for_pid_to_die(old_pid, FINALIZE_WAIT_TIMEOUT)
    if not died:
        logger.warning("Old PID %s did not exit within %ss", old_pid, FINALIZE_WAIT_TIMEOUT)
        _ulog(f"finalize: old pid={old_pid} did not die within {FINALIZE_WAIT_TIMEOUT}s")
        return False
    return _finalize_swap(exe_dir)


def finalize_pending_update_async(old_pid: int) -> threading.Thread:
    """Fire-and-forget background finalizer used at startup."""
    def _run() -> None:
        try:
            finalize_pending_update(old_pid)
        except Exception:
            logger.exception("Finalize thread crashed")
            _ulog("finalize thread crashed (see app logger for traceback)")
    t = threading.Thread(target=_run, daemon=True, name="updater-finalize")
    t.start()
    return t


def maybe_recover_pending_swap(exe_dir: Path | None = None) -> bool:
    """Detect a pending .new.exe left over by a previous failed swap and
    relaunch it in finalize mode.

    Llamada al arrancar (cuando ``--finalize-update`` NO está en argv). Si
    encontramos un ``IsaacTracker.new.exe`` adyacente a nuestro propio .exe
    estable, asumimos que un update anterior se quedó a medias y lanzamos
    ese binario con el flag de finalize pasándole nuestro PID. El caller
    debe salir si esta función retorna True.

    Requiere que el archivo ``.new.exe`` tenga un tamaño plausible — así
    evitamos relanzar una descarga parcial dejada por un cierre brusco a
    mitad de descarga, que dejaría al usuario sin app.

    Returns True iff hemos lanzado el finalizer (= el caller debe terminar).
    """
    if exe_dir is None:
        exe_dir = _exe_dir()
    if exe_dir is None:
        return False
    current = _exe_path()
    if current is None:
        return False
    # Solo recuperamos cuando estamos corriendo desde el .exe estable. Si
    # ya estamos corriendo desde .new.exe (caso raro: el usuario lo abrió
    # directamente), no relanzamos otro .new.exe — sería un bucle.
    if current.name.lower() != EXE_NAME.lower():
        return False
    new_exe = exe_dir / NEW_EXE_NAME
    if not new_exe.exists():
        return False
    try:
        size = new_exe.stat().st_size
    except OSError:
        return False
    if size < _MIN_PLAUSIBLE_EXE_BYTES:
        _ulog(f"recover: ignoring tiny .new.exe ({size} bytes), likely a partial download")
        return False
    _ulog(f"recover: found pending .new.exe ({size} bytes), relaunching for finalize")
    try:
        _launch_finalizer(new_exe, os.getpid())
    except OSError as e:
        logger.warning("Auto-recovery launch failed: %s", e)
        _ulog(f"recover: launch failed: {e}")
        return False
    return True


def open_release_page(html_url: str) -> bool:
    """Fallback for manual mode: open the release page in the default browser."""
    if not html_url:
        return False
    try:
        return bool(webbrowser.open(html_url))
    except Exception:
        return False
