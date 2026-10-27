#!/usr/bin/env bash
set -euo pipefail
source "$DOTFILES_LIB"
ensure_groups input
libinput-gestures-setup autostart
in_session && libinput-gestures-setup restart >/dev/null 2>&1 || true
success "gestes activés (reconnexion requise si le groupe input vient d'être ajouté)"
