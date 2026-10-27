# Terminaux

## WezTerm — `~/.config/wezterm/wezterm.lua`

Thème Tokyo Night, police JetBrains Mono 12, fond légèrement transparent, barre d'onglets
masquée s'il n'y a qu'un onglet, fermeture sans confirmation, 10 000 lignes d'historique.
Souris : la sélection est copiée automatiquement, clic droit = coller.

Sous Wayland, WezTerm peut planter (bug DRM syncobj) : l'alias fish
`wezterm` → `WAYLAND_DISPLAY= /usr/bin/wezterm` (module `fish-shell`) le force en XWayland.

## Konsole — `~/.local/share/konsole/Default.profile`

Copie automatique de la sélection, collage au clic du milieu, 100 000 lignes d'historique.

Pour en faire le profil par défaut : Konsole → Configuration → Gérer les profils →
« Default » → Définir par défaut (écrit `DefaultProfile=Default.profile` dans `konsolerc`).
