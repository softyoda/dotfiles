#!/usr/bin/env bash
id -nG | tr ' ' '\n' | grep -qx input &&
[[ -e $HOME/.config/autostart/libinput-gestures.desktop ]]
