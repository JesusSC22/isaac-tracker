from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Iterator

from tracker.exceptions import SaveNotFoundError

_FALLBACK_STEAM_PATHS: list[Path] = [
    Path(r"C:\Program Files (x86)\Steam"),
    Path(r"C:\Program Files\Steam"),
]

_REP_PLUS_NAME_RE = re.compile(
    r"^(?:\d{8}\.)?rep\+persistentgamedata\d+\.dat$",
    re.IGNORECASE,
)


def _read_steam_path_from_registry() -> str | None:
    try:
        import winreg
    except ImportError:
        return None
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as k:
            value, _ = winreg.QueryValueEx(k, "SteamPath")
            return value or None
    except (FileNotFoundError, OSError):
        return None


def find_steam_userdata_roots() -> list[Path]:
    candidates: list[Path] = []
    explicit = _read_steam_path_from_registry()
    if explicit:
        candidates.append(Path(explicit) / "userdata")
    for fallback in _FALLBACK_STEAM_PATHS:
        candidates.append(fallback / "userdata")
    seen: set[Path] = set()
    out: list[Path] = []
    for c in candidates:
        try:
            resolved = c.resolve(strict=False)
        except OSError:
            resolved = c
        if resolved in seen or not resolved.is_dir():
            continue
        seen.add(resolved)
        out.append(c if c.is_dir() else resolved)
    return out


def _find_local_backups_dir() -> Path | None:
    user_profile = os.environ.get("USERPROFILE")
    if not user_profile:
        return None
    backups = (
        Path(user_profile)
        / "Documents" / "My Games"
        / "Binding of Isaac Repentance+" / "save_backups"
    )
    return backups if backups.is_dir() else None


def iter_repentance_plus_saves() -> Iterator[Path]:
    for udata in find_steam_userdata_roots():
        for steamid_dir in udata.iterdir():
            if not steamid_dir.is_dir():
                continue
            remote = steamid_dir / "250900" / "remote"
            if not remote.is_dir():
                continue
            for f in remote.iterdir():
                if f.is_file() and _REP_PLUS_NAME_RE.match(f.name):
                    yield f
    backups = _find_local_backups_dir()
    if backups is not None:
        for f in backups.iterdir():
            if f.is_file() and _REP_PLUS_NAME_RE.match(f.name):
                yield f


def locate_save_file() -> Path:
    candidates = list(iter_repentance_plus_saves())
    if not candidates:
        raise SaveNotFoundError(
            "No rep+persistentgamedata*.dat files found in Steam userdata or local backups"
        )
    return max(candidates, key=lambda p: p.stat().st_mtime)
