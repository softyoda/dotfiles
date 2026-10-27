#!/usr/bin/env bash
set -euo pipefail
source "$DOTFILES_LIB"
for theme in We10X-black We10X-black-dark; do
    directory="$HOME/.local/share/icons/$theme"
    if [[ -f "$directory/index.theme" ]] && command -v gtk-update-icon-cache >/dev/null; then
        gtk-update-icon-cache -f -t "$directory"
    fi
done
if command -v kbuildsycoca6 >/dev/null; then
    kbuildsycoca6 --noincremental
fi
if [[ -n ${DBUS_SESSION_BUS_ADDRESS:-} ]] && [[ -x /usr/lib/plasma-changeicons ]]; then
    /usr/lib/plasma-changeicons "$(kreadconfig6 --file kdeglobals --group Icons --key Theme)"
fi
success "Icône officielle Blender installée ; relancer Blender si nécessaire."
