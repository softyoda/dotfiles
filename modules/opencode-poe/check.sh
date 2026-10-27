#!/usr/bin/env bash
[[ -x "$HOME/.opencode/bin/opencode" ]] || command -v opencode >/dev/null || exit 1
cfg="$HOME/.config/opencode"
shared="${OPENCODE_SHARED_CONFIG:-}"
if [[ -n "$shared" ]] && timeout 10 test -f "$shared/opencode.jsonc"; then
    for it in opencode.jsonc agent plugin skills; do
        [[ "$(readlink "$cfg/$it")" == "$shared/$it" ]] || exit 1
    done
else
    for it in opencode.jsonc agent plugin skills; do
        [[ -e "$cfg/$it" ]] || exit 1
    done
fi
