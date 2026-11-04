#!/usr/bin/env bash
set -euo pipefail
source "$DOTFILES_LIB"
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
success "Siftbay installé : ouverture locale, connexion au serveur depuis les paramètres."
