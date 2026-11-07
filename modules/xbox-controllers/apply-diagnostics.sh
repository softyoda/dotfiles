#!/usr/bin/env bash
set -euo pipefail
source "$DOTFILES_LIB"
mkdir -p "$HOME/.local/bin"
ln -sfn "$HOME/.local/share/diagnostic-manettes/diagnostic-manettes.py" "$HOME/.local/bin/diagnostic-manettes"
enable_user diagnostic-manettes.service
systemctl --user restart diagnostic-manettes.service
