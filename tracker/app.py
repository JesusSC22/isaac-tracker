"""
IsaacTracker desktop app -- PyWebView window that loads challenges.html and
pushes Isaac save state into the page on launch and on save-file changes.
"""
from __future__ import annotations

import atexit
import ctypes
import json
import logging
import os
import shutil
import sys
import tempfile
import textwrap
import threading
import time
from pathlib import Path
from typing import Any

import webview

from tracker import updater
from tracker._version import __version__
from tracker.exceptions import SaveNotFoundError, SaveParseError
from tracker.save_locator import find_steam_userdata_roots, locate_save_file
from tracker.save_parser import parse_save
from tracker.state_mapper import build_localstorage_state
from tracker.watcher import SaveWatcher

logger = logging.getLogger("tracker")


def _bundled_assets_dir() -> Path:
    """Return the directory containing bundled assets (HTML, images).

    Supports three runtime layouts: Nuitka onefile/standalone (assets live next
    to the executable, located via sys.argv[0]), PyInstaller --onefile (assets
    are extracted to sys._MEIPASS), and source mode (assets alongside this
    module).
    """
    if "__compiled__" in globals():
        return Path(__file__).resolve().parent / "assets"
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "assets"
    return Path(__file__).parent / "assets"


def _load_html() -> str:
    return (_bundled_assets_dir() / "challenges.html").read_text(encoding="utf-8")


_SPLASH_HTML = textwrap.dedent("""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        html, body {
            margin: 0; padding: 0; height: 100%;
            background: #0a0a0a;
            overflow: hidden; cursor: default;
            user-select: none;
        }
        body { display: flex; align-items: center; justify-content: center; }
        .splash {
            display: flex; flex-direction: column;
            align-items: center; gap: 18px;
            opacity: 0;
            animation: fadein 0.45s ease-out 0.05s forwards;
        }
        @keyframes fadein {
            0%   { opacity: 0; transform: scale(0.85); }
            100% { opacity: 1; transform: scale(1); }
        }
        .splash img {
            width: 200px; height: 200px;
            border-radius: 50%;
            object-fit: cover;
            image-rendering: -webkit-optimize-contrast;
            animation: pulse 1.6s ease-in-out infinite;
        }
        @keyframes pulse {
            0%, 100% { filter: drop-shadow(0 0 14px rgba(255, 220, 110, 0.45)); }
            50%      { filter: drop-shadow(0 0 30px rgba(255, 220, 110, 0.95)); }
        }
        .title {
            color: #ffd766;
            font-family: 'Trebuchet MS', sans-serif;
            font-size: 18px;
            font-weight: bold;
            letter-spacing: 6px;
            text-shadow: 0 0 10px rgba(255, 220, 110, 0.55);
        }
    </style>
    </head>
    <body>
        <div class="splash">
            <img src="icons/splash_logo.jpg" alt="">
            <div class="title">ISAAC TRACKER</div>
        </div>
    </body>
    </html>
""").strip()


