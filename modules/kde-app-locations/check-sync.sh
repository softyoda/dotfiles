#!/usr/bin/env bash
set -euo pipefail
systemctl --user is-enabled --quiet kde-app-locations.timer
systemctl --user is-active --quiet kde-app-locations.timer
