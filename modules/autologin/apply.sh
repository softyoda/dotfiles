#!/usr/bin/env bash
# Autologin Plasma Login Manager pour $USER.
# Session : variable facultative AUTOLOGIN_SESSION (profil privé), « plasma » par défaut
# (nom d'un fichier de /usr/share/wayland-sessions ou /usr/share/xsessions, sans .desktop).
set -euo pipefail
source "$DOTFILES_LIB"

session="${AUTOLOGIN_SESSION:-plasma}"
conf=/etc/plasmalogin.conf.d/autologin.conf

if [[ ! -f /usr/share/wayland-sessions/$session.desktop && ! -f /usr/share/xsessions/$session.desktop ]]; then
    warn "session « $session » introuvable dans /usr/share/{wayland-sessions,xsessions}"
fi
has plasmalogin || warn "Plasma Login Manager (paquet plasma-login-manager) n'est pas installé"

want=$(printf '[Autologin]\nUser=%s\nSession=%s\n' "$USER" "$session")
if [[ "$(cat "$conf" 2>/dev/null)" != "$want" ]]; then
    printf '%s\n' "$want" | as_root install -D -m 644 /dev/stdin "$conf"
    success "autologin : $USER → $session (effectif au prochain démarrage)"
else
    info "autologin déjà configuré ($USER → $session)"
fi

# Un fichier trié après autologin.conf dans plasmalogin.conf.d l'emporte : on prévient.
for f in /etc/plasmalogin.conf.d/*.conf; do
    [[ "$f" == "$conf" || "$f" < "$conf" ]] && continue
    grep -q '^Session=' "$f" && warn "$f redéfinit la session d'autologin (prioritaire)"
done
systemctl is-enabled -q plasmalogin.service 2>/dev/null \
    || warn "plasmalogin.service n'est pas le gestionnaire de connexion actif"
