#!/usr/bin/env bash
# Build IsaacTracker.AppImage. Must run on Linux (WSL/Ubuntu works).
#
# Usage:  bash tools/build_appimage.sh
# Output: dist/IsaacTracker-x86_64.AppImage
#
# Assumes the host has the system packages from tools/wsl_setup.sh already
# installed (python3-venv, libwebkit2gtk, etc.). If running this for the
# first time on a fresh Ubuntu, run that script first.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

VENV_DIR=".venv-linux"
DIST_DIR="dist"
APPDIR="$DIST_DIR/IsaacTracker.AppDir"
APPIMAGE_TOOL="$REPO_ROOT/tools/appimagetool-x86_64.AppImage"

echo "[build_appimage] === Step 1/5: Python venv ==="
# We bundle PyQt5 + QtWebEngine via pip and disable system-site-packages.
# Reason: relying on system python3-gi only works when the host Python ABI
# matches the bundle's. SteamOS (3.x) ships a different Python than Ubuntu
# 26.04, so gi from the host could not be imported by our bundled Python.
# PyQt5 vendored via pip is ABI-tied to OUR Python interpreter, so it works
# anywhere — at the cost of ~100 MB extra bundle size.
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"
pip install --quiet --upgrade pip
pip install --quiet pyinstaller pywebview watchdog 'PyQt5>=5.15' 'PyQtWebEngine>=5.15' qtpy

echo "[build_appimage] === Step 2/5: PyInstaller ==="
rm -rf build dist/IsaacTracker dist/IsaacTracker.AppDir
pyinstaller --noconfirm build_linux.spec

if [ ! -f "$DIST_DIR/IsaacTracker" ]; then
    echo "[build_appimage] ERROR: PyInstaller did not produce dist/IsaacTracker" >&2
    exit 1
fi

echo "[build_appimage] === Step 3/5: AppDir layout ==="
mkdir -p "$APPDIR/usr/bin" "$APPDIR/usr/lib"
cp "$DIST_DIR/IsaacTracker" "$APPDIR/usr/bin/IsaacTracker"
cp tracker/assets/icons/godhead.png "$APPDIR/isaactracker.png"

# QtWebEngine (bundled by PyInstaller) needs NSS + NSPR at runtime. These are
# typically present on desktop Linux but missing on minimal/immutable systems
# (some SteamOS images, distrobox containers). Bundle them inside the AppImage
# so we don't depend on the host.
echo "[build_appimage] Bundling NSS + NSPR runtime libs"
NSS_LIBS=$(find /usr/lib -name "libnss3.so*" -o -name "libnssutil3.so*" \
           -o -name "libsmime3.so*" -o -name "libssl3.so*" \
           -o -name "libnspr4.so*" -o -name "libplc4.so*" \
           -o -name "libplds4.so*" 2>/dev/null)
for f in $NSS_LIBS; do
    cp -P "$f" "$APPDIR/usr/lib/" 2>/dev/null || true
done
# Also bundle the nss3 helper subdir if it exists (some apps need it).
if [ -d /usr/lib/x86_64-linux-gnu/nss ]; then
    mkdir -p "$APPDIR/usr/lib/nss"
    cp -r /usr/lib/x86_64-linux-gnu/nss/* "$APPDIR/usr/lib/nss/" 2>/dev/null || true
fi

cat > "$APPDIR/IsaacTracker.desktop" <<'EOF'
[Desktop Entry]
Type=Application
Name=Isaac Tracker
Comment=Tracker for The Binding of Isaac: Repentance+
Exec=IsaacTracker
Icon=isaactracker
Categories=Game;Utility;
Terminal=false
EOF

cat > "$APPDIR/AppRun" <<'EOF'
#!/bin/sh
HERE="$(dirname "$(readlink -f "$0")")"
# Make the bundled NSS/NSPR libs visible to QtWebEngine and disable Chromium's
# sandbox (Steam Deck's user namespaces are restricted; the sandbox would fail
# to initialise and the renderer process would die immediately).
export LD_LIBRARY_PATH="$HERE/usr/lib:${LD_LIBRARY_PATH:-}"
export QTWEBENGINE_DISABLE_SANDBOX=1
exec "$HERE/usr/bin/IsaacTracker" "$@"
EOF
chmod +x "$APPDIR/AppRun"

echo "[build_appimage] === Step 4/5: appimagetool ==="
if [ ! -f "$APPIMAGE_TOOL" ]; then
    echo "[build_appimage] Downloading appimagetool..."
    wget -q -O "$APPIMAGE_TOOL" \
        https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x "$APPIMAGE_TOOL"
fi

# Inside WSL/headless we need --appimage-extract-and-run; on a normal desktop
# it works directly. Try the direct invocation first, fall back if it fails.
OUT="$DIST_DIR/IsaacTracker-x86_64.AppImage"
rm -f "$OUT"
if ! ARCH=x86_64 "$APPIMAGE_TOOL" "$APPDIR" "$OUT" 2>/dev/null; then
    echo "[build_appimage] direct appimagetool failed, retrying with extract-and-run..."
    ARCH=x86_64 "$APPIMAGE_TOOL" --appimage-extract-and-run "$APPDIR" "$OUT"
fi

echo "[build_appimage] === Step 5/5: done ==="
ls -lh "$OUT"
echo ""
echo "[build_appimage] Final artifact: $OUT"
