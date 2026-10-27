# Configuration RetroArch — émulateurs uniquement

État au 11 octobre 2026. Les trois jeux téléchargés initialement ont été supprimés, ainsi que leurs sauvegardes de test. Lors de la personnalisation visuelle, le jeu N64 déjà présent sur le PC a été ajouté à sa section ; aucun jeu supplémentaire n’a été téléchargé.

## Ce qui est installé

- Manette Xbox Series X/S, pilote Linux `udev`, profil adapté au nom `Microsoft Xbox Controller` et aux identifiants 045e:0b12. RetroArch confirme sa configuration sur le port 1. La disposition matérielle des boutons a été lue ; les pressions physiques restent à essayer par l’utilisateur.
- Game Boy / Game Boy Color : **Gambatte**, installé en premier. Son chargement et son exécution ont été vérifiés avant suppression des jeux de test. Aucun BIOS n’est obligatoire pour ce cœur.
- **178 cœurs classés Emulator** proposés dans le catalogue officiel Linux x86_64. Ils comprennent notamment mGBA, Snes9x, Genesis Plus GX, Mupen64Plus-Next, SwanStation, LRPS2/PCSX2, PPSSPP, Dolphin, melonDS, Citra, Flycast.
- Profils de manettes, informations des cœurs et compléments officiels Dolphin, PPSSPP, LRPS2, ScummVM et blueMSX. Ces compléments sont des données système, pas des jeux.

Installer les cœurs ne rend pas automatiquement toutes les machines jouables : certains attendent un BIOS, des données spécifiques ou des réglages adaptés au jeu. Aucun test de jeu n’a été effectué sur les autres systèmes. Les 178 bibliothèques ne présentent aucune dépendance dynamique manquante d’après `ldd` ; cela ne garantit pas leur compatibilité à l’exécution.

## Stockage réellement mesuré

Unités décimales : 1 Go = 1 milliard d’octets ; 1 To = 1 000 Go. Les tailles portent sur les fichiers, hors allocation et compression du système de fichiers.

| Élément | Taille |
|---|---:|
| Gambatte (Game Boy / Color) | 4.80 Mo |
| 177 autres cœurs d’émulation | 1.138 Go |
| Compléments système | 120.12 Mo |
| Profils de manettes + métadonnées | 2.60 Mo |
| **Total ajouté, hors sauvegarde de configuration** | **1.265 Go** |
| Jeux | **0 Mo** |

Donc quelques Go suffisent pour les émulateurs : aucun besoin de To pour cette installation. La taille future évoluera avec les versions et les cœurs ajoutés. L’application RetroArch et ses ressources graphiques étaient déjà installées et sont exclues du total ajouté.

## Utilisation

1. Ouvrir RetroArch normalement.
2. Pour la Game Boy : **Menu principal → Charger un cœur → Nintendo - Game Boy / Color (Gambatte)**.
3. Le cœur est prêt ; sans fichier de jeu, il n’affiche pas de jeu. Le dossier `~/Jeux/ROMs/Game Boy` est vide.

La croix sert à naviguer ; le bouton Xbox ouvre le menu en jeu. Avec le réglage actuel du menu, A valide et B revient en arrière. Pour Gambatte, la disposition standard associe le bouton Xbox B au bouton Game Boy A, et Xbox A à Game Boy B ; View = Select, Menu = Start. On pourra modifier cette disposition selon ta préférence.

## Fichiers et restauration

- Configuration : `~/.config/retroarch/retroarch.cfg`
- Cœurs : `~/.config/retroarch/cores/`
- Profil spécifique : `~/.config/retroarch/autoconfig/udev/Microsoft_Xbox_Series_xone.cfg`
- Données système : `~/.config/retroarch/system/`
- Configuration d’origine : `~/.config/retroarch/backup-setup-20261011-152122/retroarch.cfg`

Pour restaurer les réglages initiaux : fermer RetroArch, puis recopier la configuration d’origine à la place de `retroarch.cfg`. Les cœurs téléchargés restent sur disque.

L’[inventaire détaillé](INVENTAIRE-EMULATEURS.md) liste les tailles et les fichiers requis absents. Les rapports JSON fournissent l’état des téléchargements et des dépendances.

