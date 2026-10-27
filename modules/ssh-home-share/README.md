# Partage du dossier personnel par SSH — côté serveur

À appliquer sur la machine dont on veut atteindre le dossier personnel depuis les autres PC
(ex. `flystation` après sa réinstallation CachyOS). Les clients utilisent le module
**`remote-workstation`** (montage sshfs dans `~/Mounts/<nom>` + Dolphin).

## Ce que fait le module

- installe `openssh`, `avahi`, `nss-mdns` ;
- `/etc/ssh/sshd_config.d/10-dotfiles.conf` : `PasswordAuthentication no`,
  `KbdInteractiveAuthentication no`, `PermitRootLogin no` → connexion par clé uniquement ;
- ajoute à `~/.ssh/authorized_keys` les clés publiques du fichier `SHARE_AUTHORIZED_KEYS_FILE`
  (sans doublon ; refuse un fichier contenant une clé privée) ;
- vérifie la config (`sshd -t`), active `sshd` ;
- mDNS : active `avahi-daemon` et ajoute `mdns_minimal [NOTFOUND=return]` à la ligne `hosts:` de
  `/etc/nsswitch.conf` (une seule fois) → la machine répond au nom `<hôte>.local` ;
- si `ufw` est actif : `ufw allow ssh`.

## Variable (profil privé de la machine serveur)

```toml
[vars]
SHARE_AUTHORIZED_KEYS_FILE = "ssh/authorized_keys.pub"   # relatif au repo privé, ou chemin absolu / ~/…
```

Le fichier ne contient **que des clés publiques** (`~/.ssh/<clé>.pub` de chaque client), une par ligne.

## ⚠ Avant d’appliquer

Les mots de passe SSH sont désactivés : vérifier que le fichier contient bien la clé publique
de chaque client. Ensuite `ssh-copy-id` ne fonctionne plus (mot de passe refusé) : pour un nouveau
client, ajouter sa clé publique au fichier du repo privé et réappliquer le module sur le serveur.

## Vérifier

```fish
systemctl status sshd avahi-daemon
avahi-resolve -n (hostname).local
```
