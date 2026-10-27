#!/usr/bin/env bash
# Réglages clé par clé du fichier Qt du client (il contient aussi la position
# de la fenêtre, réécrite à chaque fermeture : on ne l’écrase donc pas).
set -euo pipefail
source "$DOTFILES_LIB"
need_vars SEAFILE_SERVER_URL

conf="$HOME/.var/app/com.seafile.Client/config/Seafile/Seafile Client.conf"

if pgrep -f seafile-applet >/dev/null; then
    warn "Seafile est lancé : le quitter (icône → Quitter) puis relancer ce module pour garantir la prise en compte"
fi

python3 - "$conf" "$SEAFILE_SERVER_URL" <<'EOF'
import sys
from pathlib import Path

path, server = Path(sys.argv[1]), sys.argv[2]
wanted = {"Behavior": {"hideMainWindowWhenStarted": "true", "hideDockIcon": "false"},
          "UsedServerAddresses": {"main": server}}
lines = path.read_text().splitlines() if path.exists() else []
for section, kv in wanted.items():
    head = f"[{section}]"
    if head not in lines:
        lines += ([""] if lines else []) + [head]
    start = lines.index(head)
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("[")), len(lines))
    while end > start + 1 and not lines[end - 1].strip():
        end -= 1
    for key, val in kv.items():
        idx = next((i for i in range(start + 1, end) if lines[i].split("=", 1)[0] == key), None)
        if idx is None:
            lines.insert(end, f"{key}={val}")
            end += 1
        else:
            lines[idx] = f"{key}={val}"
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text("\n".join(lines) + "\n")
EOF
success "Seafile : serveur $SEAFILE_SERVER_URL, démarrage sans fenêtre"
