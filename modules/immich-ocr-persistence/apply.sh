#!/usr/bin/env bash
set -euo pipefail
source "$DOTFILES_LIB"
need_vars IMMICH_UPDATE_LOCAL_STACK IMMICH_UPDATE_NAS_STACK IMMICH_UPDATE_NAS_SSH IMMICH_UPDATE_SERVER_URL IMMICH_UPDATE_WORKER_PING IMMICH_UPDATE_DOCKGE_STACK IMMICH_UPDATE_DOCKGE_HOST_STACK
python3 - <<'PY'
import json, os
from pathlib import Path
p = Path.home() / '.config/immich-update/config.json'
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(json.dumps({
    'local_stack': os.environ['IMMICH_UPDATE_LOCAL_STACK'],
    'nas_stack': os.environ['IMMICH_UPDATE_NAS_STACK'],
    'nas_ssh': os.environ['IMMICH_UPDATE_NAS_SSH'],
    'server_url': os.environ['IMMICH_UPDATE_SERVER_URL'].rstrip('/'),
    'worker_ping': os.environ['IMMICH_UPDATE_WORKER_PING'],
    'dockge_stack': os.environ['IMMICH_UPDATE_DOCKGE_STACK'],
    'dockge_host_stack': os.environ['IMMICH_UPDATE_DOCKGE_HOST_STACK'],
}, indent=2) + '\n')
p.chmod(0o600)
PY
python3 "$HOME/.local/share/immich-ocr/install-worker.py"
"$HOME/.local/bin/immich-ocr-hook"
install -m 644 "$HOME/.local/share/immich-ocr/immich-update.desktop" "$HOME/.local/share/applications/immich-update.desktop"
update-desktop-database "$HOME/.local/share/applications"
desktop=$(xdg-user-dir DESKTOP)
install -m 755 "$HOME/.local/share/applications/immich-update.desktop" "$desktop/Mettre à jour Immich.desktop"
systemctl --user daemon-reload
systemctl --user enable --now immich-worker-align.timer
