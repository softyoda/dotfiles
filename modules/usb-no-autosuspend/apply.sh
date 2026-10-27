#!/usr/bin/env bash
set -euo pipefail
source "$DOTFILES_LIB"
as_root udevadm control --reload-rules
# La règle agit au branchement ; pour les périphériques déjà présents, on applique directement.
for f in /sys/bus/usb/devices/*/power/autosuspend; do
    [[ "$(cat "$f")" == -1 ]] || echo -1 | as_root tee "$f" >/dev/null || true
done
success "mise en veille USB désactivée pour tous les périphériques"
