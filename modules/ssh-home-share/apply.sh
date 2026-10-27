#!/usr/bin/env bash
# Côté serveur : sshd (clés uniquement), clés autorisées, mDNS (<hôte>.local), pare-feu.
set -euo pipefail
source "$DOTFILES_LIB"
need_vars SHARE_AUTHORIZED_KEYS_FILE

# ─── Clés autorisées ────────────────────────────────────────────────────────
keys="${SHARE_AUTHORIZED_KEYS_FILE/#\~/$HOME}"
if [[ "$keys" != /* ]]; then
    for d in "${DOTFILES_PRIVATE:-}" "$HOME/.config/dotfiles-private" "$DOTFILES/../dotfiles-private"; do
        [[ -n "$d" && -f "$d/$keys" ]] && { keys="$d/$keys"; break; }
    done
fi
[[ -f "$keys" ]] || { error "fichier de clés introuvable : $SHARE_AUTHORIZED_KEYS_FILE"; exit 1; }
if grep -q 'PRIVATE KEY' "$keys"; then
    error "$keys contient une clé PRIVÉE : n’y mettre que des clés publiques (.pub)"; exit 1
fi

ak="$HOME/.ssh/authorized_keys"
install -d -m 700 "$HOME/.ssh"
touch "$ak" && chmod 600 "$ak"
added=0
while IFS= read -r line; do
    [[ "$line" =~ ^(ssh-|ecdsa-|sk-) ]] || continue
    grep -qxF -- "$line" "$ak" || { echo "$line" >> "$ak"; added=$((added + 1)); }
done < "$keys"
((added)) && success "$added clé(s) ajoutée(s) à $ak" || success "clés autorisées déjà à jour"
if ! grep -qE '^(ssh-|ecdsa-|sk-)' "$ak"; then
    warn "aucune clé dans $ak : avec PasswordAuthentication no, plus aucun accès SSH possible"
fi

# ─── sshd ───────────────────────────────────────────────────────────────────
grep -qE '^Include /etc/ssh/sshd_config.d/\*\.conf' /etc/ssh/sshd_config ||
    warn "/etc/ssh/sshd_config n’inclut pas sshd_config.d/*.conf : le drop-in serait ignoré"
as_root sshd -t || { error "configuration sshd invalide"; exit 1; }
enable_system sshd
as_root systemctl reload sshd || true

# ─── mDNS : <hôte>.local ────────────────────────────────────────────────────
if ! grep -qE '^hosts:.*mdns' /etc/nsswitch.conf; then
    as_root sed -i -E '/^hosts:/{/ resolve/{s/ resolve/ mdns_minimal [NOTFOUND=return] resolve/;b};s/ dns/ mdns_minimal [NOTFOUND=return] dns/}' /etc/nsswitch.conf
    grep -qE '^hosts:.*mdns_minimal' /etc/nsswitch.conf && info "nsswitch.conf : mdns_minimal ajouté" ||
        warn "nsswitch.conf : ajouter « mdns_minimal [NOTFOUND=return] » à la ligne hosts à la main"
fi
enable_system avahi-daemon
if systemctl is-active -q systemd-resolved && resolvectl status 2>/dev/null | grep -q '+mDNS'; then
    warn "systemd-resolved a aussi mDNS actif : mettre MulticastDNS=no dans resolved.conf pour laisser avahi seul"
fi

# ─── Pare-feu ───────────────────────────────────────────────────────────────
if has ufw && LC_ALL=C as_root ufw status | grep -q 'Status: active'; then
    as_root ufw allow ssh >/dev/null && success "ufw : ssh autorisé"
fi

success "$(hostname).local accessible en SSH (clé uniquement) pour $USER"
