#!/usr/bin/env bash
set -euo pipefail
source "$DOTFILES_LIB"
need_vars HDMI_TV_EDID_MATCH

# ── sudo sans mot de passe pour hdmi-redetect (et uniquement lui) ───────────
# Validé par visudo avant installation : un sudoers invalide bloquerait sudo.
dst=/etc/sudoers.d/hdmi-redetect
tmp=$(mktemp)
trap 'rm -f -- "$tmp"' EXIT
sed "s/\${USER}/$USER/g" "$MODULE_DIR/files/sudoers-hdmi-redetect" > "$tmp"
if ! as_root cmp -s "$tmp" "$dst"; then
    as_root visudo -cf "$tmp" >/dev/null || { error "règle sudoers invalide, non installée"; exit 1; }
    as_root install -m 440 -o root -g root "$tmp" "$dst"
    info "règle sudoers installée : $dst"
fi

# ── service de surveillance (session graphique) ─────────────────────────────
enable_user hdmi-recovery.service
systemctl --user restart hdmi-recovery.service || true

# ── raccourci global Alt+F9 → hdmi-redetect.desktop ─────────────────────────
kwriteconfig6 --file kglobalshortcutsrc --group services --group hdmi-redetect.desktop --key _launch "Alt+F9"
command -v kbuildsycoca6 >/dev/null && kbuildsycoca6 &>/dev/null || true

success "récupération HDMI active ; Alt+F9 effectif après reconnexion"
