#!/usr/bin/env bash
set -euo pipefail
source "$DOTFILES_LIB"
update-desktop-database "${XDG_DATA_HOME:-$HOME/.local/share}/applications" 2>/dev/null || true
xdg-mime default flatpakref-handler.desktop application/vnd.flatpak.ref
success "fichiers .flatpakref associés à flatpakref-install"
