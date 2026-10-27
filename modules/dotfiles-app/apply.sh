#!/usr/bin/env bash
set -euo pipefail
source "$DOTFILES_LIB"
mkdir -p ~/.local/bin
ln -sfn "$DOTFILES/bin/dotctl" ~/.local/bin/dotctl
success "dotctl → $DOTFILES/bin/dotctl"
# Emplacement du dossier privé (bibliothèque Seafile) mémorisé s'il est trouvé
priv=$(PYTHONPATH="$DOTFILES" python3 -c 'from dotctl import core; print(core.private_dir() or "")')
if [[ -n $priv ]]; then
    mkdir -p ~/.config/dotfiles && echo "$priv" > ~/.config/dotfiles/private-path
    success "dossier privé : $priv"
else
    warn "dossier privé introuvable : synchroniser la bibliothèque Seafile « dotfiles-private »"
fi
