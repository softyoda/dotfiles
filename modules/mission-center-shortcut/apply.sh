#!/usr/bin/env bash
set -euo pipefail
source "$DOTFILES_LIB"
kwriteconfig6 --file kwinrc --group Plugins --key launch-mission-centerEnabled true
systemctl --user daemon-reload
in_session && qdbus6 org.kde.KWin /KWin reconfigure >/dev/null 2>&1 || true
success "Ctrl+Maj+Échap → Mission Center (le service est lancé à la demande, pas activé)"
