#!/usr/bin/env bash
# logind gère le bouton hors session ; dans Plasma, powerdevil a la main.
source "$DOTFILES_LIB"
kwriteconfig6 --file powerdevilrc --group AC --group SuspendAndShutdown --key PowerButtonAction 8
kwriteconfig6 --file kglobalshortcutsrc --group ksmserver --key "Halt Without Confirmation" "Power Off,none,Éteindre sans confirmation"
kwriteconfig6 --file kglobalshortcutsrc --group org_kde_powerdevil --key PowerOff "none,Power Off,Éteindre"
success "bouton power → extinction (effectif après reconnexion ; logind après reboot)"
