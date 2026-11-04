#!/usr/bin/env bash
set -e
[[ -s "$HOME/.config/file-catalog/agent.key" ]]
systemctl --user is-enabled --quiet file-catalog-agent.timer
