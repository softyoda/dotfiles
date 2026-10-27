#!/bin/bash
# worker-switch.sh (NAS) — le serveur Immich du NAS ne fait que l'API tant
# qu'AU MOINS UN worker GPU répond ; sinon il reprend les microservices lui-même.
# À lancer en cron toutes les 5 min sur le NAS (tâche TrueNAS « Cron Jobs »).
#
# WORKERS : liste « hôte:port » des workers (ML exposé sur 3003)
WORKERS="${WORKERS:?ex. WORKERS=\"pc-salon.local:3003 flystation.local:3003\"}"
COMPOSE_DIR="${COMPOSE_DIR:-/mnt/Uqbar/docker/immich}"
MODE_FILE=$COMPOSE_DIR/worker-mode.env
STATE_FILE=$COMPOSE_DIR/.worker-switch-failures
LOG_FILE=$COMPOSE_DIR/.worker-switch.log
GRACE=3   # nb de vérifications ratées avant que le NAS reprenne les jobs

current_mode() { grep -oP '(?<=IMMICH_WORKERS_INCLUDE=).*' "$MODE_FILE" 2>/dev/null || echo api; }
set_mode() {
    echo "IMMICH_WORKERS_INCLUDE=$1" > "$MODE_FILE"
    docker compose -f "$COMPOSE_DIR/docker-compose.yml" up -d --force-recreate immich-server >> "$LOG_FILE" 2>&1
    echo "[$(date '+%F %H:%M')] mode → $1" >> "$LOG_FILE"
}

alive=""
for w in $WORKERS; do
    nc -z -w3 "${w%:*}" "${w#*:}" 2>/dev/null && alive+="$w "
done

if [[ -n $alive ]]; then
    echo 0 > "$STATE_FILE"
    if [[ $(current_mode) != api ]]; then
        echo "[$(date '+%F %H:%M')] workers actifs : $alive→ api seule" >> "$LOG_FILE"
        set_mode api
    fi
else
    failures=$(( $(cat "$STATE_FILE" 2>/dev/null || echo 0) + 1 ))
    echo "$failures" > "$STATE_FILE"
    echo "[$(date '+%F %H:%M')] aucun worker (échec $failures/$GRACE)" >> "$LOG_FILE"
    if (( failures >= GRACE )) && [[ $(current_mode) != api,microservices ]]; then
        set_mode api,microservices
    fi
fi
