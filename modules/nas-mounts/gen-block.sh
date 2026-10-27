#!/usr/bin/env bash
# Affiche le bloc /etc/fstab géré par le module, à partir des variables du profil :
#   NAS_HOST            ex. truenas.local
#   NAS_SMB_SHARES      "partage:point_de_montage …"   ex. "imported_disks:/mnt/nas qbittorrent:/mnt/qbittorrent"
#   NAS_IMMICH_MOUNTS   yes → ajoute les exports NFS de NAS_IMMICH_EXPORTS
#   NAS_IMMICH_EXPORTS  "export:point_de_montage[:ro] …"
set -euo pipefail

: "${NAS_HOST:?NAS_HOST manquant}" "${NAS_SMB_SHARES:?NAS_SMB_SHARES manquant}"
uid=$(id -u) gid=$(id -g)
smb_opts="credentials=$HOME/.smbcredentials-nas,uid=$uid,gid=$gid,file_mode=0664,dir_mode=0775,iocharset=utf8,vers=3.0,nofail,_netdev,x-systemd.automount"
nfs_opts="nofail,_netdev,soft,timeo=30,x-systemd.automount"

echo "# >>> dotfiles nas-mounts (généré par le module nas-mounts — ne pas modifier à la main)"
for e in $NAS_SMB_SHARES; do
    share="${e%%:*}" mnt="${e#*:}"
    echo "//$NAS_HOST/$share $mnt cifs $smb_opts 0 0"
done
if [[ "${NAS_IMMICH_MOUNTS:-no}" == yes ]]; then
    : "${NAS_IMMICH_EXPORTS:?NAS_IMMICH_MOUNTS=yes mais NAS_IMMICH_EXPORTS manquant}"
    for e in $NAS_IMMICH_EXPORTS; do
        IFS=: read -r export mnt mode <<<"$e"
        [[ "${mode:-}" == ro ]] && opts="ro,$nfs_opts" || opts="defaults,$nfs_opts"
        echo "$NAS_HOST:$export $mnt nfs $opts 0 0"
    done
fi
echo "# <<< dotfiles nas-mounts"
