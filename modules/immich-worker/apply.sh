#!/usr/bin/env bash
set -euo pipefail
source "$DOTFILES_LIB"
need_vars IMMICH_URL IMMICH_NAS_HOST IMMICH_DB_USERNAME IMMICH_DB_PASSWORD

STACK=/opt/docker/immich-worker
OLD=/opt/docker/immich-ml          # ancienne stack (avant le module)
as_root chown "$USER:$USER" "$STACK"

# IP de cette machine sur le LAN du NAS (le serveur Immich l'appelle sur :3003)
ip=${IMMICH_WORKER_IP:-$(ip -4 route get "$IMMICH_NAS_HOST" | grep -oP 'src \K\S+')}

# Version : on garde celle déjà en place ; sinon on prend celle du serveur
envget() { grep -oP "^$1=\K.*" "$2" 2>/dev/null || true; }
ver=$(envget IMMICH_VERSION "$STACK/.env")
[[ -n $ver ]] || ver=$(envget IMMICH_VERSION "$OLD/.env")
[[ -n $ver ]] || ver=$(curl -fsS "$IMMICH_URL/api/server/version" |
                       python3 -c 'import json,sys; print("v%(major)s.%(minor)s.%(patch)s" % json.load(sys.stdin))')

files=$STACK/docker-compose.yml suffix=""
if [[ ${IMMICH_ML_ACCEL:-cuda} == cuda ]]; then files+=":$STACK/docker-compose.ml-cuda.yml"; suffix=-cuda; fi

umask 077
cat > "$STACK/.env" <<ENV
# Généré par dotctl (module immich-worker) — ne pas committer
COMPOSE_FILE=$files
IMMICH_VERSION=$ver
ML_IMAGE_SUFFIX=$suffix
WORKER_BIND_IP=$ip
NAS_DB_HOST=$IMMICH_NAS_HOST
DB_USERNAME=$IMMICH_DB_USERNAME
DB_PASSWORD=$IMMICH_DB_PASSWORD
DB_DATABASE_NAME=${IMMICH_DB_NAME:-immich}
IMMICH_URL=$IMMICH_URL
IMMICH_API_KEY=${IMMICH_API_KEY:-}
IMMICH_NAS_SSH=${IMMICH_NAS_SSH:-nas}
IMMICH_NAS_DIR=${IMMICH_NAS_DIR:-/mnt/Uqbar/docker/immich}
ENV
umask 022
success "config $STACK/.env (version $ver, ML ${IMMICH_ML_ACCEL:-cuda}, écoute $ip:3003)"

# Migration depuis l'ancienne stack immich-ml (mêmes conteneurs)
if [[ -d $OLD ]]; then
    if systemctl is-enabled immich-ml.service &>/dev/null; then
        as_root systemctl disable --now immich-ml.service
        info "ancien service immich-ml.service désactivé"
    fi
    docker compose --project-directory "$OLD" down 2>/dev/null || as_root docker compose --project-directory "$OLD" down || true
    if [[ -d $OLD/cache && ! -d $STACK/cache ]]; then
        as_root cp -a "$OLD/cache" "$STACK/cache" && info "cache des modèles ML repris"
    fi
    [[ -f ~/.config/autostart/immich-ml-tray.desktop ]] &&
        mv ~/.config/autostart/immich-ml-tray.desktop ~/.config/autostart/immich-ml-tray.desktop.disabled
fi

as_root systemctl daemon-reload
as_root systemctl enable immich-worker.service
info "téléchargement des images Immich $ver$suffix…"
dc() { if id -nG | grep -qw docker; then docker compose --project-directory "$STACK" "$@"; else as_root docker compose --project-directory "$STACK" "$@"; fi; }
dc pull
as_root systemctl restart immich-worker.service
success "worker démarré — vérifier avec : immich-worker status"
echo
warn "Côté NAS (une fois) : voir modules/immich-worker/README.md § « Côté NAS »"
