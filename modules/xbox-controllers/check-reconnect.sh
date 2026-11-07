#!/usr/bin/env bash
set -euo pipefail
src="$MODULE_DIR/driver/xone-0.5.8.1"
installed=/usr/src/xone-0.5.8.1
for file in transport/dongle.c transport/mt76.c dkms.conf; do
    cmp -s "$src/$file" "$installed/$file"
done
[[ $(modinfo -F version xone_dongle) == 0.5.8.1 ]]
dkms status -m xone -v 0.5.8.1 -k "$(uname -r)" | grep -q ': installed$'
