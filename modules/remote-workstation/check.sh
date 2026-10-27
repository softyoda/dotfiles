#!/usr/bin/env bash
[[ -n "${REMOTE_WORKSTATIONS:-}" ]] || exit 1
for entry in $REMOTE_WORKSTATIONS; do
    name="${entry%%=*}"
    [[ -f "$HOME/.config/remote-workstations/$name.conf" ]] || exit 1
    systemctl --user is-enabled -q "remote-ws-mount@$name.service" 2>/dev/null || exit 1
done
