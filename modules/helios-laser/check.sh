#!/usr/bin/env bash
[[ -f /usr/local/lib/libHeliosDacAPI.so ]] &&
systemctl --user -q is-enabled helios-bridge.service
