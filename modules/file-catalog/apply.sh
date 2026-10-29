#!/usr/bin/env bash
set -euo pipefail
source "$DOTFILES_LIB"
need_vars CATALOG_URL CATALOG_PATH_MAP CATALOG_AGENT_ID CATALOG_LOCAL_SOURCES CATALOG_LAUNCH_KEY_SOURCE
revision=$(cat "$MODULE_DIR/revision")
source_dir="$HOME/.local/share/file-catalog/source"
if [[ ! -d "$source_dir/.git" ]]; then
    mkdir -p "$(dirname "$source_dir")"
    git -c credential.helper= -c 'credential.helper=!gh auth git-credential' clone https://github.com/softyoda/siftbay.git "$source_dir"
fi
[[ -z $(git -C "$source_dir" status --porcelain) ]] || { error "La copie installée a des modifications locales : $source_dir"; exit 1; }
if ! git -C "$source_dir" cat-file -e "$revision^{commit}" 2>/dev/null; then
    git -C "$source_dir" -c credential.helper= -c 'credential.helper=!gh auth git-credential' fetch origin "$revision"
fi
git -C "$source_dir" checkout --detach "$revision"
python3 "$source_dir/scripts/install_client.py"
for file in client.json local-paths.json sources.json agent.json; do python3 -m json.tool "$HOME/.config/file-catalog/$file" >/dev/null; done
install -m 600 "$CATALOG_LAUNCH_KEY_SOURCE" "$HOME/.config/file-catalog/local-launcher.key"
if [[ -n ${CATALOG_AGENT_KEY_SOURCE:-} && -f "$CATALOG_AGENT_KEY_SOURCE" ]]; then
    install -m 600 "$CATALOG_AGENT_KEY_SOURCE" "$HOME/.config/file-catalog/agent.key"
    enable_user file-catalog-agent.timer
fi
success "Siftbay installé. Le suivi en direct s’active depuis l’interface."
