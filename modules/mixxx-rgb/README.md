# Mixxx « rgb »

Build maison de **Mixxx 2.5.6** installé dans `~/.local/opt/mixxx-rgb` (le Mixxx
du dépôt Arch reste utilisable à côté). Le module télécharge l'archive officielle
(somme SHA-256 vérifiée), applique `files/mixxx-rgb.patch`, compile avec les
mêmes options CMake que le build d'origine et installe. Un fichier témoin
`~/.local/opt/mixxx-rgb/.stamp-<version>-<hash du patch>` évite de recompiler :
modifier le patch ou changer de version déclenche une nouvelle compilation.

Pour mettre à jour le patch depuis une arborescence modifiée :
`diff -Nu` contre l'archive amont (chemins `a/…` / `b/…`, 9 fichiers).

## Ce que change le patch « rgb »

Objectif : des formes d'onde colorées proches de celles de Rekordbox.

- **Nouvelle fonction de couleur** (`src/waveform/rgbreference.h`) : les trois
  bandes (graves, médiums, aigus) sont normalisées sur la plus forte, puis
  corrigées (réduction du rouge/vert quand les aigus sont faibles, atténuation
  du vert, aigus ×1,3). Utilisée par les rendus RGB logiciel et OpenGL
  (shader `rgbsignal.frag`) et par la vue d'ensemble (`woverview.cpp`).
- **Analyse** (`analyzerwaveform.*`) : filtres biquad maison à la place des
  Bessel 4 pôles (graves < 100 Hz, médiums 300 Hz–3 kHz, aigus > 1,5 kHz),
  résolution de la forme d'onde principale 441 → 1000 échantillons/s, signaux
  graves/médiums conservés linéaires (pas de compression par puissance).
- **Rendu** (`waveformrendererrgb.cpp`) : fenêtres de crêtes temporelles
  (graves ±12 ms, médiums ±1 ms) et gain d'affichage indépendant du trim
  et du ReplayGain.
- **Version de forme d'onde** (`waveformfactory.h`) : nouveaux identifiants
  `Waveform-RGBReference-1`, donc les pistes sont ré-analysées au premier
  chargement (les anciennes formes d'onde du cache ne sont pas réutilisées).
- **Alias de contrôle** (`enginebuffer.cpp`) : `[ChannelN],play_alternate`
  est un alias de `play`, utilisé par les raccourcis perso.

## Autres fichiers

- `Custom.kbd.cfg` : raccourcis clavier perso (`~/.mixxx/`).
- `effects.xml` : racks d'effets (`~/.mixxx/`).
- `org.mixxx.Mixxx.desktop` : lanceur forçant XWayland (`QT_QPA_PLATFORM=xcb`,
  `QT_XCB_GL_INTEGRATION=xcb_glx`) vers le build rgb.
- `spacealias.cpp/.json` : plugin Qt « generic » qui convertit la touche Espace
  en touche D (hors champs de saisie et dialogues). Compilé dans
  `~/.local/lib/mixxx-space-alias/generic/`. Pour l'activer, lancer Mixxx avec
  `QT_PLUGIN_PATH=~/.local/lib/mixxx-space-alias QT_QPA_GENERIC_PLUGINS=mixxxspacealias`
  (non câblé dans le `.desktop` actuel).
- Contrôleur Pioneer DDJ-400 : mapping d'origine de Mixxx, rien à installer.
- Non versionné : `mixxxdb.sqlite` (bibliothèque musicale) et `mixxx.cfg`.
