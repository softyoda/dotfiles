#!/usr/bin/env bash
set -euo pipefail
source "$DOTFILES_LIB"

# Fichier de secrets local (jamais commité) : créé vide à partir de l'exemple.
secrets="$HOME/.config/fish/secrets.fish"
if [[ ! -e "$secrets" ]]; then
    install -D -m 600 "$MODULE_DIR/files/secrets.fish.example" "$secrets"
    info "$secrets créé : y mettre les clés API (set -gx …)"
fi
chmod 600 "$secrets"

# Plugins fisher éventuels listés dans ~/.config/fish/fish_plugins.
# Pure, autopair et « done » viennent des paquets CachyOS : rien à installer par fisher.
if [[ -s "$HOME/.config/fish/fish_plugins" ]]; then
    fish -c 'fisher update' || warn "fisher update a échoué"
fi

# fish comme shell de connexion
fish_bin=$(command -v fish)
if [[ "$(getent passwd "$USER" | cut -d: -f7)" != "$fish_bin" && "$(getent passwd "$USER" | cut -d: -f7)" != /bin/fish ]]; then
    as_root chsh -s "$fish_bin" "$USER"
    success "shell par défaut : fish (effectif à la prochaine connexion)"
fi
success "fish configuré"
