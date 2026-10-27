#!/usr/bin/env bash
# Spotify en Flatpak *utilisateur* (spicetify doit pouvoir écrire dans l’appli,
# impossible sans root avec une installation --system), CLI Spicetify dans
# ~/.spicetify (installeur officiel), Marketplace, hook systemd.
set -euo pipefail
source "$DOTFILES_LIB"

SPICETIFY_VERSION=2.45.0      # CLI (se met ensuite à jour avec `spicetify update`)
MARKETPLACE_VERSION=1.0.9     # spicetify/marketplace
APP=com.spotify.Client
SPOTIFY_PATH="$HOME/.local/share/flatpak/app/$APP/current/active/files/extra/share/spotify"
PREFS_PATH="$HOME/.var/app/$APP/config/spotify/prefs"
CONF_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/spicetify"
SPICETIFY="$HOME/.spicetify/spicetify"

# 1. Spotify (Flatpak utilisateur)
if ! flatpak info --user "$APP" &>/dev/null; then
    if flatpak info --system "$APP" &>/dev/null; then
        warn "Spotify est installé en Flatpak système : spicetify ne pourra pas le patcher."
        warn "Le désinstaller (flatpak uninstall --system $APP) puis relancer ce module."
    fi
    flatpak remote-add --user --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
    info "installation de Spotify (Flatpak utilisateur)"
    flatpak install --user -y --noninteractive flathub "$APP"
fi

# 2. CLI Spicetify
if [[ ! -x "$SPICETIFY" ]]; then
    info "téléchargement de spicetify $SPICETIFY_VERSION"
    mkdir -p "$HOME/.spicetify"
    curl -fsSL "https://github.com/spicetify/cli/releases/download/v$SPICETIFY_VERSION/spicetify-$SPICETIFY_VERSION-linux-amd64.tar.gz" \
        | tar -xz -C "$HOME/.spicetify"
    chmod +x "$SPICETIFY"
fi

# 3. Marketplace (application personnalisée)
if [[ ! -f "$CONF_DIR/CustomApps/marketplace/manifest.json" ]]; then
    info "téléchargement du Marketplace $MARKETPLACE_VERSION"
    tmp=$(mktemp -d)
    curl -fsSL -o "$tmp/marketplace.zip" \
        "https://github.com/spicetify/marketplace/releases/download/v$MARKETPLACE_VERSION/marketplace.zip"
    unzip -q -o "$tmp/marketplace.zip" -d "$tmp"
    mkdir -p "$CONF_DIR/CustomApps"
    [[ -d "$CONF_DIR/CustomApps/marketplace" ]] && mv "$CONF_DIR/CustomApps/marketplace" "$tmp/old-marketplace"
    mv "$tmp/marketplace-dist" "$CONF_DIR/CustomApps/marketplace"
    rm -r -- "${tmp:?}"
fi

# 4. Réglages de config-xpui.ini, clé par clé (spicetify gère lui-même la section [Backup])
"$SPICETIFY" config >/dev/null 2>&1 || true   # crée config-xpui.ini si absent
cfg() { "$SPICETIFY" config "$1" "$2" >/dev/null; }
cfg spotify_path "$SPOTIFY_PATH"
cfg prefs_path "$PREFS_PATH"
cfg current_theme marketplace
cfg inject_css 1
cfg replace_colors 1
cfg inject_theme_js 1
cfg overwrite_assets 0
cfg always_enable_devtools 0
cfg check_spicetify_update 1
cfg home_config 1
cfg sidebar_config 0
cfg experimental_features 1
cfg remove_rtl_rule 1
cfg expose_apis 1
cfg disable_sentry 1
cfg disable_ui_logging 1
grep -Eq '^custom_apps *=.*\bmarketplace\b' "$CONF_DIR/config-xpui.ini" || cfg custom_apps marketplace
success "configuration Spicetify à jour"

# 5. Patch + hook de ré-application après chaque mise à jour Flatpak
if [[ -f "$PREFS_PATH" ]]; then
    "$HOME/.local/bin/spicetify-reapply"
else
    warn "Spotify n’a jamais été lancé (prefs absent) : le lancer une fois, se connecter, puis relancer ce module."
fi
enable_user spicetify-reapply.path
success "hook spicetify-reapply.path actif"
