#!/usr/bin/env bash
name="${FIREFOX_EXTRA_PROFILE:-}"
[[ -n "$name" ]] || exit 1
slug=${name,,}; slug=${slug// /-}; slug=$(tr -cd 'a-z0-9-' <<<"$slug")
grep -qxF "Name=$name" "${XDG_CONFIG_HOME:-$HOME/.config}/mozilla/firefox/profiles.ini" "$HOME/.mozilla/firefox/profiles.ini" 2>/dev/null &&
[[ -f "${XDG_DATA_HOME:-$HOME/.local/share}/applications/firefox-$slug.desktop" ]]
