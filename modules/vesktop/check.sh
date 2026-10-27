#!/usr/bin/env bash
apps="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
autostart="${XDG_CONFIG_HOME:-$HOME/.config}/autostart"
grep -q '^Exec=.*/usr/bin/vesktop' "$apps/vesktop.desktop" 2>/dev/null &&
grep -q '^Exec=.*vesktop --start-minimized' "$autostart/vesktop.desktop" 2>/dev/null &&
[[ $(xdg-mime query default x-scheme-handler/discord) == vesktop.desktop ]]
