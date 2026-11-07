#!/usr/bin/env bash
set -euo pipefail
systemctl --user is-enabled -q diagnostic-manettes.service
systemctl --user is-active -q diagnostic-manettes.service
[[ -L "$HOME/.local/bin/diagnostic-manettes" ]]
[[ $(readlink -f "$HOME/.local/bin/diagnostic-manettes") == "$HOME/.local/share/diagnostic-manettes/diagnostic-manettes.py" ]]
