# Machines distantes (SSHFS) — côté client

Accès simple au dossier personnel d’autres machines du réseau (ex. la station de calcul
`flystation`) depuis ce PC : il apparaît dans `~/Mounts/<nom>` et dans les Emplacements de
Dolphin. Côté serveur, appliquer le module **`ssh-home-share`** sur chaque machine partagée.

Les deux modules sont complémentaires : toute machine peut être à la fois client
(`remote-workstation`) et serveur (`ssh-home-share`).

## Variables (profil privé)

```toml
[vars]
REMOTE_WORKSTATIONS = "flystation=yoann@flystation.local"   # plusieurs : séparées par des espaces
REMOTE_WS_KEY = "~/.ssh/flystation"                          # générée (ed25519) si absente
# Optionnel : chemin distant autre que /home/<user> → "nom=user@hôte:/chemin"
# Optionnel : lanceur « Whisper Diarization Watch »
REMOTE_WS_WHISPER = "flystation:/home/yoann/Workspace/whisper-diarization/watchfolder.sh"
```

## Ce que fait le module

- génère la clé `REMOTE_WS_KEY` si elle n’existe pas ;
- ajoute `user_allow_other` à `/etc/fuse.conf` (option sshfs `allow_other`) ;
- pour chaque machine : `~/.config/remote-workstations/<nom>.conf`, le point de montage
  `~/Mounts/<nom>`, et active `remote-ws-mount@<nom>.service` (unité utilisateur générique) :
  - ping préalable : rien n’est monté tant que la machine ne répond pas ;
  - `reconnect,ServerAliveInterval=15,ServerAliveCountMax=3` : une machine en veille ou partie
    est détectée en ~45 s et le montage est retiré (Dolphin ne reste pas figé) ;
  - `Restart=always` toutes les 20 s, sans limite : le montage revient tout seul au réveil ;
- ajoute un raccourci `<nom>` dans les Emplacements de Dolphin (`~/.local/share/user-places.xbel` ;
  fermer Dolphin avant d’appliquer, sinon il peut réécrire le fichier) ;
- `~/.local/bin/remote-ws-run` + menu Dolphin « Machine distante → Exécuter sur la machine
  distante (terminal / arrière-plan) » : lance un `.sh` ou un `.desktop` du montage **sur** la
  machine distante, via ssh ;
- optionnel : lanceur `<nom>-whisper-watch.desktop`.

Migration depuis l’ancienne config manuelle : `<nom>-mount.service`, l’unité
`home-…-Mounts-<nom>.mount` (redondante) et le menu `<nom>-run.desktop` sont désactivés et
renommés en `.bak-AAAAMMJJ`. `~/.local/bin/flystation-run.sh` peut être supprimé à la main.

## Étape manuelle (une fois par machine distante)

```fish
ssh-copy-id -i ~/.ssh/flystation.pub yoann@flystation.local
systemctl --user restart remote-ws-mount@flystation.service
```

`apply.sh` teste la connexion par clé et affiche la commande `ssh-copy-id` à lancer si besoin.
Résolution `*.local` : mDNS (avahi + nss-mdns, ou systemd-resolved).

## Dépannage

```fish
systemctl --user status remote-ws-mount@flystation.service
journalctl --user -u remote-ws-mount@flystation.service -e
```
