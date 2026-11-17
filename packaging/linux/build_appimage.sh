#!/usr/bin/env bash
# Builds Shadowra's Story as an AppImage for Linux (x86_64).
#
#   Run on Linux (or WSL/Ubuntu) from anywhere:   bash packaging/linux/build_appimage.sh
#   Result:                                         dist/ShadowraS.aplha1-x86_64.AppImage
#
# Needs: python3 (3.10+) with venv, curl or wget. Everything else (pygame, PyInstaller,
# appimagetool) is fetched into packaging/linux/.build – nothing is installed system-wide.
# For the widest compatibility build on an older distro (e.g. Ubuntu 22.04): an AppImage runs on
# systems with the same or a newer glibc than the one it was built on.
set -euo pipefail

NAME="ShadowraS"
VERSION="aplha1"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
BUILD="$HERE/.build"
APPDIR="$BUILD/AppDir"
OUT="$ROOT/dist/${NAME}.${VERSION}-x86_64.AppImage"

echo "==> Project: $ROOT"
rm -rf "$APPDIR" "$BUILD/pyi"
mkdir -p "$BUILD" "$ROOT/dist"

# ---- 1. Python environment with pygame + PyInstaller -------------------------------------
if [ ! -x "$BUILD/venv/bin/python" ]; then
    echo "==> Creating build venv"
    python3 -m venv "$BUILD/venv"
fi
PY="$BUILD/venv/bin/python"
"$PY" -m pip install --quiet --upgrade pip
"$PY" -m pip install --quiet -r "$ROOT/requirements.txt" pyinstaller

# ---- 2. Freeze the game (one folder; the AppImage itself is the single file) --------------
echo "==> PyInstaller"
DATA_ARGS=(--add-data "$ROOT/assets:assets" --add-data "$ROOT/data:data"
           --add-data "$ROOT/src/controls/xheats.json:src/controls")
while IFS= read -r f; do
    rel="$(dirname "${f#$ROOT/}")"
    DATA_ARGS+=(--add-data "$f:$rel")
done < <(find "$ROOT/src/world" -name abilities.json)
( cd "$ROOT" && "$PY" -m PyInstaller --noconfirm --clean --onedir --windowed --name "$NAME" \
      --distpath "$BUILD/pyi/dist" --workpath "$BUILD/pyi/work" --specpath "$BUILD/pyi" \
      "${DATA_ARGS[@]}" main.py )

# ---- 3. AppDir ---------------------------------------------------------------------------------
echo "==> AppDir"
mkdir -p "$APPDIR/usr/bin" "$APPDIR/usr/share/applications" "$APPDIR/usr/share/icons/hicolor/256x256/apps"
cp -r "$BUILD/pyi/dist/$NAME" "$APPDIR/usr/bin/$NAME"
install -m 755 "$HERE/AppRun" "$APPDIR/AppRun"
cp "$HERE/shadowras-story.desktop" "$APPDIR/shadowras-story.desktop"
cp "$HERE/shadowras-story.desktop" "$APPDIR/usr/share/applications/"
# 256x256 icon from the game logo
"$PY" - "$ROOT/assets/images/logo/Logo.png" "$APPDIR/shadowras-story.png" <<'EOF'
import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
pygame.init()
pygame.display.set_mode((1, 1))
img = pygame.image.load(sys.argv[1]).convert_alpha()
pygame.image.save(pygame.transform.smoothscale(img, (256, 256)), sys.argv[2])
EOF
cp "$APPDIR/shadowras-story.png" "$APPDIR/usr/share/icons/hicolor/256x256/apps/"
ln -sf shadowras-story.png "$APPDIR/.DirIcon"

# ---- 4. appimagetool ------------------------------------------------------------------------
TOOL="$BUILD/appimagetool-x86_64.AppImage"
if [ ! -x "$TOOL" ]; then
    echo "==> Downloading appimagetool"
    URL="https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage"
    if command -v curl >/dev/null; then curl -fL -o "$TOOL" "$URL"; else wget -O "$TOOL" "$URL"; fi
    chmod +x "$TOOL"
fi

echo "==> Packing $OUT"
# --appimage-extract-and-run: works even where FUSE is missing (containers, WSL)
ARCH=x86_64 "$TOOL" --appimage-extract-and-run "$APPDIR" "$OUT"
chmod +x "$OUT"
echo "==> Done: $OUT"
