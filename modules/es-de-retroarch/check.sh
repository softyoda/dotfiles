#!/usr/bin/env bash
compgen -G "$HOME/Applications/ES-DE_x64*.AppImage" >/dev/null &&
[[ -d $HOME/ES-DE/themes/aura-es-de/.git ]] &&
[[ -f $HOME/ES-DE/settings/retroarch-autoconfig/xinput/Xbox_360_Wireless_Receiver.cfg || -d $HOME/ES-DE/settings/retroarch-autoconfig/sdl2 ]] &&
grep -q '^menu_driver = "xmb"' "$HOME/.config/retroarch/retroarch.cfg" &&
grep -q '^menu_swap_ok_cancel_buttons = "true"' "$HOME/.config/retroarch/retroarch.cfg"
