from __future__ import annotations

import re
import threading
from pathlib import Path
from typing import Callable

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

# Match any persistentgamedata-style save filename Isaac uses across DLCs.
# Examples that should match:
#   persistentgamedata1.dat
#   rep+persistentgamedata2.dat
#   20260513.rep+persistentgamedata1.dat
#   abp_persistentgamedata1.dat
# We accept all variants here; the locator filters by DLC prefix when picking
# the active file. The watcher just needs to know "something save-shaped changed".
_SAVE_NAME_RE = re.compile(r"persistentgamedata\d*\.dat$", re.IGNORECASE)


class SaveWatcher:
    """Watches a directory and calls `on_change` after debounced save-file modifications."""

    def __init__(
        self,
        save_dir: Path,
        on_change: Callable[[], None],
        debounce_ms: int = 500,
    ):
        self._save_dir = Path(save_dir)
        self._on_change = on_change
        self._debounce_s = debounce_ms / 1000.0
        self._observer: Observer | None = None
        self._timer: threading.Timer | None = None
        self._lock = threading.Lock()

    def start(self) -> None:
        handler = _Handler(self._schedule_fire)
        self._observer = Observer()
        self._observer.schedule(handler, str(self._save_dir), recursive=False)
        self._observer.start()

    def stop(self) -> None:
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None
        if self._observer is not None:
            self._observer.stop()
            self._observer.join(timeout=2)
            self._observer = None

    def _schedule_fire(self) -> None:
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
            self._timer = threading.Timer(self._debounce_s, self._fire)
            self._timer.daemon = True
            self._timer.start()

    def _fire(self) -> None:
        with self._lock:
            self._timer = None
        try:
            self._on_change()
        except Exception:
            # Swallow callback errors so the watcher thread keeps running.
            # The orchestrator handles error reporting.
            pass


class _Handler(FileSystemEventHandler):
    def __init__(self, fire: Callable[[], None]):
        self._fire = fire

    def on_modified(self, event: FileSystemEvent) -> None:
        if self._is_save_file(event):
            self._fire()

    def on_created(self, event: FileSystemEvent) -> None:
        if self._is_save_file(event):
            self._fire()

    @staticmethod
    def _is_save_file(event: FileSystemEvent) -> bool:
        if event.is_directory:
            return False
        return bool(_SAVE_NAME_RE.search(Path(event.src_path).name))
