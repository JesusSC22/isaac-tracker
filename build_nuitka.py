"""Build IsaacTracker.exe using Nuitka.

Produces a smaller executable than PyInstaller (~30-50% reduction) and
avoids the antivirus false positives caused by the PyInstaller bootloader.

Usage: `python build_nuitka.py` (from the project venv)

Requires Visual Studio Build Tools 2022 with the C++ workload installed.
Nuitka detects MSVC via vswhere automatically.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
ASSETS = ROOT / "tracker" / "assets"


def _sync_root_assets() -> None:
    """Mirror root-level HTML/PNG/marks into tracker/assets so the bundle is fresh."""
    file_pairs = [
        (ROOT / "challenges.html", ASSETS / "challenges.html"),
        (ROOT / "bossrush.png", ASSETS / "bossrush.png"),
    ]
    for src, dst in file_pairs:
        if src.exists():
            shutil.copyfile(src, dst)
            print(f"[build] synced {src.name}")

    src_marks = ROOT / "marks"
    dst_marks = ASSETS / "marks"
    if src_marks.is_dir():
        if dst_marks.exists():
            shutil.rmtree(dst_marks)
        shutil.copytree(src_marks, dst_marks)
        print("[build] synced marks/")


def _build() -> int:
    icon = ASSETS / "icons" / "godhead.ico"
    # Modules we never use at runtime — same list as the old PyInstaller spec.
    nofollow = [
        "setuptools", "pkg_resources", "_distutils_hack", "pip", "wheel",
        "pytest", "_pytest", "unittest", "doctest",
        "pdb", "pydoc", "pydoc_data", "lib2to3", "turtle", "turtledemo",
        "tkinter", "_tkinter",
        "xmlrpc", "smtplib", "ftplib", "telnetlib", "nntplib", "poplib", "imaplib",
        "PIL", "pillow",
        "email.mime", "html.parser",
    ]
    args = [
        sys.executable, "-m", "nuitka",
        "--standalone",
        "--onefile",
        "--windows-console-mode=disable",
        "--msvc=latest",
        "--assume-yes-for-downloads",
        "--lto=yes",
        "--python-flag=no_docstrings,no_asserts",
        f"--include-data-dir={ASSETS.as_posix()}=assets",
        f"--windows-icon-from-ico={icon.as_posix()}",
        "--output-dir=dist",
        "--output-filename=IsaacTracker.exe",
        "--remove-output",
        *[f"--nofollow-import-to={m}" for m in nofollow],
        "tracker/app.py",
    ]
    print("[build] launching nuitka (this may take several minutes)...")
    start = time.monotonic()
    proc = subprocess.run(args, cwd=ROOT)
    elapsed = time.monotonic() - start
    print(f"[build] nuitka exit={proc.returncode}, elapsed={elapsed:.1f}s")
    return proc.returncode


def main() -> int:
    _sync_root_assets()
    rc = _build()
    if rc == 0:
        exe = ROOT / "dist" / "IsaacTracker.exe"
        if exe.exists():
            size_mb = exe.stat().st_size / (1024 * 1024)
            print(f"[build] {exe} -> {size_mb:.2f} MB")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
