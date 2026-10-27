#!/usr/bin/env bash
# Raccourci global KDE « Démarrer / Mettre en pause la lecture du média » : F9 + touche Media Play.
set -euo pipefail
source "$DOTFILES_LIB"
kwriteconfig6 --file kglobalshortcutsrc --group mediacontrol --key playpausemedia \
    "$(printf 'F9\tMedia Play,Media Play,Démarrer / Mettre en pause la lecture du média')"
success "F9 → lecture/pause (effectif après reconnexion)"
