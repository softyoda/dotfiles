#!/usr/bin/env bash
conf="$HOME/.var/app/com.seafile.Client/config/Seafile/Seafile Client.conf"
grep -qx 'hideMainWindowWhenStarted=true' "$conf" 2>/dev/null &&
{ [[ -z "${SEAFILE_SERVER_URL:-}" ]] || grep -qxF "main=$SEAFILE_SERVER_URL" "$conf"; }
