#!/usr/bin/env bash
set -euo pipefail
systemctl --user is-enabled --quiet kde-app-locations.path
systemctl --user is-active --quiet kde-app-locations.path
! systemctl --user is-active --quiet kde-app-locations.timer
"$HOME/.local/bin/kde-app-locations" watch-check >/dev/null
