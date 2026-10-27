#!/usr/bin/env bash
set -euo pipefail
source "$DOTFILES_LIB"
enable_system systemd-resolved.service
if [[ "$(readlink /etc/resolv.conf)" != */run/systemd/resolve/stub-resolv.conf ]]; then
    warn "/etc/resolv.conf ne pointe pas vers le stub systemd-resolved : voir le README"
fi
as_root systemctl restart systemd-resolved.service
success "DNS over TLS actif (vérifier : resolvectl status)"
