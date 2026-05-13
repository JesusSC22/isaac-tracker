"""
IsaacTracker desktop app -- PyWebView window that loads challenges.html and
pushes Isaac save state into the page on launch and on save-file changes.
"""
from __future__ import annotations

import atexit
import json
import logging
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

import webview

from tracker.exceptions import SaveNotFoundError, SaveParseError
from tracker.save_locator import find_steam_userdata_roots, locate_save_file
from tracker.save_parser import parse_save
from tracker.state_mapper import build_localstorage_state
from tracker.watcher import SaveWatcher

logger = logging.getLogger("tracker")


def _bundled_assets_dir() -> Path:
    """Return the directory containing bundled assets (HTML, images).

    When running under PyInstaller --onefile, files are extracted to
    sys._MEIPASS; otherwise we're running from source and assets are alongside
    this module.
    """
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "assets"
    return Path(__file__).parent / "assets"


def _load_html() -> str:
    return (_bundled_assets_dir() / "challenges.html").read_text(encoding="utf-8")


def _prepare_html_url() -> str:
    """Copy bundled assets to a writable temp dir and return a file:// URL.

    Loading via a real file:// URL (rather than passing `html=` to
    create_window, which loads under `about:blank`) is required so the page
    has a stable origin and can use localStorage. Without this, scripts that
    touch localStorage on init throw SecurityError and the rest of the page's
    script (including window.applyIsaacState) never gets defined.
    """
    src_dir = _bundled_assets_dir()
    tmp_dir = Path(tempfile.mkdtemp(prefix="isaactracker_"))
    # Copy every bundled asset (and asset subdir like marks/) so relative
    # refs like `bossrush.png` and `marks/mark_0.png` resolve from the HTML.
    for item in src_dir.iterdir():
        dest = tmp_dir / item.name
        if item.is_file():
            shutil.copy2(item, dest)
        elif item.is_dir():
            shutil.copytree(item, dest)
    atexit.register(lambda: shutil.rmtree(tmp_dir, ignore_errors=True))
    html_path = tmp_dir / "challenges.html"
    # Use Path.as_uri() for a proper file:// URL on Windows.
    return html_path.as_uri()


class TrackerApi:
    """JS-callable API exposed to the PyWebView window."""

    def __init__(self):
        self._window: webview.Window | None = None

    def attach(self, window: webview.Window) -> None:
        self._window = window

    def get_initial_state(self) -> dict[str, Any]:
        """Called by JS once `pywebviewready` fires. Returns the full state
        snapshot derived from the current save file."""
        try:
            path = locate_save_file()
            parsed = parse_save(path)
            state = build_localstorage_state(parsed)
            logger.info(
                "Loaded initial state from %s (challenges=%d, chars_unlocked=%d)",
                path,
                len(parsed.challenges_complete),
                len(parsed.characters_unlocked),
            )
            return state
        except (SaveNotFoundError, SaveParseError) as e:
            logger.warning("Initial state unavailable: %s", e)
            return {
                "challenges_state": {},
                "characters_state": {},
                "meta": {"error": str(e)},
            }


def _push_state(api: TrackerApi, window: webview.Window) -> None:
    """Called by the watcher whenever the save file changes."""
    state = api.get_initial_state()
    try:
        payload = json.dumps(state)
        window.evaluate_js(f"window.applyIsaacState({payload})")
        logger.info("Pushed updated state to UI")
    except Exception:
        logger.exception("Failed to push state to UI")


def _resolve_watch_dir() -> Path | None:
    """Pick a directory to watch for save changes. Returns None if we
    can't determine one (the app still works without live updates)."""
    try:
        save_path = locate_save_file()
        return save_path.parent
    except SaveNotFoundError:
        roots = find_steam_userdata_roots()
        return roots[0] if roots else None


def main() -> None:
    log_path = Path("IsaacTracker.log")
    logging.basicConfig(
        level=logging.INFO,
        filename=str(log_path),
        filemode="a",
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    logger.info("=" * 40)
    logger.info("IsaacTracker starting")

    api = TrackerApi()
    html_url = _prepare_html_url()
    logger.info("Loading UI from %s", html_url)
    window = webview.create_window(
        title="Isaac Tracker",
        url=html_url,
        width=900,
        height=950,
        resizable=True,
        js_api=api,
    )
    api.attach(window)

    watcher: SaveWatcher | None = None
    watch_dir = _resolve_watch_dir()
    if watch_dir is not None and watch_dir.is_dir():
        watcher = SaveWatcher(watch_dir, on_change=lambda: _push_state(api, window))
        watcher.start()
        logger.info("Watching %s for save changes", watch_dir)
    else:
        logger.warning("No save directory to watch; live updates disabled")

    try:
        webview.start()
    finally:
        if watcher is not None:
            watcher.stop()
        logger.info("IsaacTracker exiting cleanly")


if __name__ == "__main__":
    main()
