#!/usr/bin/env bash
# Restore packaged modules on disk; no forced reload in the middle of a game.
set -euo pipefail
[[ $EUID -eq 0 ]] || { echo 'Exécuter avec sudo.' >&2; exit 1; }
dkms remove -m xone -v 0.5.8.1 --all
for directory in /lib/modules/*; do
    [[ -f $directory/build/.config ]] || continue
    kernel=${directory##*/}
    # Preserve original built modules when available; DKMS can rebuild if needed.
    dkms install -m xone -v 0.5.8 -k "$kernel" --force
done
echo 'Pilote d’origine restauré sur disque ; redémarrer lorsque la partie est terminée.'
