# PyInstaller spec for IsaacTracker.exe
# Build: `.\.venv\Scripts\pyinstaller.exe build.spec`

import shutil
from pathlib import Path

ROOT = Path.cwd()

# Mirror the root HTML into the bundled assets dir at build time so we don't
# ship a stale copy. (The runtime code reads from the bundled path.)
src_html = ROOT / "challenges.html"
dst_html = ROOT / "tracker" / "assets" / "challenges.html"
if src_html.exists():
    shutil.copyfile(src_html, dst_html)
    print(f"[build.spec] Synced challenges.html -> {dst_html}")

src_png = ROOT / "bossrush.png"
dst_png = ROOT / "tracker" / "assets" / "bossrush.png"
if src_png.exists():
    shutil.copyfile(src_png, dst_png)
    print(f"[build.spec] Synced bossrush.png -> {dst_png}")

a = Analysis(
    ['tracker/app.py'],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        ('tracker/assets/challenges.html', 'assets'),
        ('tracker/assets/bossrush.png', 'assets'),
    ],
    hiddenimports=[
        'watchdog.observers.read_directory_changes',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='IsaacTracker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=False,                # --windowed: no console window pops up
    icon=None,
)
