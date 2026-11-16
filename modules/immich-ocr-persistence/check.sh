#!/usr/bin/env bash
[[ -s "$HOME/.config/immich-update/config.json" ]] &&
systemctl --user is-enabled --quiet immich-worker-align.timer
