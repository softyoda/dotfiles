# Montage automatique des disques NTFS

Deux pièces :

1. **KDE** monte les supports amovibles au branchement et à la connexion
   (`kded_device_automounterrc` → `AutomountEnabled/OnLogin/OnPlugin=true`, réglable dans
   Paramètres → Disques et périphériques → Montage automatique).
2. **udisks2** choisit le pilote et les options : `/etc/udisks2/mount_options.conf`.

```ini
[defaults]
ntfs_drivers=ntfs3,ntfs
ntfs:ntfs3_defaults=uid=$UID,gid=$GID,windows_names
ntfs:ntfs_defaults=uid=$UID,gid=$GID,windows_names
```

- Syntaxe udisks2 ≥ 2.10 : `<signature>[:<pilote>]_<clé>`. La signature `ntfs` est celle
  vue par `blkid` ; le pilote est le type passé à `mount`. `_defaults` = options appliquées
  d'office, `_allow` = options qu'un utilisateur *peut* demander en plus, `_drivers` =
  ordre d'essai des pilotes. `$UID`/`$GID` sont remplacés par udisks2 par l'utilisateur
  qui monte.
- `ntfs3` (pilote noyau, rapide) est essayé d'abord, puis `ntfs` : sur Arch,
  `/usr/bin/mount.ntfs` est un lien vers **ntfs-3g** (FUSE), qui sait monter certains
  volumes que ntfs3 refuse.
- `uid=$UID,gid=$GID` : les fichiers appartiennent à l'utilisateur (NTFS n'a pas de
  droits Unix) ; `windows_names` : refuse de créer des noms invalides sous Windows
  (`:`, `?`, `*`, `CON`…), pour que le disque reste lisible sous Windows.
- Les listes `_allow` intégrées à udisks2 ne sont pas redéfinies : elles autorisent déjà
  ces options.

L'ancien fichier de ryzen mettait des *valeurs* (`uid=1000`, `umask=0022`, en double…)
dans `ntfs:lowntfs-3g_allow` — une liste d'options *autorisées*, pas appliquées — pour un
pilote `lowntfs-3g` qui n'était jamais essayé : il n'avait aucun effet.

## Disque refusé / en lecture seule

Un volume NTFS « sale » (Windows en démarrage rapide/hibernation, débranchement brutal)
est refusé par ntfs3 et monté en lecture seule (ou refusé) par ntfs-3g. Solution : sous
Windows, désactiver le démarrage rapide et faire un arrêt complet, ou en dernier recours
`sudo ntfsfix -d /dev/sdX1`.

Vérifier les options utilisées : `findmnt -t ntfs3,fuseblk`.
