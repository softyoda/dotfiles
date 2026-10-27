#!/usr/bin/env python3
"""Pose des clés dans la section [options] d'un fichier toml RustDesk.

Usage : rustdesk-set-options.py FICHIER clé=valeur [clé=valeur…]
Édition ligne à ligne : le reste du fichier (mots de passe, clés…) n'est ni lu
ni modifié. Code de sortie 0 = modifié, 3 = déjà à jour.
"""
import re
import sys
from pathlib import Path

path = Path(sys.argv[1])
wanted = dict(a.split("=", 1) for a in sys.argv[2:])
lines = path.read_text().splitlines() if path.exists() else []

start = next((i for i, l in enumerate(lines) if l.strip() == "[options]"), None)
if start is None:
    lines += ["", "[options]"]
    start = len(lines) - 1
end = next((i for i in range(start + 1, len(lines)) if lines[i].lstrip().startswith("[")), len(lines))

changed = False
for key, val in wanted.items():
    new = f"{key} = '{val}'"
    pat = re.compile(rf"^\s*'?{re.escape(key)}'?\s*=")
    idx = next((i for i in range(start + 1, end) if pat.match(lines[i])), None)
    if idx is None:
        lines.insert(end, new)
        end += 1
        changed = True
    elif lines[idx] != new:
        lines[idx] = new
        changed = True

if changed:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")
sys.exit(0 if changed else 3)
