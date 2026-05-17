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

# Mirror marks directory (13 hard-mode completion sprites) from root → assets.
src_marks = ROOT / "marks"
dst_marks = ROOT / "tracker" / "assets" / "marks"
if src_marks.is_dir():
    if dst_marks.exists():
        shutil.rmtree(dst_marks)
    shutil.copytree(src_marks, dst_marks)
    print(f"[build.spec] Synced marks/ -> {dst_marks}")

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
        ('tracker/assets/trinket_icons', 'assets/trinket_icons'),
        ('tracker/assets/items_inline.js', 'assets'),
        ('tracker/assets/trinkets_inline.js', 'assets'),
        ('tracker/assets/cards_inline.js', 'assets'),
        ('tracker/assets/bestiary_inline.js', 'assets'),
    ],
    hiddenimports=[
        'watchdog.observers.read_directory_changes',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        # Dev/build tooling pulled in transitively by PyInstaller hooks.
        'setuptools',
        'pkg_resources',
        '_distutils_hack',
        'pip',
        'wheel',
        # Test frameworks (only used during development).
        'pytest',
        '_pytest',
        'unittest',
        'doctest',
        # Stdlib pieces a windowed app never touches.
        '_pyrepl',
        'pdb',
        'pydoc',
        'pydoc_data',
        'lib2to3',
        'turtle',
        'turtledemo',
        'tkinter',
        # XML-RPC / SMTP / FTP — not used.
        'xmlrpc',
        'smtplib',
        'ftplib',
        'telnetlib',
        'nntplib',
        'poplib',
        'imaplib',
        # Image lib not used (pywebview renders HTML directly).
        'PIL',
        'pillow',
    ],
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
    icon=str(ROOT / "tracker" / "assets" / "icons" / "godhead.ico"),
)
