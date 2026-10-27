#!/usr/bin/env bash
systemctl -q is-enabled mullvad-daemon.service || exit 1
mullvad lan get 2>/dev/null | grep -q ': allow' || exit 1
mullvad auto-connect get 2>/dev/null | grep -q ': on' || exit 1
t=$(mullvad tunnel get 2>/dev/null)
grep -Eq 'Quantum resistance: +on' <<<"$t" && grep -Eq 'DAITA: +true' <<<"$t" && grep -Eq 'IPv6: +off' <<<"$t" || exit 1
gui="${XDG_CONFIG_HOME:-$HOME/.config}/Mullvad VPN/gui_settings.json"
python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); sys.exit(0 if d.get("startMinimized") and d.get("unpinnedWindow") else 1)' "$gui"
