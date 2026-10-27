#!/usr/bin/env bash
set -euo pipefail
source "$DOTFILES_LIB"
need_vars DISKOVER_PATHS

# Sources de Diskover Community (révision épinglée) ; compose.yaml et les wrappers sont déployés par le module
DIR="$HOME/.local/opt/diskover-community"
REV=c2ba335880e96fc26300db496ee69193ad349678
if [[ ! -d $DIR/.git ]]; then
    mkdir -p "$DIR"
    git -C "$DIR" init -q
    git -C "$DIR" remote add origin https://github.com/diskoverdata/diskover-community.git
fi
git -C "$DIR" fetch -q --depth 1 origin "$REV"
git -C "$DIR" -c advice.detachedHead=false checkout -q "$REV" 2>/dev/null || \
    git -C "$DIR" -c advice.detachedHead=false checkout -q FETCH_HEAD

ensure_groups docker
enable_system docker.service
mkdir -p "$HOME/.local/share/diskover/config/scan-logs"
enable_user diskover-scan.timer
success "Diskover prêt : « diskover start » (Docker requis, groupe docker : reconnexion) puis http://localhost:8000"
