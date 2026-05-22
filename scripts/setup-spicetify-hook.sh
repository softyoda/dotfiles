#!/bin/bash
# Installe le hook systemd qui ré-applique spicetify après chaque update de Spotify (Flatpak).
# Idempotent : peut être ré-exécuté sans danger.

set -e
source "$(dirname "$0")/utils.sh"

DOTFILES="$(cd "$(dirname "$0")/.." && pwd)"

header "Hook auto-reapply Spicetify"

mkdir -p "$HOME/.config/systemd/user" "$HOME/.local/bin"

install -m 755 "$DOTFILES/scripts/spicetify-reapply" "$HOME/.local/bin/spicetify-reapply"
install -m 644 "$DOTFILES/systemd/user/spicetify-reapply.service" "$HOME/.config/systemd/user/spicetify-reapply.service"
install -m 644 "$DOTFILES/systemd/user/spicetify-reapply.path"    "$HOME/.config/systemd/user/spicetify-reapply.path"

systemctl --user daemon-reload
systemctl --user enable --now spicetify-reapply.path >/dev/null

success "Hook activé — spicetify backup apply tournera à chaque update de Spotify."
