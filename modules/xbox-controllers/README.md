# Manettes Xbox

| Élément | Rôle |
|---|---|
| `xpadneo-dkms` | pilote des manettes Xbox One/Series en **Bluetooth** (vibrations, batterie, bons mappings) |
| `xone-dkms` + `xone-dongle-firmware` | pilote du **dongle sans fil Xbox** et des manettes en USB |
| `/etc/modprobe.d/xpadneo.conf` | `disable_mouse=1` (pas de mode souris avec le stick) et `disable_shift_mode=1` (le bouton Xbox reste un bouton normal, utile pour Steam) |
| `/etc/modprobe.d/bluetooth.conf` | `disable_ertm=1` (requis par les manettes Xbox en Bluetooth) ; `btusb enable_autosuspend=0` (l'adaptateur ne se met pas en veille → pas de déconnexions/latence) |
| `/etc/udev/rules.d/50-realtek-bt-no-autosuspend.rules` | coupe la mise en veille USB du dongle Bluetooth Realtek `0bda:a728` |

Les paquets viennent des dépôts **CachyOS** ; sur Arch pur, ils sont dans l'AUR
(`paru -S xpadneo-dkms xone-dkms xone-dongle-firmware`). Les modules DKMS sont recompilés à
chaque mise à jour du noyau (paquet `*-headers` correspondant nécessaire).

La règle udev vise un modèle précis de dongle Bluetooth (Realtek `0bda:a728`, celui de
ryzen). Elle est sans effet si ce matériel est absent ; pour un autre adaptateur, trouver
`idVendor:idProduct` avec `lsusb` et dupliquer la ligne. `btusb enable_autosuspend=0`
couvre déjà la plupart des cas ; la règle est une sécurité supplémentaire.

Appairage : `bluetoothctl` ou Paramètres → Bluetooth, manette en mode appairage (bouton
sur le dessus maintenu jusqu'au clignotement rapide).
