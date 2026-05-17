from __future__ import annotations

import os
import sys
import re
from pathlib import Path
from typing import Iterator

from tracker.exceptions import SaveNotFoundError

_FALLBACK_STEAM_PATHS_WINDOWS: list[Path] = [
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


def _find_steam_userdata_roots_windows() -> list[Path]:
    candidates: list[Path] = []
    explicit = _read_steam_path_from_registry()
    if explicit:
        candidates.append(Path(explicit) / "userdata")
    for fallback in _FALLBACK_STEAM_PATHS_WINDOWS:
        candidates.append(fallback / "userdata")
    return candidates


def _find_steam_userdata_roots_linux() -> list[Path]:
    home = Path.home()
    return [
        # Native Steam install (also the Steam Deck default).
        home / ".local" / "share" / "Steam" / "userdata",
        # Legacy symlink path; same data on most distros.
        home / ".steam" / "steam" / "userdata",
        # Flatpak Steam.
        home / ".var" / "app" / "com.valvesoftware.Steam"
             / ".local" / "share" / "Steam" / "userdata",
        # Snap Steam (less common, included for completeness).
        home / "snap" / "steam" / "common" / ".local" / "share" / "Steam" / "userdata",
    ]


def find_steam_userdata_roots() -> list[Path]:
    if sys.platform == "win32":
        candidates = _find_steam_userdata_roots_windows()
    else:
        candidates = _find_steam_userdata_roots_linux()
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


def _find_local_backups_dirs_windows() -> list[Path]:
    user_profile = os.environ.get("USERPROFILE")
    if not user_profile:
        return []
    return [
        Path(user_profile)
        / "Documents" / "My Games"
        / "Binding of Isaac Repentance+" / "save_backups"
    ]


def _find_local_backups_dirs_linux() -> list[Path]:
    """Repentance+ runs through Proton on Linux. The game writes its 'Documents'
    folder inside the Proton prefix, so save_backups end up there too. We cover
    both the native-Steam prefix and the Flatpak prefix."""
    home = Path.home()
    proton_pfx_doc = (
        "drive_c/users/steamuser/Documents/"
        "Binding of Isaac Repentance+/save_backups"
    )
    # Some Proton versions use "My Documents" instead of "Documents".
    proton_pfx_mydoc = (
        "drive_c/users/steamuser/My Documents/"
        "Binding of Isaac Repentance+/save_backups"
    )
    bases = [
        home / ".local" / "share" / "Steam" / "steamapps" / "compatdata" / "250900" / "pfx",
        home / ".steam" / "steam" / "steamapps" / "compatdata" / "250900" / "pfx",
        home / ".var" / "app" / "com.valvesoftware.Steam"
             / ".local" / "share" / "Steam" / "steamapps" / "compatdata" / "250900" / "pfx",
    ]
    out: list[Path] = []
    for base in bases:
        out.append(base / proton_pfx_doc)
        out.append(base / proton_pfx_mydoc)
    return out


def _find_local_backups_dirs() -> list[Path]:
    if sys.platform == "win32":
        return [p for p in _find_local_backups_dirs_windows() if p.is_dir()]
    return [p for p in _find_local_backups_dirs_linux() if p.is_dir()]


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
    for backups in _find_local_backups_dirs():
        for f in backups.iterdir():
            if f.is_file() and _REP_PLUS_NAME_RE.match(f.name):
                yield f


def locate_save_file() -> Path:
    candidates = list(iter_repentance_plus_saves())
    if not candidates:
        raise SaveNotFoundError(
            "No se encontró ninguna partida de Isaac Repentance+ en Steam ni en las copias de seguridad locales."
        )
    return max(candidates, key=lambda p: p.stat().st_mtime)
