#!/usr/bin/env bash
set -euo pipefail
source "$DOTFILES_LIB"
systemctl --user disable --now kde-app-locations.timer 2>/dev/null || true
"$HOME/.local/bin/kde-app-locations" watch
enable_user kde-app-locations.path
