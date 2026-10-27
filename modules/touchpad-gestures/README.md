# Gestes du pavé tactile

Surtout utile sur **portable** : sur un poste fixe sans pavé tactile, le module est inutile.

- `libinput-gestures` (AUR) lit les gestes via libinput ; il exige l'appartenance au groupe `input`
  (ajouté par `apply.sh`, reconnexion nécessaire).
- `libinput-gestures-setup autostart` crée `~/.config/autostart/libinput-gestures.desktop`.
- Les gestes déclenchent des raccourcis KWin via `qdbus` (`Expose`, `ShowDesktopGrid`, bureaux virtuels…) ou `xdotool` (Alt+←/→).
- Configuration : `~/.config/libinput-gestures.conf` ; `libinput-gestures-setup restart` pour recharger.
