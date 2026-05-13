import os
from pathlib import Path

from tracker.exceptions import SaveNotFoundError

_CANDIDATE_DIRNAMES = [
    "Binding of Isaac Repentance+",
    "Binding of Isaac Repentance",
]


def find_save_directory() -> Path:
    user_profile = os.environ.get("USERPROFILE")
    if not user_profile:
        raise SaveNotFoundError("USERPROFILE environment variable is not set")
    base = Path(user_profile) / "Documents" / "My Games"
    for name in _CANDIDATE_DIRNAMES:
        candidate = base / name
        if candidate.is_dir():
            return candidate
    raise SaveNotFoundError(f"No Isaac save directory found under {base}")


def locate_save_file() -> Path:
    save_dir = find_save_directory()
    dat_files = list(save_dir.glob("persistentgamedata*.dat"))
    if not dat_files:
        raise SaveNotFoundError(f"No persistentgamedata*.dat files in {save_dir}")
    return max(dat_files, key=lambda p: p.stat().st_mtime)
