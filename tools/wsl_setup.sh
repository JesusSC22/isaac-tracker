#!/usr/bin/env bash
# One-shot setup for a fresh Ubuntu (WSL or native). Installs everything the
# AppImage build needs. Idempotent: safe to re-run.
#
# Usage:  bash tools/wsl_setup.sh

set -euo pipefail

echo "[wsl_setup] Updating apt index..."
sudo apt-get update -y

echo "[wsl_setup] Installing build + runtime packages..."
sudo apt-get install -y --no-install-recommends \
    python3 \
    python3-venv \
    python3-pip \
    wget \
    file \
    fuse \
    desktop-file-utils \
    libnss3 \
    libnspr4 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxss1 \
    libxshmfence1 \
    libxkbfile1 \
    libxcb-cursor0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-xinerama0 \
    libxcb-xkb1 \
    libasound2t64 \
    libdrm2 \
    libgbm1

echo "[wsl_setup] Done. You can now run: bash tools/build_appimage.sh"
