# Partages NAS (SMB/NFS)

Monte les partages du NAS TrueNAS via `/etc/fstab` en **automontage systemd**
(`x-systemd.automount,nofail,_netdev`) : rien ne bloque au démarrage si le NAS est absent,
le partage est monté au premier accès.

## Ce que fait le module

- `apply.sh` génère (`gen-block.sh`) un bloc entre `# >>> dotfiles nas-mounts` et
  `# <<< dotfiles nas-mounts` à la fin de `/etc/fstab` et le remplace à chaque application
  (sauvegarde `/etc/fstab.bak-AAAAMMJJ-HHMMSS` à chaque modification) ;
- hors du bloc, les lignes **strictement identiques** (aux espaces près) à une ligne du bloc sont
  retirées : ce sont les doublons de l’ancienne config manuelle. Les autres lignes (y compris les
  anciens commentaires « # NAS TrueNAS via SMB… ») ne sont jamais touchées — à nettoyer à la main
  si besoin ;
- crée les points de montage, `systemctl daemon-reload`, redémarre `remote-fs.target` ;
- `~/.smbcredentials-nas` (mode 600) à partir des secrets `NAS_SMB_USER` / `NAS_SMB_PASSWORD` ;
- `~/.local/bin/nas-mounter` + lanceur « Partages NAS » : fenêtre yad pour monter/démonter à la
  main ; la liste des partages est lue dans le bloc de `/etc/fstab`.
- `check.sh` vérifie que le bloc existe et correspond aux variables actuelles.

## Variables (profil privé)

```toml
[vars]
NAS_HOST = "truenas.local"
NAS_SMB_SHARES = "imported_disks:/mnt/nas qbittorrent:/mnt/qbittorrent"
# Optionnel : exports NFS Immich (utilisés par le worker Immich)
NAS_IMMICH_MOUNTS = "yes"
NAS_IMMICH_EXPORTS = "/mnt/Pool/immich/uploads:/mnt/immich-uploads /mnt/Pool/photos:/mnt/immich-photos:ro"
```

Format : `NAS_SMB_SHARES` = `partage:point_de_montage` séparés par des espaces ;
`NAS_IMMICH_EXPORTS` = `export:point_de_montage[:ro]`.

## Secrets (`~/.config/dotfiles/secrets.env`, jamais commité)

```sh
NAS_SMB_USER=…
NAS_SMB_PASSWORD=…
```

## Vérifier

```fish
ls /mnt/nas                       # déclenche le montage
systemctl list-units --type=automount
findmnt -t cifs,nfs,nfs4
```

## IPv6

Si `<nas>.local` se résout en IPv6 sur une machine (systemd-resolved avec mDNS), le NFS du NAS
peut refuser le montage (« incorrect mount option »). Mettre l'IPv4 du NAS dans `NAS_HOST`.
