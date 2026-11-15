#!/usr/bin/env bash
set -euo pipefail
[[ -r /etc/modprobe.d/xone-event-traces.conf ]]
[[ -x /usr/local/libexec/xone-event-traces.py ]]
# File drift is checked by dotctl; current kernel flags require administrator access.
systemctl --user is-active -q diagnostic-manettes.service
