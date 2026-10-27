#!/usr/bin/env bash
# Télécharge l'AppImage V0.3.2 (somme SHA-256 vérifiée) et en extrait l'icône.
set -euo pipefail
source "$DOTFILES_LIB"

VERSION=0.3.2
URL="https://github.com/dennisklappe/OrcaSlicer-WaveOverhangs/releases/download/v$VERSION/OrcaSlicerWaveOverhangs_Linux_AppImage_Ubuntu2404_V$VERSION.AppImage"
SHA256=db449e2576324de7800e0f9189945be89a7f8d746da7621923d574e7b83d5cbc
APP="$HOME/Applications/OrcaSlicerWaveOverhangs.AppImage"

mkdir -p "$HOME/Applications"
if [[ -f "$APP" ]] && echo "$SHA256  $APP" | sha256sum -c --quiet - 2>/dev/null; then
    info "AppImage $VERSION déjà présente"
else
    # Ancien nom (AppImageLauncher) : réutiliser le fichier s'il a la bonne somme
    old=$(ls "$HOME"/Applications/OrcaSlicerWaveOverhangs_*V$VERSION*.AppImage 2>/dev/null | head -1 || true)
    if [[ -n "$old" ]] && echo "$SHA256  $old" | sha256sum -c --quiet - 2>/dev/null; then
        ln -sf "$old" "$APP"
    else
        info "téléchargement de OrcaSlicerWaveOverhangs $VERSION (≈ 150 Mo)"
        curl -fL --progress-bar -o "$APP.part" "$URL"
        echo "$SHA256  $APP.part" | sha256sum -c --quiet - || { rm -f "$APP.part"; error "somme de contrôle incorrecte"; exit 1; }
        mv "$APP.part" "$APP"
    fi
    chmod +x "$APP"
fi

icon="${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor/256x256/apps/orcaslicer-waveoverhangs.png"
if [[ ! -f "$icon" ]]; then
    tmp=$(mktemp -d)
    ( cd "$tmp" && "$(readlink -f "$APP")" --appimage-extract '*.png' >/dev/null 2>&1 || true )
    png=$(find "$tmp/squashfs-root" -maxdepth 1 \( -name '*.png' -o -name '.DirIcon' \) 2>/dev/null | head -1)
    if [[ -n "$png" ]]; then mkdir -p "$(dirname "$icon")"; cp -L "$png" "$icon"; fi
    rm -rf -- "$tmp"
fi
update-desktop-database "${XDG_DATA_HOME:-$HOME/.local/share}/applications" 2>/dev/null || true
success "OrcaSlicer WaveOverhangs $VERSION prêt"
