#!/usr/bin/env bash
# (la règle sudoers n'est pas lisible sans root : non vérifiée ici)
systemctl --user is-enabled -q hdmi-recovery.service &&
[[ $(kreadconfig6 --file kglobalshortcutsrc --group services --group hdmi-redetect.desktop --key _launch) == Alt+F9 ]]
