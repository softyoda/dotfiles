#!/usr/bin/env bash
prefix="${WINEPREFIX:-$HOME/.wine}"
[[ -d "$prefix" ]] || exit 0
grep -q '^"ddraw"="native,builtin"' "$prefix/user.reg" &&
grep -q '^"dinput"="native,builtin"' "$prefix/user.reg"
