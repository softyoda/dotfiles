#!/usr/bin/env bash
# Clé par clé (F9, bouton power et Alt+F9 HDMI sont gérés par d'autres modules).
set -euo pipefail
source "$DOTFILES_LIB"
k() { kwriteconfig6 --file kglobalshortcutsrc --group "$1" --key "$2" "$3"; }
k kwin Cube "Meta+C,none,Basculer ou non vers le cube"
k plasmashell "next activity" "Meta+A,none,Parcourir les activités"
k plasmashell "previous activity" "Meta+Shift+A,none,Parcourir les activités (à l'envers)"
kwriteconfig6 --file kglobalshortcutsrc --group services --group org.kde.konsole.desktop --key _launch none
success "raccourcis KDE appliqués (effectifs après reconnexion)"
