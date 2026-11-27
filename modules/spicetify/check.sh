#!/usr/bin/env bash
config_home="${XDG_CONFIG_HOME:-$HOME/.config}"
conf="$config_home/spicetify"
ini="$conf/config-xpui.ini"
data_home="${XDG_DATA_HOME:-$HOME/.local/share}"
spotify_path="$data_home/spotify-launcher/install/usr/share/spotify"
desktop="$data_home/applications/spotify-launcher.desktop"
[[ -x "$HOME/.spicetify/spicetify" && -f "$conf/CustomApps/marketplace/manifest.json" ]] &&
grep -Eq '^custom_apps *=.*\bmarketplace\b' "$ini" &&
grep -Eq '^current_theme *= *marketplace' "$ini" &&
grep -Eq '^disable_sentry *= *1' "$ini" &&
grep -Fxq "spotify_path=$spotify_path" <(sed -E 's/^spotify_path[[:space:]]*=[[:space:]]*/spotify_path=/' "$ini") &&
grep -Fxq "prefs_path=$config_home/spotify/prefs" <(sed -E 's/^prefs_path[[:space:]]*=[[:space:]]*/prefs_path=/' "$ini") &&
grep -Fxq "Exec=\"$HOME/.local/bin/spotify-with-spicetify\" %u" "$desktop" &&
! systemctl --user -q is-enabled spicetify-reapply.path 2>/dev/null
