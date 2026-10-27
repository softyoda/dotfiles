#!/usr/bin/env bash
# OpenCode : binaire (installeur officiel) + config.
#  (a) OPENCODE_SHARED_CONFIG accessible → ~/.config/opencode/{opencode.jsonc,agent,plugin,skills} = liens vers le NAS
#  (b) sinon → copie autonome de files/standalone (clé : {env:POE_API_KEY} ou `opencode auth login`)
set -euo pipefail
source "$DOTFILES_LIB"

# ─── Binaire ───────────────────────────────────────────────────────────────
if [[ -x "$HOME/.opencode/bin/opencode" ]] || has opencode; then
    success "OpenCode déjà installé"
else
    info "installation d’OpenCode (https://opencode.ai/install)"
    curl -fsSL https://opencode.ai/install | bash -s -- --no-modify-path
fi

cfg="$HOME/.config/opencode"
mkdir -p "$cfg"
items=(opencode.jsonc agent plugin skills)
stamp=$(date +%Y%m%d)

shared="${OPENCODE_SHARED_CONFIG:-}"
if [[ -n "$shared" ]] && timeout 10 test -f "$shared/opencode.jsonc"; then
    # ─── (a) config partagée sur le NAS ──────────────────────────────────────
    for it in "${items[@]}"; do
        dst="$cfg/$it"
        [[ "$(readlink "$dst" 2>/dev/null)" == "$shared/$it" ]] && continue
        if [[ -e "$dst" && ! -L "$dst" ]]; then
            mv "$dst" "$dst.bak-$stamp"
            warn "$dst sauvegardé en $dst.bak-$stamp"
        fi
        ln -sfn "$shared/$it" "$dst"
        info "$dst → $shared/$it"
    done
    success "config partagée liée ($shared)"
    if grep -qE '"apiKey"[[:space:]]*:[[:space:]]*"[^{"]' "$shared/opencode.jsonc"; then
        warn "le opencode.jsonc partagé contient une clé API en clair : la remplacer par \"{env:POE_API_KEY}\""
    fi
else
    # ─── (b) copie autonome ─────────────────────────────────────────────────
    [[ -n "$shared" ]] && warn "$shared inaccessible (NAS non monté ?) : copie autonome déployée"
    export OPENCODE_DIR="$cfg"
    export LLM_SERVER_URL="${LLM_SERVER_URL:-http://localhost:8081/v1}"
    src="$MODULE_DIR/files/standalone"
    for it in "${items[@]}"; do
        [[ -L "$cfg/$it" ]] && rm -f -- "$cfg/$it"   # ancien lien vers le NAS
    done
    mkdir -p "$cfg/agent" "$cfg/plugin" "$cfg/skills"
    cp -R "$src/agent/." "$cfg/agent/"
    cp -R "$src/plugin/." "$cfg/plugin/"
    cp "$src/CODING-RULES.md" "$cfg/CODING-RULES.md"
    # Seules ces deux variables sont substituées (les ${…} TypeScript restent intacts)
    envsubst '${OPENCODE_DIR} ${LLM_SERVER_URL}' < "$src/opencode.jsonc" > "$cfg/opencode.jsonc"
    envsubst '${LLM_SERVER_URL}' < "$src/plugin/team-workflow.ts" > "$cfg/plugin/team-workflow.ts"
    success "copie autonome déployée dans $cfg"
fi

# Dépendances des plugins (installées par OpenCode au démarrage à partir de package.json)
[[ -f "$cfg/package.json" ]] || cp "$MODULE_DIR/files/standalone/package.json" "$cfg/package.json"

info "connexion à faire une fois : opencode auth login → Poe (clé API Poe)"
