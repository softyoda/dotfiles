#!/usr/bin/env bash
set -euo pipefail
source "$DOTFILES_LIB"
in_session || { warn "à lancer dans la session Plasma (écran rond branché)"; exit 1; }

# Sortie ronde = première sortie carrée connectée (ou ROUND_OUTPUT)
out=${ROUND_OUTPUT:-$(kscreen-doctor -j | python3 -c '
import json, sys
for o in json.load(sys.stdin)["outputs"]:
    s = o.get("size") or {}
    if o.get("connected") and s.get("width") and s.get("width") == s.get("height"):
        print(o["name"]); break')}
[[ -n $out ]] || { error "aucun écran carré/rond détecté"; exit 1; }
kscreen-doctor "output.$out.scale.${ROUND_SCALE:-1.5}" >/dev/null
success "échelle ${ROUND_SCALE:-1.5} sur $out"

# Script KWin « zone sûre »
pkg="$MODULE_DIR/kwin-script/round-safe-area"
if [[ -d ~/.local/share/kwin/scripts/round-safe-area ]]; then
    kpackagetool6 --type KWin/Script --upgrade "$pkg" >/dev/null
else
    kpackagetool6 --type KWin/Script --install "$pkg" >/dev/null
fi
kwriteconfig6 --file kwinrc --group Plugins --key round-safe-areaEnabled true
qdbus6 org.kde.KWin /Scripting org.kde.kwin.Scripting.unloadScript round-safe-area >/dev/null 2>&1 || true
qdbus6 org.kde.KWin /KWin reconfigure
success "zone sûre active : les fenêtres restent dans le carré visible"

# Barre du haut (sauvegarde de l'ancienne disposition une seule fois)
rc=~/.config/plasma-org.kde.plasma.desktop-appletsrc
[[ -f $rc.bak-avant-rond ]] || cp "$rc" "$rc.bak-avant-rond"
qdbus6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "$(cat "$MODULE_DIR/files/panels.js")" >/dev/null
success "barre ronde en place (ancienne disposition : $rc.bak-avant-rond)"
