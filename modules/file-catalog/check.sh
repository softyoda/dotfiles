#!/usr/bin/env bash
set -e
[[ -x "$HOME/.local/bin/siftbay" ]]
source_dir="$HOME/.local/share/file-catalog/source"
[[ $(git -C "$source_dir" rev-parse HEAD) = $(cat "$MODULE_DIR/revision") ]]
[[ -z $(git -C "$source_dir" status --porcelain) ]]
[[ "$(xdg-mime query default x-scheme-handler/file-catalog)" = file-catalog-handler.desktop ]]
