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

## Traces de connexion renforcées (15 novembre 2026)

L’incident de 22:10:37–22:10:46 pendant une partie de 007 a montré une disparition
réelle de la manette puis sa reconnexion, alors que le dongle USB restait présent
et le pilote corrigé était chargé. Son voyant clignotait ; batterie « High » avant
et après. La cause profonde n’est pas établie ; le correctif du 7 novembre ne
constitue donc pas une élimination démontrée de toutes les coupures.

`xbox-controllers/event-traces` active une liste limitée de messages **déjà présents**
dans le pilote : `CLIENT_LOST`, ajout/retrait/appairage/chiffrement des clients,
statut GIP déconnecté, annonce et versions firmware, création/destruction des
périphériques, chargement firmware et chemins suspend/resume. Cela peut aider à
distinguer un événement de perte déclaré par le récepteur d’une déconnexion
signalée dans le protocole GIP. Cela ne mesure pas les interférences ni le signal
radio et ne garantit pas d’établir une cause physique.

Aucun debug global de module, paquet de boutons, paquet audio, dump USB, clé de
chiffrement, reset, reload ou recompilation du pilote. Les messages peuvent contenir
une adresse matérielle : ils restent dans les archives locales, à anonymiser avant partage.

Fichiers système installés après autorisation :

- `/etc/modprobe.d/xone-event-traces.conf` : réapplique les sélecteurs au prochain
  chargement de `xone_dongle` / `xone_gip`, y compris après redémarrage.
- `/usr/local/libexec/xone-event-traces.py` : active/désactive les mêmes sélecteurs
  sur les modules actuellement chargés, via dynamic debug. Le contrôle vérifie
  l’activation de tous les points sélectionnés disponibles ; zéro point est une erreur.

La collecte utilisateur existante archive ces nouveaux messages avec la même
rotation (30 jours maximum, plafond 256 Mio). La configuration persistante est
incluse dans l’état et les rapports ; sa présence ne prouve pas à elle seule les
flags du noyau courant. Les messages du noyau restent aussi soumis aux limites
journald/rate-limit ; aucun volume illimité ni garantie de capturer tout événement.

```sh
bin/dotctl info xbox-controllers/event-traces --json
bin/dotctl plan xbox-controllers/event-traces --json
bin/dotctl apply xbox-controllers/event-traces
sudo python3 /usr/local/libexec/xone-event-traces.py status
```

Pour arrêter ces traces, sans perturber les manettes :

```sh
sudo python3 /usr/local/libexec/xone-event-traces.py disable
sudo rm -- /etc/modprobe.d/xone-event-traces.conf
```

La collecte normale reste active. Décocher une sous-partie dans l’interface ne
supprime pas les fichiers ni les paramètres déjà appliqués.

Référence technique : [dynamic debug du noyau Linux](https://docs.kernel.org/admin-guide/dynamic-debug-howto.html).
