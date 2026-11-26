#!/usr/bin/env bash
set -euo pipefail
source "$DOTFILES_LIB"

as_root udevadm control --reload-rules
as_root udevadm trigger --action=add --subsystem-match=tty --property-match="ID_PATH=$PANASONIC_CEC_USB_PATH"
udevadm settle --timeout=10
systemctl --user daemon-reload
if systemctl --user is-active --quiet graphical-session.target; then
    systemctl --user restart panasonic-cec.service
fi
