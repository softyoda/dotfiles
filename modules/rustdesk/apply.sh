#!/usr/bin/env bash
# Service système + options NON secrètes. Le mot de passe permanent, les clés
# et l’identifiant ne sont jamais gérés ici (voir README).
# Serveur auto-hébergé facultatif : RUSTDESK_SERVER=hôte[:port] dotctl apply rustdesk
set -euo pipefail
source "$DOTFILES_LIB"

conf="${XDG_CONFIG_HOME:-$HOME/.config}/rustdesk"
setopt() { python3 "$MODULE_DIR/files/rustdesk-set-options.py" "$@"; }

opts=(allow-linux-headless=Y verification-method=use-permanent-password)
[[ -n "${RUSTDESK_SERVER:-}" ]] && opts+=("custom-rendezvous-server=$RUSTDESK_SERVER")

changed=0
setopt "$conf/RustDesk2.toml" "${opts[@]}" && changed=1 || [[ $? == 3 ]]
setopt "$conf/RustDesk_local.toml" enable-check-update=N || [[ $? == 3 ]]

enable_system rustdesk.service
if ((changed)); then
    as_root systemctl restart rustdesk.service
    info "service RustDesk redémarré pour prendre en compte les options"
fi
success "RustDesk : service actif, accès sans session, pas de vérification de mise à jour"
