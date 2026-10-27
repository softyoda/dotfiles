#!/usr/bin/env bash
src="$MODULE_DIR/files/mixxx-rgb.patch"
prefix="$HOME/.local/opt/mixxx-rgb"
[[ -x "$prefix/bin/mixxx" ]] &&
[[ -f "$HOME/.local/lib/mixxx-space-alias/generic/libmixxxspacealias.so" ]] &&
[[ -f "$prefix/.stamp-2.5.6-$(sha256sum "$src" 2>/dev/null | cut -c1-12)" ]]
