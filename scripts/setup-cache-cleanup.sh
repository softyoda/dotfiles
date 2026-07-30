#!/usr/bin/env bash
set -e

DOTFILES="$(cd "$(dirname "$0")/.." && pwd)"
source "$DOTFILES/scripts/utils.sh"

header "Nettoyage automatique des caches (pacman + paru)"

info "Installation du script /usr/local/bin/cache-cleanup.sh…"
sudo install -m 755 "$DOTFILES/scripts/cache-cleanup.sh" /usr/local/bin/cache-cleanup.sh

info "Installation des units systemd…"
sudo install -m 644 "$DOTFILES/systemd/system/cache-cleanup.service" /etc/systemd/system/cache-cleanup.service
sudo install -m 644 "$DOTFILES/systemd/system/cache-cleanup.timer"   /etc/systemd/system/cache-cleanup.timer

info "Activation du timer quotidien…"
sudo systemctl daemon-reload
sudo systemctl enable --now cache-cleanup.timer

success "Nettoyage quotidien activé (fichiers de cache > 7 jours supprimés chaque jour)."
echo "  → Prochaine exécution : $(systemctl list-timers cache-cleanup.timer --no-pager 2>/dev/null | awk 'NR==2{print $1, $2, $3}')"
