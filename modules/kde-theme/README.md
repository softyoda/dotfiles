# Thème KDE (We10XOS sombre)

Remplace l'ancien dossier `kde/` et les scripts `scripts/kde-backup.sh` /
`scripts/kde-restore.sh` : au lieu d'écraser des fichiers rc entiers, `apply.sh`
écrit les réglages **clé par clé** avec `kwriteconfig6`.

## Ce que fait le module

| Élément | Valeur | Origine |
|---|---|---|
| Thème global | `com.github.yeyushengfan258.We10XOS-dark` | téléchargé (git épinglé) |
| Thème Plasma | `We10XOS-dark` | téléchargé |
| Décoration | Aurorae `__aurorae__svg__We10XOS-dark` (moteur `org.kde.kwin.aurorae.v2`) | téléchargé |
| Couleurs | `We10XOSDark` + accent `104,107,111` (#686b6f) | `files/color-schemes/` (version locale retouchée) |
| Icônes | `We10X-black-dark` (+ Papirus en secours) | téléchargé / paquet `papirus-icon-theme` |
| Curseurs | `Win10OS-cursors`, taille 36 | téléchargé dans `~/.icons` |
| Splash | `Watch_Dogs_Theme` | `files/look-and-feel/` |
| Effets KWin | verre (`kwin-effects-glass-git`), flou 11 / bruit 4 / saturation 169, fenêtres molles (avancé : 14 / 5), atténuation des inactives, translucidité, secouer le curseur ×4, `kwin4_effect_geometry_change` ; aperçu et « kinetic maximize » désactivés | paquets + `files/kwin-effects/` |
| Tuilage | marge 4 px, disposition 25 / 50 / 25 | `kwinrc`, pour chaque écran connu |
| Coins actifs | `ElectricBorderCornerRatio=0.3` | |
| XWayland | échelle `$XWAYLAND_SCALE` | var (2 sur l'écran 4K) |
| Fond d'écran | applet « Blurred Wallpaper » (`a2n.blur`) en diaporama sur `$WALLPAPER_DIR`, 120 s, flou 50 | `plasma6-wallpapers-blurredwallpaper-git` |
| Verrouillage | pas de verrouillage automatique (l'économiseur rétro prend le relais) | `kscreenlockerrc` |
| Divers | animations ×0,25, police Noto Sans 10, `LANG=fr_FR.UTF-8` | |

Les dépôts téléchargés sont mis en cache dans `~/.cache/dotfiles/kde-theme/` :

- https://github.com/yeyushengfan258/We10XOS-kde (commit `270f0d7`)
- https://github.com/yeyushengfan258/We10X-icon-theme (commit `0f52ff2`, `./install.sh -t black`)
- https://github.com/yeyushengfan258/Win10OS-cursors (commit `79d13bb`)

Petits paquets versionnés dans `files/` :

- `look-and-feel/Watch_Dogs_Theme` — splash, https://github.com/ferretwithaberet/watch_dogs-kde-splash
- `kwin-effects/kwin4_effect_geometry_change` — version locale (différente de
  https://github.com/peterfajdiga/kwin4_effect_geometry_change)
- `plasmoids/org.kde.plasma.simplekickoff` — lanceur simple (GPL-2.0+), non utilisé par défaut
- `wallpapers/org.kde.plasma.citygrow` — fond animé, non utilisé par défaut

Thèmes CachyOS (Emerald, Iridescent, Nord) installés en paquets pour pouvoir
basculer depuis les Paramètres.

## Variables (profil privé)

- `WALLPAPER_DIR` — dossier du diaporama (`~` accepté), ex. `~/Dropbox/09_Illustrations/Wallpapers`
- `XWAYLAND_SCALE` — échelle des applis X11 (`2` en 4K, `1` sinon)

## Disposition du panneau (optionnel, manuel)

`plasma-org.kde.plasma.desktop-appletsrc` est propre à chaque machine (écrans,
activités, icônes du bureau) : il n'est **pas** appliqué automatiquement.
`layout/` contient une copie nettoyée (sans positions d'icônes, correspondances
d'écrans, identifiants d'activité ni fond d'écran) :

```bash
bash modules/kde-theme/layout/restore-layout.sh   # demande confirmation, sauvegarde l'ancien
```

Panneau en bas, non flottant, 46 px : lanceur, bureaux virtuels, tâches,
zone de notification, horloge, « réduire tout ».

## Non packagé (à installer à la main si besoin, via « Obtenir de nouveaux éléments »)

- Splashs inutilisés : AccretionDisk (115 Mo), FalloutPipBoy-Loading-Plasma6
  (https://github.com/LuMarans30/FalloutPipBoy-Loading-Plasma6), Illusion, Lain,
  MatrixCode, SimpleTuxSplash-Plasma6 — KDE Store.
- WhiteSur (https://github.com/vinceliuice/WhiteSur-kde), Layan, couleurs Sweet /
  SumacNightMoltenGlass — essais précédents.
- Applet météo `Minimal.chaac.weather` : https://github.com/zayronxio/Chaac.Minimal.Weather
- Effet `kwin6_effect_aura_glow` (Burn-My-Windows pour KWin,
  https://github.com/Schneegans/Burn-My-Windows) — installé mais désactivé.
