#!/usr/bin/env bash
# plymouth-set-default-theme sans argument affiche le thème réellement utilisé
# (il retombe sur le thème par défaut si celui de plymouthd.conf est introuvable).
[[ "$(plymouth-set-default-theme 2>/dev/null)" == cogwheel-spinner ]]
