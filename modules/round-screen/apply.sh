#!/usr/bin/env bash
set -euo pipefail
source "$DOTFILES_LIB"
source "$MODULE_DIR/source.sh"
in_session || { warn "à lancer dans la session Plasma (écran rond branché)"; exit 1; }
ensure_linux_rond_source
# Conserver le réglage propre à cette machine dans le profil privé.
out=${ROUND_OUTPUT:-$(kscreen-doctor -j | python3 -c '
import json, sys
outs=[]
for o in json.load(sys.stdin)["outputs"]:
    s=o.get("size") or {}
    if o.get("connected") and s.get("width") and s.get("width")==s.get("height"):
        outs.append(o["name"])
if len(outs)==1: print(outs[0])')}
[[ -n $out ]] || { error "choisir ROUND_OUTPUT : aucune sortie carrée unique"; exit 1; }
kscreen-doctor "output.$out.scale.${ROUND_SCALE:-1.5}" >/dev/null
"$LINUX_ROND_SOURCE/scripts/install.sh"
success "Linux Rond installé à la révision $LINUX_ROND_REVISION ; panneaux conservés"
