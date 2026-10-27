#!/usr/bin/env bash
set -euo pipefail
source "$DOTFILES_LIB"
grep -q nvidia-container-runtime /etc/docker/daemon.json 2>/dev/null ||
    as_root nvidia-ctk runtime configure --runtime=docker
enable_system docker.service
ensure_groups docker
success "docker prêt (GPU : docker run --rm --gpus all ubuntu nvidia-smi)"
