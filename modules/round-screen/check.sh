#!/usr/bin/env bash
set -euo pipefail
source "$MODULE_DIR/source.sh"
[[ -d $LINUX_ROND_SOURCE/.git ]]
[[ $(git -C "$LINUX_ROND_SOURCE" remote get-url origin) == "$LINUX_ROND_URL" ]]
[[ $(git -C "$LINUX_ROND_SOURCE" rev-parse HEAD) == "$LINUX_ROND_REVISION" ]]
[[ -z $(git -C "$LINUX_ROND_SOURCE" status --porcelain) ]]
"$LINUX_ROND_SOURCE/scripts/check.sh"
