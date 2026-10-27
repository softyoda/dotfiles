#!/usr/bin/env bash
conf="${XDG_CONFIG_HOME:-$HOME/.config}/spicetify"
ini="$conf/config-xpui.ini"
[[ -x "$HOME/.spicetify/spicetify" ]] &&
flatpak info --user com.spotify.Client &>/dev/null &&
[[ -f "$conf/CustomApps/marketplace/manifest.json" ]] &&
grep -Eq '^custom_apps *=.*\bmarketplace\b' "$ini" &&
grep -Eq '^current_theme *= *marketplace' "$ini" &&
grep -Eq '^disable_sentry *= *1' "$ini" &&
grep -Eq "^spotify_path *= *$HOME/.local/share/flatpak/" "$ini" &&
systemctl --user -q is-enabled spicetify-reapply.path
