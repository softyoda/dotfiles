#!/usr/bin/env bash
# Client Spotify installé dans le dossier utilisateur par spotify-launcher.
set -euo pipefail
source "$DOTFILES_LIB"

SPICETIFY_VERSION=2.46.7      # CLI (se met ensuite à jour avec `spicetify update`)
MARKETPLACE_VERSION=1.0.9     # spicetify/marketplace
SPOTIFY_PATH="${XDG_DATA_HOME:-$HOME/.local/share}/spotify-launcher/install/usr/share/spotify"
CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
PREFS_PATH="${SPOTIFY_PATH%/install/usr/share/spotify}/spicetify-version.prefs"
CONF_DIR="$CONFIG_HOME/spicetify"
SPICETIFY="$HOME/.spicetify/spicetify"

# Désactive l’ancien déclencheur lors de la migration depuis Flatpak.
if [[ -f "$CONFIG_HOME/systemd/user/spicetify-reapply.path" ]]; then
    systemctl --user disable --now spicetify-reapply.path
fi

# 1. CLI Spicetify
if [[ ! -x "$SPICETIFY" ]]; then
    info "téléchargement de spicetify $SPICETIFY_VERSION"
    mkdir -p "$HOME/.spicetify"
    curl -fsSL "https://github.com/spicetify/cli/releases/download/v$SPICETIFY_VERSION/spicetify-$SPICETIFY_VERSION-linux-amd64.tar.gz" \
        | tar -xz -C "$HOME/.spicetify"
    chmod +x "$SPICETIFY"
fi

# 2. Marketplace (application personnalisée)
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

# 3. Réglages de config-xpui.ini, clé par clé (spicetify gère lui-même la section [Backup])
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

# Le module KDE peut aussi ajouter des actions à ce raccourci.
desktop="${XDG_DATA_HOME:-$HOME/.local/share}/applications/spotify-launcher.desktop"
if [[ ! -f "$desktop" ]]; then
    install -Dm644 /usr/share/applications/spotify-launcher.desktop "$desktop"
fi
kwriteconfig6 --file "$desktop" --group "Desktop Entry" --key Name Spotify
kwriteconfig6 --file "$desktop" --group "Desktop Entry" --key Exec "\"$HOME/.local/bin/spotify-with-spicetify\" %u"

# 4. Le raccourci natif applique le patch avant de lancer le client.
if [[ ! -x "$SPOTIFY_PATH/spotify" ]]; then
    info "Ouvrir Spotify depuis le menu pour initialiser le client natif."
else
    "$HOME/.local/bin/spicetify-reapply"
fi
