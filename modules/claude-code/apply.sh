#!/usr/bin/env bash
# Installeur natif officiel : binaire dans ~/.local/share/claude, lien ~/.local/bin/claude,
# mises à jour automatiques gérées par Claude Code lui-même.
set -euo pipefail
source "$DOTFILES_LIB"

if [[ -x "$HOME/.local/bin/claude" ]] || has claude; then
    success "Claude Code déjà installé"
else
    info "installation de Claude Code (curl -fsSL https://claude.ai/install.sh | bash)"
    curl -fsSL https://claude.ai/install.sh | bash
fi
has jq || warn "jq absent : le hook gh de settings.json en a besoin (pacman -S jq)"
info "connexion à faire une fois : lancer « claude » puis /login (compte Claude Pro/Max)"
