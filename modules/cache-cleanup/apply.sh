#!/usr/bin/env bash
set -euo pipefail
source "$DOTFILES_LIB"
as_root systemctl daemon-reload
enable_system cache-cleanup.timer
success "nettoyage quotidien activé (fichiers de cache > 7 jours)"
