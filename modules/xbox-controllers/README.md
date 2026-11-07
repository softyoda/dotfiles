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

## Dongle Xbox : diagnostic et correctif de reconnexion (7 novembre 2026)

**Lire [le dossier de reprise](REPRISE-XBOX-2026-11-07.md) avant toute intervention.**
Il décrit les bugs, les essais infructueux retirés, le pilote actuellement installé,
les validations à quatre manettes et les limites restantes.

Deux sous-parties explicites, désactivées par défaut pour les autres machines :

- `xbox-controllers/diagnostics` : collecte utilisateur et outil « Diagnostic manettes Xbox ».
- `xbox-controllers/xone-reconnect` : pilote local **0.5.8.1**, sources GPL conservées
  dans [`driver/xone-0.5.8.1`](driver/xone-0.5.8.1/), correctif complet consultable dans
  [`driver/xone-reconnect-local.patch`](driver/xone-reconnect-local.patch).

Ce sont les **sources du pilote Linux**, pas celles du firmware propriétaire Microsoft.
Le binaire existant reste fourni par `xone-dongle-firmware` ; aucun firmware n’a été
flashé durablement dans les manettes ou le récepteur.

### Restauration sur une machine compatible

Examiner `dotctl info xbox-controllers/<partie> --json` et
`dotctl plan xbox-controllers/<partie> --json` avant application. La sélection
explicite applique aussi le socle commun du module. L’installation du pilote nécessite
les en-têtes des noyaux cibles et les droits administrateur ; elle ne décharge aucun
pilote actif. Le correctif est encore local et dérive d’une proposition amont non fusionnée.
Ne pas le généraliser à un autre modèle de récepteur sans validation.

```sh
bin/dotctl apply xbox-controllers/diagnostics
bin/dotctl apply xbox-controllers/xone-reconnect
```

Le script pilote est aussi utilisable directement après revue :

```sh
sudo bash modules/xbox-controllers/driver/install.sh
# Retour au pilote fourni par le paquet, puis redémarrage hors partie :
sudo bash modules/xbox-controllers/driver/rollback.sh
```

L’installateur conserve `xone/0.5.8` pour le retour arrière et ajoute
`xone/0.5.8.1` dans DKMS (`AUTOINSTALL=yes`). Il choisit Clang ou GCC en fonction de
la configuration de chaque noyau. Ne pas confondre le statut DKMS « built » de
l’ancien pilote avec une ancienne version encore active.