Sources officielles : [Gambatte](https://docs.libretro.com/library/gambatte/), [profils de manettes](https://docs.libretro.com/guides/controller-autoconfiguration/), [catalogue des cœurs](https://buildbot.libretro.com/nightly/linux/x86_64/latest/), [fichiers système](https://buildbot.libretro.com/assets/system/).

Correction : McSoftServe, cœur humoristique du 1er avril classé « Emulator » par Libretro, a été retiré.

Les 17 cœurs du groupe Arcade ont été supprimés à la demande de l’utilisateur (1,147 Go de fichiers).


## Interface XMB et effets communautaires

Personnalisation du 11 octobre 2026 : [Retrorama XMB de lipebello](https://github.com/lipebello/Retroarch-XMB-Retrorama-Theme), avec ses icônes, sa police et ses fonds. Un seul onglet par console, sans multiplier les émulateurs ni les variantes régionales. Les rubriques Images, Vidéos, Musique, Netplay, Exploration et Cœurs sans contenu sont masquées ; les cœurs restent installés et accessibles via Charger un cœur. Les consoles non retenues parmi les 26 principales restent accessibles ainsi.

Les onglets vides sont intentionnels : aucun faux jeu n’a été ajouté. Les fonds dynamiques sont des images fixes qui changent en naviguant entre consoles. Les 26 sections ont chacune leur fond distinct en 1920×1080. GameCube, Wii et PS2 complètent le pack XMB grâce aux illustrations originales de [Retrorama Champion Edition](https://github.com/lipebello/es-theme-retrorama-ce), assemblées dans le modèle fourni par l’auteur. Les sources SVG sont conservées dans assets-retrorama/sources/. Aucun fond générique de remplacement ne reste pour ces sections.

Les playlists utilisent un cœur par défaut. Pour ajouter des jeux plus tard, déposer ses fichiers dans le dossier associé puis utiliser **Réglages → Listes de lecture → Gérer les listes de lecture → [console] → Actualiser la liste de lecture**. Les dossiers ont été configurés pour le scan récursif ; utiliser les dossiers dédiés conserve la sélection automatique des effets. L’actualisation et les formats multidisques peuvent nécessiter un tri : préférer les fichiers .cue ou .m3u aux pistes .bin isolées pour ces jeux.

| Console | Dossier sous ~/Jeux/ROMs | Cœur par défaut | Effet |
|---|---|---|---|
| Atari - 2600 | Atari 2600 | stella | Mega Bezel Standard, CRT + cadre réfléchissant |
| Atari - 5200 | Atari 5200 | a5200 | Mega Bezel Standard, CRT + cadre réfléchissant |
| Atari - 7800 | Atari 7800 | prosystem | Mega Bezel Standard, CRT + cadre réfléchissant |
| Atari - Jaguar | Jaguar | virtualjaguar | Mega Bezel Standard, CRT + cadre réfléchissant |
| NEC - PC Engine | PC Engine | mednafen_pce_fast | Mega Bezel Standard, CRT + cadre réfléchissant |
| Nintendo - NES | NES | mesen | Mega Bezel Standard, CRT + cadre réfléchissant |
| Nintendo - Super Nintendo | SNES | snes9x | Mega Bezel Standard, CRT + cadre réfléchissant |
| Nintendo - Nintendo 64 | N64 | mupen64plus_next | CRT Easymode |
| Nintendo - GameCube | GameCube | dolphin | Rendu du cœur, sans effet imposé |
| Nintendo - Wii | Wii | dolphin | Rendu du cœur, sans effet imposé |
| Nintendo - Game Boy | Game Boy | gambatte | Game Boy, LCD vert + bordure |
| Nintendo - Game Boy Color | Game Boy Color | gambatte | Game Boy Color, LCD + bordure |
| Nintendo - Game Boy Advance | Game Boy Advance | mgba | Game Boy Advance, LCD + bordure |
| Nintendo - Nintendo DS | Nintendo DS | melondsds | Grille LCD |
| Nintendo - Nintendo 3DS | Nintendo 3DS | azahar | Rendu du cœur, sans effet imposé |
| Sega - Master System | Master System | genesis_plus_gx | Mega Bezel Standard, CRT + cadre réfléchissant |
| Sega - Mega Drive | Mega Drive | genesis_plus_gx | Mega Bezel Standard, CRT + cadre réfléchissant |
| Sega - Mega-CD | Mega-CD | genesis_plus_gx | Mega Bezel Standard, CRT + cadre réfléchissant |
| Sega - 32X | 32X | picodrive | Mega Bezel Standard, CRT + cadre réfléchissant |
| Sega - Saturn | Saturn | kronos | CRT Easymode |
| Sega - Dreamcast | Dreamcast | flycast | CRT Easymode |
| Sega - Game Gear | Game Gear | genesis_plus_gx | Game Gear + bordure |
| SNK - Neo Geo Pocket | Neo Geo Pocket | mednafen_ngp | Neo Geo Pocket + bordure |
| Sony - PlayStation | PlayStation | swanstation | CRT Easymode |
| Sony - PlayStation 2 | PlayStation 2 | pcsx2 | Rendu du cœur, sans effet imposé |
| Sony - PSP | PSP | ppsspp | PSP + bordure |

Les shaders viennent du [dépôt Slang de Libretro](https://github.com/libretro/slang-shaders), déjà installé sur le PC. Le pilote **glcore** est activé pour les utiliser. Les dossiers Game Boy/Color et Game Gear permettent de distinguer les systèmes partageant le même cœur. En dehors des dossiers dédiés, Gambatte reçoit une grille LCD générique et Genesis Plus GX un CRT léger. Les presets sont configurés pour les cœurs par défaut du tableau ; les 178 autres variantes ne sont pas toutes reconfigurées ni testées.

Pour changer d’effet en jeu : **Menu rapide → Shaders → Charger un préréglage**. Le dossier proposé contient six choix lisibles : CRT avec cadre/reflets, CRT léger, Game Boy, Game Boy Color, Game Boy Advance et LCD. Les sous-dossiers crt, handheld et bezel donnent accès aux autres presets communautaires. Utiliser **Shaders → Sauvegarder → Sauvegarder le préréglage du jeu** pour limiter un changement au jeu courant. Désactiver Shaders vidéo pour retrouver une image sans filtre.

Mega Bezel intègre son propre cadre et les reflets réagissent à l’image du jeu. Les portables utilisent les bordures du pack console-border. Les overlays communautaires de Libretro sont également accessibles dans **Menu rapide → Affichage à l’écran → Overlay à l’écran**, sous borders/animated-border : NES, Super Famicom, Mega Drive et PlayStation (Fercho). Leur animation suit les boutons ; ils sont laissés facultatifs pour éviter de superposer deux cadres. Désactiver le preset avec bordure avant d’en sélectionner un ; leur cadrage peut demander un ajustement selon la console et la fenêtre.

Validation : lancement XMB/glcore avec la RTX 3080, capture du menu montrant les onglets et le fond par console, compilation et rendu de Mega Bezel et Game Boy sur mire locale sans ROM. La manette Xbox reste reconnue. Aucun test de compatibilité de l’ensemble des jeux/cœurs n’a été effectué.

### Retour aux réglages précédents

Fermer RetroArch. La sauvegarde avant personnalisation se trouve ici :

`~/.config/retroarch/backup-visual-20261011-160257`

Elle contient retroarch.cfg, config/ et playlists/. Restaurer retroarch.cfg remet les anciens réglages d’interface et le pilote graphique précédent. Pour retirer aussi les presets ajoutés, utiliser la liste exacte des fichiers dans visual-installation.json ; ne pas supprimer des sauvegardes de jeux. Les anciens fichiers config/ et playlists/ sont disponibles dans la sauvegarde. Les graphismes se trouvent dans ~/.config/retroarch/assets-retrorama/ ; les shaders simplifiés dans ~/.config/retroarch/shaders-selection/.

### Tester d’autres icônes tout en conservant les dessins

Aller dans **Réglages → Interface utilisateur → Apparence → Thème d’icônes**. Les neuf styles déjà installés (Automatic, Daite, Dot-Art, FlatUI, FlatUX, Monochrome, Pixel, Retrosystem, Systematic) sont accessibles ; des alias conservent les icônes des consoles dont les noms de section ont été simplifiés. Custom/Personnalisé correspond à Retrorama. **Systematic** représente les consoles ; **Retrosystem** utilise notamment leurs manettes ; **Monochrome** est plus sobre. Cela change les icônes, pas les fonds dynamiques, les shaders ou les overlays. Redémarrer RetroArch si un changement ne se recharge pas immédiatement.

Les illustrations sont l’œuvre de Filipe Bello (lipebello / Phill’s Doodles). Leurs sources et les licences fournies par les dépôts sont conservées dans assets-retrorama/. Les trois compléments sont des adaptations locales du modèle et des illustrations existants ; les dessins n’ont pas été recréés.


### Jaquettes et captures

Téléchargement à la demande activé. Jaquette affichée à gauche pour conserver le dessin du fond à droite. Les images disponibles de Star Wars Episode I - Racer (USA), seul jeu actuellement dans les playlists, ont été récupérées depuis libretro-thumbnails (boîte, capture, écran-titre). Les futurs jeux reconnus pourront récupérer leurs images à la navigation ; la disponibilité dépend du catalogue et des noms. Aucun fichier de jeu téléchargé.


## ES-DE : interface animée

ES-DE 3.5.0 installé via l’AppImage officielle ; raccourci **ES-DE** dans le menu des applications. Configuration dans `~/ES-DE/`, thème communautaire [Adroit](https://github.com/RickAndTired/adroit-es-de), variante Grid Covers et palette Animated. Fond vidéo fourni par le thème et transitions glissées actifs. Référence GIF facultative retirée car seul le MP4 est fourni ; les fichiers originaux du thème sont conservés avec le suffixe .upstream.

Les 26 consoles sont reliées aux dossiers existants et à leurs cœurs RetroArch. ES-DE affiche seulement celles contenant des jeux ; actuellement la N64. Aucun jeu n’a été téléchargé. Les trois images du jeu N64 ont été reprises pour ES-DE. Les jeux se lancent dans le même RetroArch, avec ses shaders et sauvegardes. Le menu XMB Retrorama reste disponible en ouvrant RetroArch directement.

Vérifications : décodage du fond background.mp4 confirmé dans le journal, manette Xbox reconnue automatiquement, jaquette affichée, lancement de Star Wars Episode I - Racer depuis ES-DE effectué par l’utilisateur. Le journal confirme le chargement du preset Nintendo - N64.slangp et la compilation de crt-easymode.slang, puis le retour à ES-DE après fermeture du jeu.

Pour tester d’autres thèmes : **Start/Menu → Paramètres de l’interface utilisateur → Téléchargeur de thèmes** (libellé selon traduction). Les thèmes ES-DE sont séparés des shaders et overlays RetroArch. Adroit change le style du menu pour une présentation animée ; les illustrations Retrorama restent dans RetroArch.


## Retour au frontend d’origine

`quit_on_close_content = "2"` est activé (quitter à la fermeture du contenu seulement pour un lancement en ligne de commande). ES-DE lance RetroArch avec un cœur et un jeu : **bouton Xbox → Fermer le contenu** ferme alors RetroArch et réaffiche ES-DE. Si RetroArch est ouvert normalement puis le jeu choisi dans XMB, la même action arrête seulement le jeu et conserve XMB. ES-DE garde `RunInBackground=false`, son fonctionnement normal d’attente de l’émulateur.

Le bouton Xbox ouvre toujours le menu rapide pour régler shaders, contrôles ou sauvegardes. Pour arrêter un jeu et retrouver sa bibliothèque, utiliser **Fermer le contenu**, sans quitter manuellement le frontend. L’option se fonde sur le mode de lancement : un jeu ouvert directement par une commande ou un raccourci de jeu ferme aussi RetroArch à la fermeture du contenu. Les raccourcis classiques ES-DE et RetroArch ont le comportement décrit ci-dessus.

Vérification : valeur enregistrée, commandes des 26 consoles ES-DE avec cœur explicite, profil Xbox conservé et logique contrôlée dans les sources RetroArch 1.22.2 (`should_quit_on_close`).


## Xbox originale : xemu

xemu **0.8.136 Linux**, AppImage officielle, installé dans ~/Applications et accessible avec le raccourci **xemu** ou la commande ~/.local/bin/xemu. La version Windows téléchargée n’est pas utilisée. Les fichiers mcpx_1.0.bin et Complex_4627.bin fournis dans Téléchargements ont été copiés vers ~/.local/share/xemu/xemu/bios/. Le MCPX a l’empreinte MD5 attendue par le projet : d49c52a4102f6df7bcf8d0617ac475ed.

Configuration : ~/.local/share/xemu/xemu/xemu.toml. Disque préformaté officiel xemu-dashboard dans ~/.local/share/xemu/xemu/xbox_hdd.qcow2, EEPROM générée par xemu. Ce disque contient le tableau de bord libre minimal, pas celui de Microsoft. Le format QCOW2 grandit avec les données écrites ; capacité virtuelle annoncée de 8 Go.

Manette Xbox Series affectée au port 1 (GUID SDL 0600b7925e040000120b000017050000), profil standard et vibrations activées par défaut. A/B/X/Y et les sticks gardent leur rôle habituel ; LB/RB correspondent aux boutons blanc/noir de la Xbox originale. Le bouton Xbox, ou View+Menu, ouvre le menu de xemu ; F1/F2 permettent également d’ouvrir ses menus au clavier. Pour revenir à ES-DE, quitter xemu depuis son menu (ou Alt+F4). Fermer seulement le disque ne ferme pas l’émulateur.

OpenGL, résolution interne ×2, ratio natif et synchronisation verticale par défaut. Les shaders RetroArch ne s’appliquent pas à xemu. La manette est détectée et enregistrée ; les vibrations et chaque touche restent à confirmer dans un jeu.

ES-DE possède maintenant une section Microsoft - Xbox : dossier ~/Jeux/ROMs/Xbox, images .iso/.ISO, lancement xemu en plein écran. Utiliser des images de disque au format compatible xemu (XISO), pas n’importe quelle ISO brute. La section n’apparaît qu’avec des jeux. Relancer ES-DE pour charger l’ajout après la fin du scraping en cours. Aucun jeu n’a été téléchargé.

Validation : xemu lit le BIOS, le MCPX et le disque sans erreur de chargement ; son interface de contrôle QMP renvoie running=true. Port manette 1 vérifié dans la configuration enregistrée. Aucun jeu Xbox n’a été testé.

Sources : [installation Linux](https://xemu.app/docs/download/), [fichiers requis](https://xemu.app/docs/required-files/), [manettes](https://xemu.app/docs/controller/), [options de lancement](https://xemu.app/docs/cli/).
