"""Auto-update system: check GitHub for newer releases, download, swap.

All failures (network, parse, missing assets, permission denied) are caught
and surfaced as a None return / mode="manual" hint rather than raised — the
update path must never crash the app or surface an error to the user.
"""
from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import sys
import threading
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path
from typing import Any, Callable

from tracker._version import __version__

logger = logging.getLogger("tracker.updater")

GITHUB_REPO = "JesusSC22/isaac-tracker"
EXE_NAME = "IsaacTracker.exe"
NEW_EXE_NAME = "IsaacTracker.new.exe"
SWAP_SCRIPT_NAME = "_update.bat"
USER_AGENT = f"IsaacTracker/{__version__}"
NETWORK_TIMEOUT = 5.0
DOWNLOAD_TIMEOUT = 60.0

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


_SWAP_SCRIPT = """@echo off
set WAITED=0
set RETRIES=15
:wait
timeout /t 1 /nobreak >nul
tasklist /FI "IMAGENAME eq {exe_name}" 2>nul | find /I "{exe_name}" >nul
if %ERRORLEVEL% NEQ 0 goto swap
set /a WAITED+=1
if %WAITED% GEQ 12 (
    taskkill /F /IM "{exe_name}" >nul 2>&1
    timeout /t 2 /nobreak >nul
    goto swap
)
goto wait
:swap
move /Y "%~dp0{new_exe_name}" "%~dp0{exe_name}" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    set /a RETRIES-=1
    if %RETRIES% GTR 0 (
        timeout /t 1 /nobreak >nul
        goto swap
    )
    exit /b 1
)
rem Give Windows a moment to fully release the freshly-renamed .exe.
rem Without this, PyInstaller's bootloader sometimes fails with "Failed to
rem load Python DLL" because the file isn't yet visible to LoadLibrary.
timeout /t 2 /nobreak >nul
start "" "%~dp0{exe_name}"
(goto) 2>nul & del "%~f0"
"""


def _write_swap_script(exe_dir: Path) -> Path:
    script_path = exe_dir / SWAP_SCRIPT_NAME
    script_path.write_text(
        _SWAP_SCRIPT.format(exe_name=EXE_NAME, new_exe_name=NEW_EXE_NAME),
        encoding="ascii",
    )
    return script_path


def _launch_detached(script_path: Path) -> None:
    """Launch the swap script detached so it survives our process exit.
    CREATE_NO_WINDOW hides the cmd console; we don't pair it with
    DETACHED_PROCESS because the two flags are mutually exclusive per MSDN
    and combining them shows the console window anyway."""
    flags = 0
    if sys.platform == "win32":
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000) | \
                getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200)
    subprocess.Popen(
        ["cmd", "/c", str(script_path)],
        creationflags=flags,
        close_fds=True,
        cwd=str(script_path.parent),
    )


def apply_update(asset_url: str, on_progress: Callable[[int, int | None], None]) -> dict[str, Any]:
    """Download new exe, stage swap script, launch it detached.

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
    try:
        script = _write_swap_script(exe_dir)
        _launch_detached(script)
    except OSError as e:
        logger.warning("Could not stage swap script: %s", e)
        return {"ok": False, "error": "swap-script-failed"}
    return {"ok": True, "should_exit": True}


def open_release_page(html_url: str) -> bool:
    """Fallback for manual mode: open the release page in the default browser."""
    if not html_url:
        return False
    try:
        return bool(webbrowser.open(html_url))
    except Exception:
        return False
