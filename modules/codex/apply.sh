#!/usr/bin/env bash
# Codex réécrit ~/.codex/config.toml (projets de confiance…) : on ne l’écrase jamais.
# Absent → copie de la base ; présent → ajout des clés manquantes en tête (clés de premier niveau).
set -euo pipefail
source "$DOTFILES_LIB"

cfg="$HOME/.codex/config.toml"
mkdir -p "$HOME/.codex"
if [[ ! -f "$cfg" ]]; then
    install -m 600 "$MODULE_DIR/files/config.toml" "$cfg"
    success "config.toml créé"
else
    for kv in "model_context_window = 872000" "model_auto_compact_token_limit = 800000"; do
        key="${kv%% *}"
        if ! grep -qE "^${key}[[:space:]]*=" "$cfg"; then
            sed -i "1i ${kv}" "$cfg"
            info "ajouté : $kv"
        fi
    done
    success "config.toml à jour (projets et serveurs MCP locaux conservés)"
fi
info "connexion à faire une fois : codex login (compte ChatGPT)"
