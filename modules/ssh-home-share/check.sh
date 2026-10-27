#!/usr/bin/env bash
systemctl is-enabled -q sshd 2>/dev/null &&
systemctl is-enabled -q avahi-daemon 2>/dev/null &&
grep -qE '^hosts:.*mdns' /etc/nsswitch.conf &&
grep -qE '^(ssh-|ecdsa-|sk-)' "$HOME/.ssh/authorized_keys" 2>/dev/null
