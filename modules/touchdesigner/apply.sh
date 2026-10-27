#!/usr/bin/env bash
# Base de données MIME + associations .toe/.tox. Le préfixe Wine et le runner
# sont à reconstruire à la main : voir README.md.
set -euo pipefail
source "$DOTFILES_LIB"

share="${XDG_DATA_HOME:-$HOME/.local/share}"
update-mime-database "$share/mime" 2>/dev/null || warn "update-mime-database indisponible"
update-desktop-database "$share/applications" 2>/dev/null || true
gtk-update-icon-cache -q -t "$share/icons/hicolor" 2>/dev/null || true
for mime in application/x-touchdesigner-toe application/x-touchdesigner-tox; do
    xdg-mime default touchdesigner-file.desktop "$mime"
done

base="$share/touchdesigner-linux"
if [[ ! -x "$base/runner/bin/wine64" || ! -d "$base/prefix/drive_c" ]]; then
    warn "runner Wine ou préfixe TouchDesigner absent : suivre le README du module (étapes manuelles)"
fi
success "associations .toe / .tox à jour"
