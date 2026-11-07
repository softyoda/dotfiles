#!/usr/bin/env bash
set -euo pipefail
source "$DOTFILES_LIB"
as_root bash "$MODULE_DIR/driver/install.sh" "$MODULE_DIR/driver/xone-0.5.8.1"
success "Pilote corrigé installé ; chargement au prochain redémarrage. Aucun reset des joueurs actifs."
