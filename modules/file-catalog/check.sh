#!/usr/bin/env bash
set -e
[[ -x "$HOME/.local/bin/siftbay" && -s "$HOME/.config/file-catalog/local-launcher.key" ]]
source_dir="$HOME/.local/share/file-catalog/source"
[[ $(git -C "$source_dir" rev-parse HEAD) = $(cat "$MODULE_DIR/revision") ]]
[[ -z $(git -C "$source_dir" status --porcelain) ]]
python3 -m json.tool "$HOME/.config/file-catalog/client.json" >/dev/null
[[ "$(xdg-mime query default x-scheme-handler/file-catalog)" = file-catalog-handler.desktop ]]
systemctl --user is-enabled --quiet file-catalog-agent.timer
