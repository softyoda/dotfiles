#!/usr/bin/env bash
# Exit 0 si ~/.local/share/arch-update/lib = libs patchées (copies identiques)
# + liens symboliques vers /usr/share/arch-update/lib pour tout le reste.
sys_lib=/usr/share/arch-update/lib
override="${XDG_DATA_HOME:-$HOME/.local/share}/arch-update/lib"
patched="$MODULE_DIR/files/lib"
[[ -d "$override" && ! -L "$override" ]] || exit 1
for f in "$sys_lib"/*; do
    n=$(basename "$f")
    if [[ -f "$patched/$n" ]]; then
        [[ ! -L "$override/$n" ]] && cmp -s "$patched/$n" "$override/$n" || exit 1
    else
        [[ "$(readlink "$override/$n")" == "$f" ]] || exit 1
    fi
done
# pas de fichier périmé en trop (ex. ancien tray.py)
for f in "$override"/*; do
    n=$(basename "$f")
    [[ -e "$sys_lib/$n" || -f "$patched/$n" ]] || exit 1
done
