# Worker Immich (GPU)

Le NAS héberge Immich (API, base Postgres, Redis, stockage). Les jobs lourds —
miniatures, transcodage vidéo (NVENC), métadonnées, reconnaissance (CLIP, visages,
OCR) — tournent sur les PC équipés d'un GPU : ce module en fait un **worker**.

## Plusieurs workers allumés en même temps

Pas de conflit : chaque worker lance `immich-microservices`, qui pioche ses jobs
dans la **même file Redis** du NAS. Deux workers allumés = les jobs se répartissent
tout seuls. Aucun allumé = les jobs attendent ; au bout de 3 vérifications le NAS
reprend lui-même les microservices (script `nas/worker-switch.sh`).

Chaque worker utilise son propre conteneur ML (`IMMICH_MACHINE_LEARNING_URL`
local). Le serveur API du NAS, lui, a besoin d'un ML pour la recherche
intelligente : dans **Administration → Machine Learning → URL**, lister les
workers par ordre de préférence (ex. `http://pc-salon.local:3003`,
`http://flystation.local:3003`) ; Immich bascule sur le suivant si le premier
ne répond pas.

## Commande `immich-worker`

```
immich-worker status          # versions serveur / worker, conteneurs, jobs
immich-worker align           # met le worker à la version du serveur (rollback auto)
immich-worker check-update    # nouvelle release Immich ?
immich-worker upgrade-nas     # sauvegarde DB → MAJ du NAS → alignement du worker
immich-worker logs [ml|ms]
```

`upgrade-nas` :
1. `pg_dumpall` compressé dans le dossier compose du NAS (`db-backup-pre-<version>-<date>.sql.gz`) ;
2. `docker compose pull` de la nouvelle image **avant** toute bascule (rien ne change si le téléchargement échoue) ;
3. sauvegarde de `.env` (`.env.bak-<date>`), passage de `IMMICH_VERSION`, `up -d` ;
4. attente que l'API réponde dans la nouvelle version, puis `align` sur ce worker.
   `align` télécharge d'abord, bascule, attend le healthcheck et **revient à
   l'ancienne version** si le worker ne démarre pas.

Version majeure : la commande prévient et renvoie vers les notes de version.
L'icône de notification (`immich-worker-tray`) affiche l'état, notifie les
nouvelles versions et propose les mêmes actions.

## Variables

| Variable | Où | Exemple |
|---|---|---|
| `IMMICH_URL` | profil | `https://photos.example.org` |
| `IMMICH_NAS_HOST` | profil | IP du NAS (Postgres 5432 / Redis 6379 exposés sur le LAN) |
| `IMMICH_ML_ACCEL` | profil | `cuda` (défaut) ou `cpu` |
| `IMMICH_NAS_SSH`, `IMMICH_NAS_DIR` | profil | alias ssh du NAS, dossier compose |
| `IMMICH_DB_USERNAME`, `IMMICH_DB_PASSWORD`, `IMMICH_DB_NAME` | secrets | |
| `IMMICH_API_KEY` | secrets (optionnel) | clé admin, pour afficher les jobs |

## Côté NAS (une fois)

1. Exposer Postgres et Redis sur l'IP LAN du NAS (`ports: "<ip-nas>:5432:5432"` et `"<ip-nas>:6379:6379"`).
2. Dans le compose du NAS, la variable s'appelle **`IMMICH_MACHINE_LEARNING_URL`**
   (l'ancien nom `MACHINE_LEARNING_URL` est ignoré), ou mieux : régler la liste
   d'URL dans l'interface d'administration (voir plus haut).
3. Remplacer `scripts/worker-switch.sh` par `nas/worker-switch.sh` (liste `WORKERS`).

## Migration depuis l'ancienne stack `/opt/docker/immich-ml`

`apply.sh` désactive `immich-ml.service`, arrête l'ancienne stack, reprend le
cache des modèles et désactive l'ancien `immich-ml-tray`. Les anciens scripts de
stockage froid (VPS) restent dans `/opt/docker/immich-ml/scripts`, inutilisés.
