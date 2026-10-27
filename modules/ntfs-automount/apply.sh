#!/usr/bin/env bash
# mount_options.conf est relu par udisks2 à chaque montage : pas de redémarrage nécessaire.
set -euo pipefail
source "$DOTFILES_LIB"
# Montage automatique côté KDE (module kded « Périphériques amovibles »)
kwriteconfig6 --file kded_device_automounterrc --group General --key AutomountEnabled true
kwriteconfig6 --file kded_device_automounterrc --group General --key AutomountOnLogin true
kwriteconfig6 --file kded_device_automounterrc --group General --key AutomountOnPlugin true
success "montage automatique NTFS configuré (débrancher/rebrancher le disque)"
