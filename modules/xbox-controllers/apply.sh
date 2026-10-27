#!/usr/bin/env bash
set -euo pipefail
source "$DOTFILES_LIB"
as_root udevadm control --reload-rules
# Dongle Bluetooth Realtek déjà branché : appliquer la règle tout de suite.
for d in /sys/bus/usb/devices/*; do
    [[ "$(cat "$d/idVendor" 2>/dev/null):$(cat "$d/idProduct" 2>/dev/null)" == 0bda:a728 ]] || continue
    echo on | as_root tee "$d/power/control" >/dev/null
done
success "manettes Xbox configurées (options des modules effectives au prochain redémarrage)"
