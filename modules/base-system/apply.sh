#!/usr/bin/env bash
# Réglages système de base (idempotent) : paru, Flathub, pacman.conf, paru.conf,
# SUDO_ASKPASS, groupes. Ne réécrit jamais pacman.conf en entier : édition clé par clé.
set -euo pipefail
source "$DOTFILES_LIB"

# Règle une option de la section [options] d'un fichier ini root (pacman.conf, paru.conf).
#   set_option FICHIER CLÉ [VALEUR]
# - ligne active déjà correcte : rien ;
# - ligne présente (commentée ou autre valeur) : remplacée sur place ;
# - absente : ajoutée juste après « [options] ».
set_option() {
    local file="$1" key="$2" value="${3:-}" want ok
    if [[ -n "$value" ]]; then
        want="$key = $value"; ok="^[[:space:]]*${key}[[:space:]]*=[[:space:]]*${value}[[:space:]]*$"
    else
        want="$key"; ok="^[[:space:]]*${key}[[:space:]]*$"
    fi
    grep -Eq "$ok" "$file" && return 0
    local any="^[[:space:]]*#?[[:space:]]*${key}([[:space:]]*=.*)?[[:space:]]*$"
    if grep -Eq "$any" "$file"; then
        as_root sed -i -E "0,/${any}/s//${want}/" "$file"
    else
        as_root sed -i "/^\[options\]/a ${want}" "$file"
    fi
    info "$file : $want"
}

# ── paru ────────────────────────────────────────────────────────────────────
if ! has paru; then
    if pacman -Si paru &>/dev/null; then
        info "installation de paru (dépôt CachyOS)…"
        as_root pacman -S --needed --noconfirm paru
    else
        info "compilation de paru depuis l'AUR…"
        tmp=$(mktemp -d)
        trap 'rm -rf -- "$tmp"' EXIT
        git clone --depth 1 https://aur.archlinux.org/paru-bin.git "$tmp/paru"
        (cd "$tmp/paru" && makepkg -si --noconfirm)
    fi
    success "paru installé"
fi

# ── Flathub ─────────────────────────────────────────────────────────────────
if ! flatpak remotes --system --columns=name 2>/dev/null | grep -qx flathub; then
    as_root flatpak remote-add --system --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
    success "dépôt Flathub ajouté"
fi

# ── pacman.conf ─────────────────────────────────────────────────────────────
set_option /etc/pacman.conf Color
set_option /etc/pacman.conf ILoveCandy
set_option /etc/pacman.conf DisableDownloadTimeout
set_option /etc/pacman.conf ParallelDownloads 10

# ── paru.conf : pas de revue interactive des PKGBUILD ───────────────────────
[[ -f /etc/paru.conf ]] && set_option /etc/paru.conf SkipReview

# ── sudo graphique (fenêtre KDE) pour les applications sans terminal ────────
if ! grep -qx 'SUDO_ASKPASS=/usr/bin/ksshaskpass' /etc/environment; then
    if grep -q '^SUDO_ASKPASS=' /etc/environment; then
        as_root sed -i 's|^SUDO_ASKPASS=.*|SUDO_ASKPASS=/usr/bin/ksshaskpass|' /etc/environment
    else
        ensure_line_root 'SUDO_ASKPASS=/usr/bin/ksshaskpass' /etc/environment
    fi
    info "SUDO_ASKPASS défini (effectif après reconnexion)"
fi

# ── groupes ─────────────────────────────────────────────────────────────────
# Seulement les groupes d'administration ; docker & co sont gérés par les modules concernés.
ensure_groups wheel

success "système de base configuré"
