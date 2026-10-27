# Économiseur d'écran rétro

XScreenSaver 6.x : veille animée après 3 min (cycle 1 min), sans verrouillage ni DPMS.
Aucun fond de bureau n'est modifié.

| Élément | Rôle |
|---|---|
| `~/.xscreensaver` | animations retenues et délais (réglables via « Économiseur rétro — animations et délais ») |
| `retro-screensaver.service` | lance `xscreensaver` avec la session graphique |
| `~/.config/autostart/retro-screensaver.desktop` | volontairement `Hidden=true` (le service le remplace) |
| `guard.py` + `retro-saver-guard.service` | service D-Bus `local.RetroSaver` : désactive l'économiseur pendant GameMode, une lecture MPRIS en cours ou le plein écran |
| script KWin `local-retro-guard` | signale à `guard.py` qu'une fenêtre est en plein écran |
| `preferences.conf` | `protect=true|false` : active/désactive la protection |
| `plugin/` | sources du plugin Plasma (menu clic droit du bureau) ; compilé par `apply.sh` via `plugin/build.sh` |
| `retro-menu.conf` | drop-in de `plasma-plasmashell.service` : ajoute `QT_PLUGIN_PATH` pour charger le plugin |
| `powerdevilrc` | inhibitions génériques de KeepAwake bloquées, sinon l'économiseur ne se déclenche jamais |

## Après application

- Redémarrer le shell : `systemctl --user restart plasma-plasmashell.service`.
- Brancher le menu sur le bureau (clic droit sur le bureau → configurer → actions de la souris) : choisir le plugin « local.retro.contextmenu ». (sur cette machine, le bouton droit utilise actuellement le menu KDE d'origine `org.kde.contextmenu`.)
- La protection pendant jeux/films est à valider dans les applis réellement utilisées.
