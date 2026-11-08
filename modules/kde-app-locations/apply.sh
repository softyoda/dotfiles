#!/usr/bin/env bash
set -euo pipefail
source "$DOTFILES_LIB"
"$HOME/.local/bin/kde-app-locations" sync
success "actions d’emplacement ajoutées aux raccourcis utilisateur"
