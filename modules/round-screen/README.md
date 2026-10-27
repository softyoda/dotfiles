# Écran rond (Waveshare 5" 1080×1080)

Le cadre visible est le cercle inscrit : les coins du carré 1080×1080 n'existent pas.

- **Échelle 150 %** (`ROUND_SCALE`) : ~5" à 1080 px, sinon tout est minuscule.
- **Barres en arc** : conteneur Plasma `org.softyoda.arcpanel`, fond courbe et icônes orientées vers le centre.
- **Haut** : son, réseau, heure, périphériques, luminosité.
- **Dock en bas** : menu, applis ouvertes, notifications et icônes d’applications.
  Espacements réguliers, séparateurs radiaux et traits d’état courbes côté intérieur :
  long accentué = active, court accentué = ouverte, court gris et icône estompée = réduite.
- Restauration : `dotctl apply round-screen` dans la session Plasma de la machine cible.
  Le module installe le conteneur, recrée les panneaux de l’écran rond puis relance Plasma
  pour configurer la zone de notification. Les autres écrans conservent leurs panneaux.
- **Script KWin `round-safe-area`** : sur la sortie carrée, chaque appli occupe le carré inscrit
  (côté = d/√2), façon Android ; les dialogues y sont centrés. Plein écran (vidéo, jeux) non touché.
  Réglages dans `kwinrc` `[Script-round-safe-area]` : `Inset` (0.7071), `AndroidMode`,
  `ConstrainFullscreen`, `OutputName`.
- Aperçu à distance : `spectacle -b -n -f -o /tmp/round.png` puis `tools/preview.py` (masque du cercle).

## Limites connues

- **Curseur** : Wayland/KWin n'offre pas de « barrière » de pointeur ; il peut entrer dans les coins
  invisibles (sans conséquence : aucune fenêtre n'y est).
- **Overscan** non pris en charge par le pilote NVIDIA (resterait la solution la plus simple).
- **Tactile** : le contrôleur USB de l'écran n'énumère plus (testé : 3 câbles data, 2 PC).
  Une fois revenu : Configuration → Écran tactile → associer à cette sortie.

Revenir en arrière : supprimer les barres, restaurer `plasma-org.kde.plasma.desktop-appletsrc.bak-avant-rond`,
`kwriteconfig6 --file kwinrc --group Plugins --key round-safe-areaEnabled false`.

Les essais de projection sur captures de terminal ne font pas partie de cette configuration validée.