def _prepare_asset_urls() -> tuple[str, str]:
    """Copy bundled assets to a writable temp dir and return (main_url, splash_url).

    Loading via a real file:// URL (rather than passing `html=` to
    create_window, which loads under `about:blank`) is required so the page
    has a stable origin and can use localStorage. Without this, scripts that
    touch localStorage on init throw SecurityError and the rest of the page's
    script (including window.applyIsaacState) never gets defined.

    The splash page also lives in this temp dir so its `<img src="icons/...">`
    resolves against the same bundled-asset tree.
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
    splash_path = tmp_dir / "splash.html"
    splash_path.write_text(_SPLASH_HTML, encoding="utf-8")
    atexit.register(lambda: shutil.rmtree(tmp_dir, ignore_errors=True))
    main_path = tmp_dir / "challenges.html"
    # Use Path.as_uri() for a proper file:// URL on Windows.
    return main_path.as_uri(), splash_path.as_uri()


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

    def get_app_version(self) -> str:
        return __version__

    def check_update(self) -> dict[str, Any] | None:
        """Synchronous check (5s network timeout). Returns the update payload
        or None. Never raises — any failure is swallowed and reported as None.
        """
        try:
            return updater.check_for_update()
        except Exception:
            logger.exception("check_update failed unexpectedly")
            return None

    def apply_update(self, asset_url: str, html_url: str = "", mode: str = "auto") -> dict[str, Any]:
        """Either download+stage swap (auto mode) or open the release page
        in the user's browser (manual mode). Pushes progress to JS via
        window._updateProgress(downloaded, total) during auto download."""
        if mode == "manual":
            ok = updater.open_release_page(html_url)
            return {"ok": ok, "fallback": "browser"}

        def _on_progress(downloaded: int, total: int | None) -> None:
            if not self._window:
                return
            try:
                t = "null" if total is None else str(int(total))
                self._window.evaluate_js(
                    f"window._updateProgress && window._updateProgress({int(downloaded)}, {t})"
                )
            except Exception:
                pass

        try:
            return updater.apply_update(asset_url, _on_progress)
        except Exception:
            logger.exception("apply_update failed unexpectedly")
            return {"ok": False, "error": "unexpected"}

    def shutdown_for_update(self) -> None:
        """JS calls this after seeing apply_update return ok+should_exit;
        we destroy the window AND force-exit so the swap script can proceed.

        window.destroy() alone is not enough: the watchdog SaveWatcher uses a
        non-daemon Observer thread, and pywebview/WebView2 keeps host objects
        alive, so Python lingers past the window close — and the swap .bat
        is polling for our PID to leave the process table. The Timer-driven
        os._exit gives pywebview ~0.6s to tear down cleanly, then nukes us.
        """
        if self._window:
            try:
                self._window.destroy()
            except Exception:
                logger.exception("window.destroy failed during shutdown_for_update")
        threading.Timer(0.6, lambda: os._exit(0)).start()


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


_GWL_EXSTYLE = -20
_WS_EX_LAYERED = 0x00080000
_LWA_ALPHA = 0x00000002


def _find_main_hwnd() -> int | None:
    if sys.platform != "win32":
        return None
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    user32.FindWindowW.restype = ctypes.c_void_p
    hwnd = user32.FindWindowW(None, "Isaac Tracker")
    return int(hwnd) if hwnd else None


def _make_window_layered(hwnd: int, alpha: int) -> None:
    """Mark the window as layered and apply an initial alpha (0-255)."""
    if sys.platform != "win32":
        return
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    user32.GetWindowLongW.argtypes = [ctypes.c_void_p, ctypes.c_int]
    user32.GetWindowLongW.restype = ctypes.c_long
    user32.SetWindowLongW.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_long]
    user32.SetWindowLongW.restype = ctypes.c_long
    user32.SetLayeredWindowAttributes.argtypes = [
        ctypes.c_void_p, ctypes.c_ulong, ctypes.c_ubyte, ctypes.c_ulong,
    ]
    user32.SetLayeredWindowAttributes.restype = ctypes.c_int
    ex_style = user32.GetWindowLongW(hwnd, _GWL_EXSTYLE)
    user32.SetWindowLongW(hwnd, _GWL_EXSTYLE, ex_style | _WS_EX_LAYERED)
    user32.SetLayeredWindowAttributes(hwnd, 0, alpha, _LWA_ALPHA)


def _set_window_alpha(hwnd: int, alpha: int) -> None:
    if sys.platform != "win32":
        return
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    user32.SetLayeredWindowAttributes.argtypes = [
        ctypes.c_void_p, ctypes.c_ulong, ctypes.c_ubyte, ctypes.c_ulong,
    ]
    user32.SetLayeredWindowAttributes(hwnd, 0, alpha, _LWA_ALPHA)


def _clear_layered_style(hwnd: int) -> None:
    """Remove WS_EX_LAYERED so the window goes back to normal rendering once
    the fade-in finishes (layered windows can interfere with WebView2 on
    some configurations)."""
    if sys.platform != "win32":
        return
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    user32.GetWindowLongW.argtypes = [ctypes.c_void_p, ctypes.c_int]
    user32.GetWindowLongW.restype = ctypes.c_long
    user32.SetWindowLongW.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_long]
    user32.SetWindowLongW.restype = ctypes.c_long
    ex_style = user32.GetWindowLongW(hwnd, _GWL_EXSTYLE)
    user32.SetWindowLongW(hwnd, _GWL_EXSTYLE, ex_style & ~_WS_EX_LAYERED)


def _fade_in_main_window(hwnd: int) -> None:
    """Animate the main window's alpha from 0 to 255 over ~450 ms."""
    if sys.platform != "win32" or not hwnd:
        return
    steps = 18
    duration = 0.45
    for i in range(1, steps + 1):
        alpha = int(255 * (i / steps))
        _set_window_alpha(hwnd, alpha)
        time.sleep(duration / steps)
    _clear_layered_style(hwnd)


