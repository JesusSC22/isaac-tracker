import time
from pathlib import Path

from tracker.watcher import SaveWatcher


def test_single_change_fires_once_after_debounce(tmp_path):
    f = tmp_path / "persistentgamedata1.dat"
    f.write_bytes(b"a")
    calls = []
    w = SaveWatcher(tmp_path, on_change=lambda: calls.append(time.time()), debounce_ms=200)
    w.start()
    try:
        time.sleep(0.1)
        f.write_bytes(b"ab")
        time.sleep(0.6)
        assert len(calls) == 1
    finally:
        w.stop()


def test_multiple_changes_within_window_coalesce(tmp_path):
    f = tmp_path / "persistentgamedata1.dat"
    f.write_bytes(b"a")
    calls = []
    w = SaveWatcher(tmp_path, on_change=lambda: calls.append(time.time()), debounce_ms=300)
    w.start()
    try:
        time.sleep(0.1)
        for byte in [b"ab", b"abc", b"abcd"]:
            f.write_bytes(byte)
            time.sleep(0.05)
        time.sleep(0.7)
        assert len(calls) == 1
    finally:
        w.stop()


def test_changes_in_different_windows_fire_separately(tmp_path):
    f = tmp_path / "persistentgamedata1.dat"
    f.write_bytes(b"a")
    calls = []
    w = SaveWatcher(tmp_path, on_change=lambda: calls.append(time.time()), debounce_ms=150)
    w.start()
    try:
        time.sleep(0.1)
        f.write_bytes(b"ab")
        time.sleep(0.6)
        f.write_bytes(b"abc")
        time.sleep(0.6)
        assert len(calls) == 2
    finally:
        w.stop()


def test_ignores_non_dat_files(tmp_path):
    calls = []
    w = SaveWatcher(tmp_path, on_change=lambda: calls.append(time.time()), debounce_ms=150)
    w.start()
    try:
        time.sleep(0.1)
        (tmp_path / "log.txt").write_bytes(b"junk")
        time.sleep(0.5)
        assert len(calls) == 0
    finally:
        w.stop()


def test_matches_repentance_plus_naming(tmp_path):
    calls = []
    w = SaveWatcher(tmp_path, on_change=lambda: calls.append(time.time()), debounce_ms=150)
    w.start()
    try:
        time.sleep(0.1)
        # Real Repentance+ filename in Steam userdata
        (tmp_path / "rep+persistentgamedata1.dat").write_bytes(b"x")
        time.sleep(0.5)
        assert len(calls) == 1
    finally:
        w.stop()
