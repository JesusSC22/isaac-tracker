# PyInstaller spec for IsaacTracker (Linux build).
# Run inside WSL/Ubuntu (or any Linux):
#   pyinstaller build_linux.spec
# Output: dist/IsaacTracker  (ELF binary, used to assemble the AppImage later).

import shutil
from pathlib import Path

ROOT = Path.cwd()

# Mirror the root HTML into the bundled assets dir so we don't ship a stale copy.
src_html = ROOT / "challenges.html"
dst_html = ROOT / "tracker" / "assets" / "challenges.html"
if src_html.exists():
    shutil.copyfile(src_html, dst_html)
    print(f"[build_linux.spec] Synced challenges.html -> {dst_html}")

src_png = ROOT / "bossrush.png"
dst_png = ROOT / "tracker" / "assets" / "bossrush.png"
if src_png.exists():
    shutil.copyfile(src_png, dst_png)
    print(f"[build_linux.spec] Synced bossrush.png -> {dst_png}")

src_marks = ROOT / "marks"
dst_marks = ROOT / "tracker" / "assets" / "marks"
if src_marks.is_dir():
    if dst_marks.exists():
        shutil.rmtree(dst_marks)
    shutil.copytree(src_marks, dst_marks)
    print(f"[build_linux.spec] Synced marks/ -> {dst_marks}")

a = Analysis(
    ['tracker/app.py'],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        ('tracker/assets/challenges.html', 'assets'),
        ('tracker/assets/bossrush.png', 'assets'),
        ('tracker/assets/marks', 'assets/marks'),
        ('tracker/assets/ach_icons', 'assets/ach_icons'),
        ('tracker/assets/icons', 'assets/icons'),
        ('tracker/assets/item_icons', 'assets/item_icons'),
        ('tracker/assets/card_icons', 'assets/card_icons'),
        ('tracker/assets/pill_icons', 'assets/pill_icons'),
        ('tracker/assets/items_inline.js', 'assets'),
        ('tracker/assets/trinkets_inline.js', 'assets'),
        ('tracker/assets/cards_inline.js', 'assets'),
        ('tracker/assets/pills_inline.js', 'assets'),
    ],
    hiddenimports=[
        # Linux uses inotify rather than ReadDirectoryChangesW.
        'watchdog.observers.inotify',
        'watchdog.observers.inotify_buffer',
        # pywebview's Qt backend (bundled via PyQt5 + PyQtWebEngine).
        'qtpy',
        'qtpy.QtCore',
        'qtpy.QtWidgets',
        'qtpy.QtWebEngineWidgets',
        'qtpy.QtWebChannel',
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtWidgets',
        'PyQt5.QtWebEngineWidgets',
        'PyQt5.QtWebChannel',
        'webview.platforms.qt',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        'setuptools',
        'pkg_resources',
        '_distutils_hack',
        'pip',
        'wheel',
        'pytest',
        '_pytest',
        'unittest',
        'doctest',
        '_pyrepl',
        'pdb',
        'pydoc',
        'pydoc_data',
        'lib2to3',
        'turtle',
        'turtledemo',
        'tkinter',
        'xmlrpc',
        'smtplib',
        'ftplib',
        'telnetlib',
        'nntplib',
        'poplib',
        'imaplib',
        'PIL',
        'pillow',
    ],
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
    console=False,
)
