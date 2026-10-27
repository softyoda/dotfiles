#!/usr/bin/env bash
# Active le thème (fichiers déjà déployés par [[files]]) et régénère l'initramfs si besoin.
set -euo pipefail
source "$DOTFILES_LIB"

theme=cogwheel-spinner

if [[ "$(plymouth-set-default-theme)" != "$theme" ]]; then
    info "thème Plymouth → $theme (régénération de l'initramfs, ~1 min)…"
    as_root plymouth-set-default-theme -R "$theme"
    success "thème $theme actif au prochain démarrage"
else
    info "thème $theme déjà actif"
fi

# Prérequis non gérés automatiquement (voir README) : on se contente de prévenir.
if ! cat /etc/mkinitcpio.conf /etc/mkinitcpio.conf.d/*.conf 2>/dev/null \
        | grep -E '^[[:space:]]*HOOKS=' | tail -n1 | grep -qw plymouth; then
    warn "le hook « plymouth » est absent de HOOKS dans /etc/mkinitcpio.conf"
fi
grep -qw splash /proc/cmdline || warn "paramètre noyau « splash » absent de la ligne de commande"
