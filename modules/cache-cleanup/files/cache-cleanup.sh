#!/usr/bin/env bash
# Daily cache cleanup: removes cached package files older than 7 days.
# Managed by systemd/system/cache-cleanup.timer
set -u

AGE_DAYS=7
PACMAN_CACHE="/var/cache/pacman/pkg"

echo "[cache-cleanup] $(date -Is) starting (age > ${AGE_DAYS} days)"

# 1. pacman package cache: drop package files older than a week
if [ -d "$PACMAN_CACHE" ]; then
    find "$PACMAN_CACHE" -maxdepth 1 -type f -name '*.pkg.tar.*' -mtime +${AGE_DAYS} -print -delete
    # stale interrupted-download temp dirs
    find "$PACMAN_CACHE" -maxdepth 1 -type d -name 'download-*' -mtime +${AGE_DAYS} -exec rm -rf {} +
fi

# 2. paru AUR clone caches (runs as root via systemd: scan every user home)
#    built packages + downloaded source archives older than a week
for clone in /root/.cache/paru/clone /home/*/.cache/paru/clone; do
    [ -d "$clone" ] || continue
    find "$clone" -type f \
        \( -name '*.pkg.tar.*' \
        -o -name '*.tar.xz' -o -name '*.tar.gz' -o -name '*.tar.bz2' -o -name '*.tar.zst' \
        -o -name '*.zip' -o -name '*.AppImage' -o -name '*.deb' \) \
        -mtime +${AGE_DAYS} -print -delete
done

echo "[cache-cleanup] $(date -Is) done"
