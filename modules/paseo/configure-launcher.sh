#!/usr/bin/env bash
set -euo pipefail
source "$DOTFILES_LIB"
has update-desktop-database && update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
has kbuildsycoca6 && kbuildsycoca6 >/dev/null 2>&1 || true
case ":$PATH:" in *":$HOME/.local/bin:"*) ;; *) warn "~/.local/bin n’est pas dans le PATH : le wrapper paseo ne sera pas prioritaire en terminal" ;; esac
success "Paseo prêt : lancer « Paseo » depuis le menu (le lanceur passe par le wrapper)"
