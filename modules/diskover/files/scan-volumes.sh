#!/usr/bin/env bash
set -uo pipefail
exec 9>/config/scan-logs/all.lock
flock -n 9 || { echo 'Un scan est déjà en cours.'; exit 0; }
last=/config/scan-logs/last-scan-start
if [ "${1:-}" = '--weekly' ] && [ -f "$last" ]; then
  elapsed=$(( $(date +%s) - $(stat -c %Y "$last") ))
  if [ "$elapsed" -lt 604800 ]; then echo 'Dernier scan lancé il y a moins de 7 jours : scan automatique ignoré.'; exit 0; fi
fi
for path in /scan/linux/home/${USER} /scan/intel /scan/truenas /scan/truenas-qbittorrent /scan/truenas-immich-uploads /scan/truenas-immich-thumbs; do
  timeout 20 stat "$path/." >/dev/null || exit 1
done
touch "$last"
printf '%s START diskover-tout\n' "$(date -Iseconds)"
python3 /app/diskover/diskover.py --threads=6 --indexthreads=2 -f -i diskover-tout /scan >/config/scan-logs/tout.log 2>&1
result=$?
printf '%s END diskover-tout exit=%s\n' "$(date -Iseconds)" "$result"
if [ "$result" = 64 ]; then
  echo 'Scan terminé avec avertissements : consulter tout.log pour les chemins ignorés.'
  exit 0
fi
exit "$result"
