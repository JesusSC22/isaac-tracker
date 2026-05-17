import os
import time
from pathlib import Path

import pytest

from tracker.exceptions import SaveNotFoundError
from tracker.save_locator import (
    locate_save_file,
    find_steam_userdata_roots,
    iter_repentance_plus_saves,
)


def test_find_steam_userdata_roots_uses_explicit_steam_path(tmp_path, monkeypatch):
    steam = tmp_path / "Steam"
    (steam / "userdata" / "111111" / "250900" / "remote").mkdir(parents=True)
    monkeypatch.setattr(
        "tracker.save_locator._read_steam_path_from_registry",
        lambda: str(steam),
    )
    roots = list(find_steam_userdata_roots())
    assert (steam / "userdata") in roots


def test_find_steam_userdata_roots_falls_back_to_common_locations(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "tracker.save_locator._read_steam_path_from_registry",
        lambda: None,
    )
    steam1 = tmp_path / "Program Files (x86)" / "Steam"
    (steam1 / "userdata").mkdir(parents=True)
    monkeypatch.setattr(
        "tracker.save_locator._FALLBACK_STEAM_PATHS_WINDOWS",
        [steam1],
    )
    roots = list(find_steam_userdata_roots())
    assert steam1 / "userdata" in roots


def test_iter_repentance_plus_saves_finds_steam_files(tmp_path, monkeypatch):
    udata = tmp_path / "Steam" / "userdata"
    (udata / "1111" / "250900" / "remote").mkdir(parents=True)
    (udata / "2222" / "250900" / "remote").mkdir(parents=True)
    a = udata / "1111" / "250900" / "remote" / "rep+persistentgamedata1.dat"
    b = udata / "2222" / "250900" / "remote" / "rep+persistentgamedata2.dat"
    c = udata / "1111" / "250900" / "remote" / "rep_persistentgamedata1.dat"  # rep_ ignored
    for f in (a, b, c):
        f.write_bytes(b"x")
    monkeypatch.setattr(
        "tracker.save_locator.find_steam_userdata_roots",
        lambda: [udata],
    )
    monkeypatch.setenv("USERPROFILE", str(tmp_path / "no-docs"))
    saves = list(iter_repentance_plus_saves())
    assert a in saves
    assert b in saves
    assert c not in saves


def test_locate_save_file_picks_most_recent_across_steamids(tmp_path, monkeypatch):
    udata = tmp_path / "Steam" / "userdata"
    (udata / "1111" / "250900" / "remote").mkdir(parents=True)
    (udata / "2222" / "250900" / "remote").mkdir(parents=True)
    older = udata / "1111" / "250900" / "remote" / "rep+persistentgamedata1.dat"
    newer = udata / "2222" / "250900" / "remote" / "rep+persistentgamedata1.dat"
    older.write_bytes(b"x")
    newer.write_bytes(b"x")
    now = time.time()
    os.utime(older, (now - 1000, now - 1000))
    os.utime(newer, (now - 10, now - 10))
    monkeypatch.setattr(
        "tracker.save_locator.find_steam_userdata_roots",
        lambda: [udata],
    )
    monkeypatch.setenv("USERPROFILE", str(tmp_path / "no-docs"))
    assert locate_save_file() == newer


def test_locate_save_file_falls_back_to_documents_backups(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "tracker.save_locator.find_steam_userdata_roots",
        lambda: [],
    )
    docs_backups = tmp_path / "Documents" / "My Games" / "Binding of Isaac Repentance+" / "save_backups"
    docs_backups.mkdir(parents=True)
    f = docs_backups / "20260513.rep+persistentgamedata1.dat"
    f.write_bytes(b"x")
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    assert locate_save_file() == f


def test_locate_save_file_raises_when_nothing_found(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "tracker.save_locator.find_steam_userdata_roots",
        lambda: [],
    )
    monkeypatch.setenv("USERPROFILE", str(tmp_path / "empty"))
    with pytest.raises(SaveNotFoundError):
        locate_save_file()
