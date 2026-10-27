# Écran rond (Waveshare 5" 1080×1080)

Le cadre visible est le cercle inscrit : les coins du carré 1080×1080 n'existent pas.

- **Échelle 150 %** (`ROUND_SCALE`) : ~5" à 1080 px, sinon tout est minuscule.
- **Barre du haut** épaisse et non flottante, ajustée au contenu et centrée : l'épaisseur pousse
  les éléments dans la partie large de l'arc. Ordre : liste des fenêtres · menu (au centre, là où
  l'arc est le plus haut) · heure (taille fixe) · notifications (clé USB, réseau, son…).
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
