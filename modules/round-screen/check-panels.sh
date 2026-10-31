#!/usr/bin/env bash
set -euo pipefail
python3 - "${XDG_CONFIG_HOME:-$HOME/.config}/plasma-org.kde.plasma.desktop-appletsrc" <<'PY'
import re,sys
text=open(sys.argv[1]).read()
groups=re.split(r'^\[',text,flags=re.M)
# Seuls les conteneurs, pas les widgets imbriqués.
arcs=[g for g in groups if re.match(r'Containments\]\[\d+\]\n',g)
      and re.search(r'^plugin=org\.softyoda\.arcpanel$',g,re.M)]
sys.exit(0 if len(arcs)>=2 else 1)
PY
