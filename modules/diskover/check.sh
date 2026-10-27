#!/usr/bin/env bash
[[ -d $HOME/.local/opt/diskover-community/diskover ]] &&
systemctl --user is-enabled diskover-scan.timer &>/dev/null
