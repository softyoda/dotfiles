#!/usr/bin/env bash
set -euo pipefail
source "$DOTFILES_LIB"

if lpstat -e 2>/dev/null | grep -qi selphy; then
    info "file CUPS de la Selphy déjà présente"
    exit 0
fi

# Découverte réseau (mDNS) nécessaire pour trouver l'imprimante sans adresse fixe.
systemctl is-active -q avahi-daemon.service || enable_system avahi-daemon.service
systemctl is-active -q cups.service || enable_system cups.service

uri="${SELPHY_URI:-}"
if [[ -z $uri ]]; then
    for _ in 1 2 3; do
        uri=$(as_root lpinfo --include-schemes dnssd -v 2>/dev/null | awk 'tolower($0) ~ /selphy/ {print $2; exit}') || true
        [[ -n $uri ]] && break
        sleep 2
    done
fi
if [[ -z $uri ]]; then
    warn "Selphy introuvable sur le réseau : l'allumer (Wi-Fi connecté) puis relancer, ou renseigner SELPHY_URI"
    exit 1
fi

as_root lpadmin -p Canon_SELPHY -D "Canon SELPHY" -E -v "$uri" -m everywhere
success "imprimante ajoutée : Canon_SELPHY ($uri)"
