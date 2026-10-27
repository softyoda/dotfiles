#!/usr/bin/env bash
[[ -f /opt/docker/immich-worker/.env ]] && systemctl is-enabled immich-worker.service &>/dev/null