def _apply_window_icon() -> None:
    """Set the title-bar icon via Win32 (pywebview's create_window has no
    `icon=` parameter, and pywebview's WinForms host does not auto-inherit
    the .exe's icon resource for the window decoration)."""
    if sys.platform != "win32":
        return
    icon_path = _bundled_assets_dir() / "icons" / "godhead.ico"
    if not icon_path.exists():
        return
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    user32.FindWindowW.restype = ctypes.c_void_p
    user32.LoadImageW.restype = ctypes.c_void_p
    user32.SendMessageW.argtypes = [
        ctypes.c_void_p, ctypes.c_uint, ctypes.c_void_p, ctypes.c_void_p,
    ]
    IMAGE_ICON = 1
    LR_LOADFROMFILE = 0x00000010
    WM_SETICON = 0x0080
    ICON_SMALL, ICON_BIG = 0, 1
    hwnd = user32.FindWindowW(None, "Isaac Tracker")
    if not hwnd:
        return
    path_str = str(icon_path)
    h_small = user32.LoadImageW(None, path_str, IMAGE_ICON, 16, 16, LR_LOADFROMFILE)
    h_big = user32.LoadImageW(None, path_str, IMAGE_ICON, 32, 32, LR_LOADFROMFILE)
    if h_small:
        user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, h_small)
    if h_big:
        user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, h_big)


def main() -> None:
    # No log file is created. The logger.* calls below remain no-ops; set
    # the env var ISAAC_TRACKER_LOG=1 (from source) to re-enable INFO logs.
    import os
    if os.environ.get("ISAAC_TRACKER_LOG"):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        )
    else:
        logging.disable(logging.CRITICAL)
    logger.info("IsaacTracker starting")

    # If we were launched by an in-progress update (we are running as
    # IsaacTracker.new.exe and the previous PID was passed in argv), kick off
    # the swap in the background while the GUI loads. The user sees a normal
    # cold start; behind the scenes the old .exe is removed and we rename
    # ourselves to IsaacTracker.exe so the next launch is unsurprising.
    old_pid = updater.parse_finalize_pid(sys.argv)
    if old_pid is not None:
        updater.finalize_pending_update_async(old_pid)
    elif updater.maybe_recover_pending_swap():
        # Auto-recovery: hemos detectado un IsaacTracker.new.exe adyacente
        # huérfano de un update previo que falló el rename. Acabamos de
        # lanzarlo con --finalize-update apuntando a nosotros; debemos
        # salir para que el nuevo proceso pueda completar el swap.
        sys.exit(0)

    api = TrackerApi()
    main_url, splash_url = _prepare_asset_urls()
    logger.info("Loading UI from %s", main_url)

    splash = webview.create_window(
        title="IsaacTrackerSplash",
        url=splash_url,
        width=380,
        height=380,
        frameless=True,
        easy_drag=False,
        on_top=True,
        resizable=False,
        background_color="#0a0a0a",
    )

    # Main window arrives visible so PyWebView/WebView2 actually loads its
    # URL (a hidden window never navigates, producing a blank page). We hide
    # it from the user by making it layered + alpha=0 the moment its HWND
    # exists, then ramp the alpha up to 255 once the splash closes.
    window = webview.create_window(
        title="Isaac Tracker",
        url=main_url,
        width=900,
        height=950,
        resizable=True,
        js_api=api,
    )
    api.attach(window)

    def _hide_main_immediately() -> None:
        # Called as soon as the main window's HWND exists. We set alpha=0
        # before WebView2 paints anything, so the user sees only the splash.
        hwnd = _find_main_hwnd()
        if hwnd:
            _make_window_layered(hwnd, 0)

    window.events.before_show += _hide_main_immediately

    watcher: SaveWatcher | None = None
    watch_dir = _resolve_watch_dir()
    if watch_dir is not None and watch_dir.is_dir():
        watcher = SaveWatcher(watch_dir, on_change=lambda: _push_state(api, window))
        watcher.start()
        logger.info("Watching %s for save changes", watch_dir)
    else:
        logger.warning("No save directory to watch; live updates disabled")

    def _splash_to_main() -> None:
        # Splash visible duration. The CSS fade-in inside the splash takes
        # ~0.5s, so we hold the splash a bit longer than that before swapping.
        time.sleep(1.2)
        try:
            splash.destroy()
        except Exception:
            logger.exception("Failed to close splash window")
        if sys.platform == "win32":
            hwnd = _find_main_hwnd()
            if hwnd:
                _fade_in_main_window(hwnd)
        _apply_window_icon()

    def _on_started() -> None:
        threading.Thread(target=_splash_to_main, daemon=True).start()

    try:
        # On Linux we ship PyQt5+QtWebEngine in the AppImage, so force Qt.
        # On Windows pywebview uses EdgeHTML/WebView2 regardless of gui hint;
        # passing None lets it pick the native default.
        gui_hint = "qt" if sys.platform != "win32" else None
        webview.start(func=_on_started, gui=gui_hint)
    finally:
        if watcher is not None:
            watcher.stop()
        logger.info("IsaacTracker exiting cleanly")


if __name__ == "__main__":
    main()
