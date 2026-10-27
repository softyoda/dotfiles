#!/usr/bin/env bash
[[ -f $HOME/.local/lib/qt6/plugins/plasma/containmentactions/local.retro.contextmenu.so ]] &&
[[ $(kreadconfig6 --file kwinrc --group Plugins --key local-retro-guardEnabled) == true ]] &&
[[ $(kreadconfig6 --file powerdevilrc --group Inhibitions --key BlockedInhibitions) == *keepawake-rs* ]] &&
systemctl --user is-enabled retro-screensaver.service retro-saver-guard.service &>/dev/null
