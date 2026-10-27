#!/usr/bin/env bash
# Exit 0 si l'autologin vise $USER et la session attendue.
conf=/etc/plasmalogin.conf.d/autologin.conf
session="${AUTOLOGIN_SESSION:-plasma}"
awk -v u="$USER" -v s="$session" '
    /^\[/ { sec = $0; next }
    sec == "[Autologin]" && $0 == "User=" u    { fu = 1 }
    sec == "[Autologin]" && $0 == "Session=" s { fs = 1 }
    END { exit !(fu && fs) }' "$conf" 2>/dev/null
