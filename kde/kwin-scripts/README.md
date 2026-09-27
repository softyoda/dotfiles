# Snap Assist

`org.kde.snapassist` ajoute des miniatures cliquables pour placer une autre fenêtre dans la zone libre après un placement sur un bord ou un coin de l'écran. Installation pour Plasma 6 / Wayland, sans privilèges administrateur :

```sh
bash scripts/setup-snap-assist.sh
```

La restauration KDE (`scripts/kde-restore.sh`, y compris le bouton de restauration de l'installateur graphique) l'installe automatiquement. L'extension est aussi activée aux ouvertures de session suivantes.

Source : https://github.com/RoccoRakete/plasma-snap-assist
Version intégrée : `7f00e2f0c81b8e04f5cd9adf46ab7c55d1df7b55`.
Licence : GPL-2.0-or-later, fournie avec les sources.
Modification locale : les notifications de diagnostic sont désactivées par défaut (`DebugNotifications=false`). L'effet d'animation supplémentaire n'est pas installé.

Pour les demi-écrans, le choix remplit la moitié opposée. Pour les quarts, cette version propose le quart diagonalement opposé, pas un remplissage successif des trois quarts restants.

Tests de géométrie et de disposition :

```sh
QT_QPA_PLATFORM=offscreen /usr/lib/qt6/bin/qmltestrunner \
  -input kde/kwin-scripts/org.kde.snapassist/tests
```

Désactivation : décocher Snap Assist dans Configuration du système → Gestion des fenêtres → Scripts KWin.
