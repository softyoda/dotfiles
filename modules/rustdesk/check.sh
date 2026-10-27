#!/usr/bin/env bash
conf="${XDG_CONFIG_HOME:-$HOME/.config}/rustdesk"
systemctl -q is-enabled rustdesk.service &&
grep -qx "allow-linux-headless = 'Y'" "$conf/RustDesk2.toml" &&
grep -qx "verification-method = 'use-permanent-password'" "$conf/RustDesk2.toml" &&
grep -qx "enable-check-update = 'N'" "$conf/RustDesk_local.toml"
