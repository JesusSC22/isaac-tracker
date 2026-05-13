import os
import time
from pathlib import Path

import pytest

from tracker.exceptions import SaveNotFoundError
from tracker.save_locator import locate_save_file, find_save_directory


def test_find_save_directory_repentance_plus_priority(tmp_path, monkeypatch):
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    rep_plus = tmp_path / "Documents" / "My Games" / "Binding of Isaac Repentance+"
    rep = tmp_path / "Documents" / "My Games" / "Binding of Isaac Repentance"
    rep_plus.mkdir(parents=True)
    rep.mkdir(parents=True)
    assert find_save_directory() == rep_plus


def test_find_save_directory_falls_back_to_repentance(tmp_path, monkeypatch):
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    rep = tmp_path / "Documents" / "My Games" / "Binding of Isaac Repentance"
    rep.mkdir(parents=True)
    assert find_save_directory() == rep


def test_find_save_directory_raises_when_missing(tmp_path, monkeypatch):
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    with pytest.raises(SaveNotFoundError):
        find_save_directory()


def test_locate_save_file_picks_most_recent(tmp_path, monkeypatch):
    save_dir = tmp_path / "Documents" / "My Games" / "Binding of Isaac Repentance+"
    save_dir.mkdir(parents=True)
    monkeypatch.setenv("USERPROFILE", str(tmp_path))

    for slot, mtime_offset in [(1, -300), (2, -100), (3, -200)]:
        f = save_dir / f"persistentgamedata{slot}.dat"
        f.write_bytes(b"x")
        now = time.time()
        os.utime(f, (now + mtime_offset, now + mtime_offset))

    result = locate_save_file()
    assert result.name == "persistentgamedata2.dat"


def test_locate_save_file_raises_when_no_dat_files(tmp_path, monkeypatch):
    save_dir = tmp_path / "Documents" / "My Games" / "Binding of Isaac Repentance+"
    save_dir.mkdir(parents=True)
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    with pytest.raises(SaveNotFoundError):
        locate_save_file()
