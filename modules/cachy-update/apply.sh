#!/usr/bin/env bash
# Installe ~/.local/share/arch-update/lib (prioritaire sur /usr/share/arch-update/lib) :
#   - libs patchées du module (files/lib/*.sh) : copiées ;
#   - toutes les autres : liens symboliques vers la version système, pour suivre
#     automatiquement les mises à jour du paquet.
# Le dossier est reconstruit à part puis échangé d'un coup (jamais à moitié installé).
set -euo pipefail
source "$DOTFILES_LIB"

sys_lib=/usr/share/arch-update/lib
data_home="${XDG_DATA_HOME:-$HOME/.local/share}"
override="$data_home/arch-update/lib"
patched="$MODULE_DIR/files/lib"

[[ -d "$sys_lib" ]] || { error "$sys_lib introuvable (cachy-update installé ?)"; exit 1; }

if bash "$MODULE_DIR/check.sh"; then
    info "bibliothèques déjà à jour"
    exit 0
fi

mkdir -p "$(dirname "$override")"
staging=$(mktemp -d "$(dirname "$override")/.lib-install.XXXXXX")
trap 'rm -rf -- "$staging"' EXIT

for f in "$sys_lib"/*; do
    ln -s "$f" "$staging/$(basename "$f")"
done
for f in "$patched"/*.sh; do
    [[ -e "$sys_lib/$(basename "$f")" ]] || warn "$(basename "$f") n'existe plus dans $sys_lib : patch à revoir"
    install -m 755 "$f" "$staging/$(basename "$f")"
    bash -n "$staging/$(basename "$f")"
done

if [[ -e "$override" || -L "$override" ]]; then
    backup="$override.backup-$(date +%Y%m%d-%H%M%S)"
    mv "$override" "$backup"
    info "ancien dossier sauvegardé : $backup"
fi
mv "$staging" "$override"
trap - EXIT

success "mode automatique installé : au prochain « Proceed with update? », répondre A"
