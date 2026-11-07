#!/usr/bin/env bash
# Run explicitly as administrator; never reloads a live controller driver.
set -euo pipefail
[[ $EUID -eq 0 ]] || { echo 'Exécuter avec sudo.' >&2; exit 1; }
src=${1:-$(cd -- "$(dirname -- "$0")" && pwd)/xone-0.5.8.1}
dst=/usr/src/xone-0.5.8.1
[[ -f $src/dkms.conf && -d /usr/src/xone-0.5.8 ]] || { echo 'Sources xone-dkms 0.5.8 requises.' >&2; exit 1; }
if [[ -d $dst ]]; then
    for file in transport/dongle.c transport/mt76.c dkms.conf; do
        cmp -s "$src/$file" "$dst/$file" || { echo "Version locale existante différente : $file ; arrêter et examiner." >&2; exit 1; }
    done
else
    backup=/var/lib/xone-reconnect/backups/$(date +%Y%m%d-%H%M%S)
    install -d -m 0700 "$backup"
    dkms status -m xone > "$backup/dkms-before.txt"
    for directory in /lib/modules/*; do
        [[ -f $directory/build/.config ]] || continue
        kernel=${directory##*/}
        install -d "$backup/$kernel"
        for module in "$directory"/updates/dkms/xone*.ko*; do
            [[ ! -f $module ]] || cp -a "$module" "$backup/$kernel/"
        done
    done
    install -d "$dst"
    cp -a "$src/." "$dst/"
    chown -R root:root "$dst"
fi
[[ -L /var/lib/dkms/xone/0.5.8.1/source ]] || dkms add -m xone -v 0.5.8.1
# Build everything before replacing any module on disk.
for directory in /lib/modules/*; do
    [[ -f $directory/build/.config ]] || continue
    dkms build -m xone -v 0.5.8.1 -k "${directory##*/}"
done
for directory in /lib/modules/*; do
    [[ -f $directory/build/.config ]] || continue
    kernel=${directory##*/}
    if ! dkms status -m xone -v 0.5.8.1 -k "$kernel" | grep -q ': installed$'; then
        dkms install -m xone -v 0.5.8.1 -k "$kernel" --force
    fi
done
dkms status -m xone
