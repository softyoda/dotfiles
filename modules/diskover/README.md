# Diskover Community

Catalogue de fichiers interrogeable (Elasticsearch + interface web) dans Docker, lié à `127.0.0.1:8000`.
Basé sur l'image LinuxServer `lscr.io/linuxserver/diskover`.

## Contenu

| Élément | Rôle |
|---|---|
| `~/.local/bin/diskover` | commande : `open`, `start`, `stop`, `status`, `logs`, `rescan`, `scan-status`, `scan DOSSIER diskover-NOM` |
| `~/.local/opt/diskover-community/compose.yaml` | services Diskover + Elasticsearch (sources du projet clonées par `apply.sh`, révision épinglée) |
| `~/.local/share/diskover/config/scan-volumes.sh` | scan commun `diskover-tout` lancé dans le conteneur |
| `diskover-scan.service` / `.timer` | rescan hebdomadaire (dimanche 04:00, rattrapage si PC éteint) |
| `diskover.desktop` | lanceur dans le menu |

## Variable `DISKOVER_PATHS`

Liste (séparée par des espaces) des points de montage qui doivent être montés avant un rescan ; la commande refuse de scanner si l'un manque.
Sur ryzen : `/run/media/ryzen/SSD_INTEL /mnt/nas /mnt/qbittorrent /mnt/immich-uploads /mnt/immich-thumbs`.

## À adapter sur une autre machine

- `compose.yaml` monte ces chemins en lecture seule sous `/scan/…` (SSD_INTEL, NAS, qBittorrent, Immich). Retirer ou adapter les lignes inutiles, ainsi que la boucle de vérification dans `scan-volumes.sh`.
- Premier démarrage : `diskover start`, puis dans l'interface Settings → Indices → Reload indices → sélectionner `diskover-tout`.
- Le groupe `docker` est ajouté par `apply.sh` (reconnexion nécessaire).
