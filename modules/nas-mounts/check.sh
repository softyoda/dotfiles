#!/usr/bin/env bash
# Le bloc géré existe dans /etc/fstab et correspond aux variables actuelles.
expected=$(bash "$MODULE_DIR/gen-block.sh" 2>/dev/null) || exit 1
current=$(sed -n '/^# >>> dotfiles nas-mounts/,/^# <<< dotfiles nas-mounts/p' /etc/fstab)
[[ -n "$current" && "$current" == "$expected" ]]
