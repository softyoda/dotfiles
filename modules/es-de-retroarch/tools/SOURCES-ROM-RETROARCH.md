# Sources de ROM et de jeux pour ton installation RetroArch

Guide préparé le **11 octobre 2026**, pour ton PC Linux et les **178 cœurs encore installés** après suppression du groupe Arcade et de McSoftServe.

Ce document fournit les liens pour que **tu choisisses et télécharges toi-même** les jeux. Aucun jeu, pack ou BIOS n’a été téléchargé pour préparer ce guide.

Il s’agit d’une sélection documentée, pas d’une liste exhaustive de tout Internet. Les sources privilégiées sont les auteurs, les éditeurs, les projets officiels et les archives communautaires identifiables. Les catalogues communautaires restent à vérifier jeu par jeu : leur présence dans ce guide ne certifie ni chaque fichier ni chaque autorisation de distribution.

Les jeux commerciaux historiques ne disposent pas tous d’une distribution de ROM autorisée. Je distingue donc les **homebrews**, les **démos**, les **jeux gratuits** et les **ROM vendues par leurs auteurs**. Pour les systèmes sans source confirmée, je l’indique au lieu de promettre un « full set » fiable.

## Sommaire

1. [Les points de départ les plus utiles](#1-les-points-de-départ-les-plus-utiles)
2. [Les packs et compilations réellement identifiés](#2-les-packs-et-compilations-réellement-identifiés)
3. [Game Boy et autres consoles Nintendo](#3-game-boy-et-autres-consoles-nintendo)
4. [Consoles Sega](#4-consoles-sega)
5. [Consoles Sony](#5-consoles-sony)
6. [Atari et autres consoles](#6-atari-et-autres-consoles)
7. [Ordinateurs rétro](#7-ordinateurs-rétro)
8. [Machines spécialisées et plateformes virtuelles](#8-machines-spécialisées-et-plateformes-virtuelles)
9. [Télécharger et installer dans RetroArch](#9-télécharger-et-installer-dans-retroarch)
10. [BIOS, formats et problèmes courants](#10-bios-formats-et-problèmes-courants)
11. [Repères de stockage](#11-repères-de-stockage)
12. [Formats déclarés par tes 178 cœurs](#12-formats-déclarés-par-tes-178-cœurs)

## 1. Les points de départ les plus utiles

| Source | Ce que tu peux y chercher | Type de source | Pack unique ? |
|---|---|---|---|
| [Catalogue de contenus Libretro](https://buildbot.libretro.com/assets/cores/) | Contenus classés par machine | Serveur du projet RetroArch/Libretro | Généralement non : fichiers séparés |
| [itch.io — Game Boy ROM](https://itch.io/games/tag-gameboy-rom) | Jeux GB/GBC publiés par leurs créateurs | Plateforme de publication ; vérifier l’auteur | Selon la fiche |
| [Action 53](https://action53.itch.io/) | Compilations NES | Équipe des compilations | **Oui** |
| [Morphcat Games](https://morphcatgames.itch.io/) | Jeux NES avec ROM explicitement incluse | Développeur | Généralement par jeu |
| [GBAdev](https://gbadev.org/) | Jeux, démos et projets GBA | Communauté de développement | Généralement non |
| [PDRoms — fichiers](https://pdroms.de/files) | Homebrews pour de nombreuses plateformes | Archive communautaire | Variable |
| [NESWorld — homebrew](https://www.nesworld.com/content.php?data=homebrew) | Sélections de jeux indépendants rétro | Catalogue communautaire | Généralement non |
| [Zophar — Public Domain ROMs](https://www.zophar.net/pdroms.html) | Anciennes créations, démos et logiciels classés par machine | Archive communautaire | Variable |
| [Retroguru](https://www.retroguru.com/) | Jeux du studio, avec versions pour plusieurs plateformes | Développeur | Versions séparées |
| [RetroSouls](https://www.retrosouls.net/) | Jeux pour Mega Drive et ZX Spectrum notamment | Développeur | Généralement par jeu |
| [The Mojon Twins](https://www.mojontwins.com/) | Créations NES, Spectrum, CPC, Mega Drive, DOS, ZX81 | Développeurs | Selon la publication |
| [DOS Games Archive](https://www.dosgamesarchive.com/) | Jeux DOS gratuits, shareware et démos | Archive spécialisée | Généralement par jeu |
| [DOSGames.com](https://dosgames.com/) | Jeux DOS distribués gratuitement | Archive spécialisée | Généralement par jeu |
| [GameBrew](https://www.gamebrew.org/wiki/Main_Page) | Fiches de homebrews, notamment portables et consoles récentes | Wiki communautaire | Généralement non |

**Comment utiliser les catalogues communautaires :** ouvrir la fiche du jeu, identifier son auteur, suivre le lien du projet original lorsqu’il existe, puis vérifier la plateforme et le fichier proposé. Une étiquette « gratuit » ne signifie pas que tous les éléments du jeu sont libres de droits ; une licence de moteur ne couvre pas forcément ses graphismes ou ses données.

**Attention au mot « collection » :** sur itch.io, il peut simplement s’agir d’une liste de favoris. Un véritable téléchargement groupé doit afficher un fichier ou une offre contenant plusieurs jeux.

### Ce que contiennent réellement certains répertoires Libretro

Vérification des listes de fichiers pendant la préparation du guide ; aucun binaire téléchargé ni testé. Ce tableau permet de distinguer les jeux des outils de diagnostic.

| Répertoire | Contenu observé | Utilité pour toi |
|---|---|---|
| [Atari 2600](https://buildbot.libretro.com/assets/cores/Atari%20-%202600/) | Sheep It Up | Un jeu identifié |
| [WonderSwan Color](https://buildbot.libretro.com/assets/cores/Bandai%20-%20WonderSwan%20Color/) | `swandriving.wsc` | Un programme à essayer, pas une compilation |
| [ColecoVision](https://buildbot.libretro.com/assets/cores/Coleco%20-%20Colecovision/) | Bruce’s Controller Tester | **Test de manette**, pas une sélection de jeux |
| [GameCube / Wii](https://buildbot.libretro.com/assets/cores/Nintendo%20-%20GameCube%20-%20Wii/) | Super Methane Brothers et plusieurs tests | Jeu et outils mélangés |
| [Nintendo 3DS](https://buildbot.libretro.com/assets/cores/Nintendo%20-%20Nintendo%203DS/) | Bottomless Block Barrage | Un jeu identifié |
| [Nintendo 64](https://buildbot.libretro.com/assets/cores/Nintendo%20-%20Nintendo%2064/) | Flappy Bird et tests de contrôleur | Très petit choix |
| [Virtual Boy](https://buildbot.libretro.com/assets/cores/Nintendo%20-%20Virtual%20Boy/) | Ballface et VB Racing | Deux programmes identifiés |
| [Pokémon Mini](https://buildbot.libretro.com/assets/cores/Nintendo%20-%20Pokemon%20Mini/) | Touhou – Bad Apple | Une démo audiovisuelle ; pas un catalogue de jeux |
| [Neo Geo Pocket](https://buildbot.libretro.com/assets/cores/SNK%20-%20Neo%20Geo%20Pocket/) | Gears of Fate | Un titre identifié |
| [Dreamcast](https://buildbot.libretro.com/assets/cores/Sega%20-%20Dreamcast/) | Volgarr the Viking et tests | Jeu et outils mélangés |
| [Game Gear](https://buildbot.libretro.com/assets/cores/Sega%20-%20Game%20Gear/) | ButtonTest | **Test de boutons uniquement** dans la liste consultée |
| [Master System](https://buildbot.libretro.com/assets/cores/Sega%20-%20Master%20System%20-%20Mark%20III/) | Test de contrôleur de Charles MacDonald | **Test de boutons**, pas une bibliothèque de jeux |
| [Saturn](https://buildbot.libretro.com/assets/cores/Sega%20-%20Saturn/) | `demo.zip` | Une démo ; contenu précis non inspecté |
| [PlayStation 1](https://buildbot.libretro.com/assets/cores/Sony%20-%20PlayStation/) | 240p Test Suite et PSXTEST | **Outils de test**, pas des jeux |
| [PSP](https://buildbot.libretro.com/assets/cores/Sony%20-%20PlayStation%20Portable/) | Cube Test | **Démo de test**, pas une collection de jeux |
| [Arduous](https://buildbot.libretro.com/assets/cores/Arduous/) | `demo.hex` | Une démo |

Le répertoire Intellivision est présent dans l’index principal, mais son contenu n’a pas pu être récupéré par mon outil : son lien est fourni comme piste, sans contenu confirmé. Une liste accessible ne vaut pas audit de sécurité des fichiers ni vérification de leurs droits ; les pages d’auteurs restent préférables lorsque disponibles.

## 2. Les packs et compilations réellement identifiés

### Compilations NES Action 53

Ce sont des compilations homebrew avec un menu de sélection dans la ROM. Elles mélangent jeux, petites expériences et parfois outils : le nombre annoncé ne correspond pas exclusivement à des jeux complets.

| Compilation | Contenu annoncé | Téléchargement | Cœur installé à utiliser |
|---|---|---|---|
| [Action 53 Volume 1](https://action53.itch.io/vol1) | 20 titres et expériences | Archive ZIP sur la page | Mesen |
| [Double Action 53 Volume 2](https://action53.itch.io/vol2) | 16 jeux et 3 petites applications | Archive ZIP sur la page | Mesen |
| [Action 53 Volume 3](https://action53.itch.io/vol3) | 23 jeux et expériences annoncés par la collection | Archive sur la page | Mesen |
| [Action 53 Volume 4 — Actually 54](https://action53.itch.io/vol4) | 54 titres et expériences | Archive ZIP affichée à environ 2,3 Mo | Mesen |

Il existe des reprises et des versions différentes entre volumes : ne pas additionner les chiffres en supposant autant de jeux uniques. Les auteurs indiquent aussi que le **mapper 28** doit être pris en charge par l’émulateur ; ils proposent Mesen. Décompresse le ZIP puis ouvre la ROM `.nes`. [Instructions du volume 4](https://action53.itch.io/vol4).

### Archive CHIP-8 en un téléchargement

[Chip8 Community Archive de John Earnest](https://github.com/JohnEarnest/chip8Archive) contient des programmes compilés dans le dossier `roms/`, leurs métadonnées et leurs sources. Le projet annonce une licence **CC0** pour son contenu. C’est un vrai ensemble récupérable via **Code → Download ZIP** ; après extraction, utilise les fichiers `.ch8` avec **JAXE**. Les programmes peuvent viser CHIP-8, Super-CHIP ou XO-CHIP et demander les réglages correspondants. [Description et licence](https://github.com/JohnEarnest/chip8Archive/blob/master/Readme.md).

### Ce que je n’ai pas confirmé comme pack

| Source | Ce qu’elle fournit | Limite |
|---|---|---|
| Libretro Content Downloader | Un catalogue centralisé | Pas un pack universel couvrant toutes les consoles |
| itch.io | Jeux et offres d’auteurs | Les bundles changent ; leur contenu doit préciser les ROM incluses |
| PDRoms / NESWorld / Zophar | Nombreuses fiches | Pas de pack complet vérifié ici |
| GBAdev | Publications et compétitions | Une compétition ne signifie pas qu’un ZIP global existe |
| Archives DOS | Beaucoup de jeux distincts | Les versions peuvent être limitées au shareware ou à une démo |

Je n’ai pas trouvé de pack officiel regroupant les bibliothèques commerciales de toutes tes consoles. Les compilations identifiées ci-dessus permettent de récupérer plusieurs créations sans confondre cela avec un catalogue commercial complet.

## 3. Game Boy et autres consoles Nintendo

### Game Boy / Game Boy Color — ta priorité

**Cœur déjà configuré : Gambatte.** Fichiers reconnus : `.gb`, `.gbc`, `.dmg`. Les autres cœurs GB/GBC utilisent généralement les mêmes jeux : pas besoin d’une collection distincte pour chaque émulateur.

| Source | Intérêt | Ce qu’il faut sélectionner |
|---|---|---|
| [itch.io — Game Boy ROM](https://itch.io/games/tag-gameboy-rom) | Catalogue de créations récentes, gratuites ou payantes | Une vraie ROM, pas uniquement la version navigateur |
| [Tobu Tobu Girl — Tangram Games](https://tangramgames.dk/tobutobugirl/) | Publication directe du développeur, ROM gratuite | Le lien de téléchargement donné par le studio |
| [Tobu Tobu Girl Deluxe](https://tangramgames.dk/tobutobugirldx/) | Édition Game Boy Color publiée gratuitement par le studio | La ROM de l’édition Deluxe |
| [Libretro — Game Boy](https://buildbot.libretro.com/assets/cores/Nintendo%20-%20GameBoy/) | Petit catalogue centralisé | Le fichier du jeu choisi ; certains sont des démos |
| [NESWorld — Game Boy Color](https://nesworld.com/article.php?data=gbchomebrew&system=gbc) | Autre catalogue homebrew | Vérifier la fiche et la version |
| [Homebrew Hub — projet GBDev](https://github.com/gbdev/homebrewhub) | Projet de catalogue GB/GBC | Suivre l’adresse de l’instance indiquée dans le dépôt |

L’adresse historique `hh.gbdev.io` a renvoyé un refus d’accès à mon outil de consultation. Le projet est identifié, mais je ne présente pas son interface comme vérifiée accessible pendant cette recherche.

**Première installation :** télécharger une ROM depuis la page de son auteur, la placer dans `~/Jeux/ROMs/Game Boy/`, puis utiliser **Charger un contenu** dans RetroArch. L’installation de Gambatte n’impose aucun téléchargement de pack BIOS. [Documentation Gambatte](https://docs.libretro.com/library/gambatte/).

### Game Boy Advance

| Source | Offre | Cœur installé |
|---|---|---|
| [GBAdev](https://gbadev.org/) | Section Games/Demos et publications de développeurs | mGBA |
| [Goodboy Galaxy — version GBA](https://goodboygalaxy.itch.io/goodboy-galaxy-gba) | Jeu payant vendu explicitement comme ROM GBA | mGBA |
| [Goodboy Galaxy — démo](https://goodboygalaxy.itch.io/goodboy-galaxy-demo) | Démo liée par la page officielle du jeu | mGBA |
| [Libretro — GBA](https://buildbot.libretro.com/assets/cores/Nintendo%20-%20GameBoy%20Advance/) | Contenus regroupés par plateforme | mGBA |

Pour Goodboy Galaxy, choisir le fichier **GBA ROM** plutôt que l’exécutable PC ou le paquet destiné à la 3DS. Une démo et un jeu complet doivent rester identifiables dans tes noms de fichiers.

### NES / Famicom

Les quatre compilations **Action 53** de la section 2 sont les packs les plus concrets de cette sélection.

Pour des jeux séparés, [Morphcat Games](https://morphcatgames.itch.io/) propose notamment **Micro Mages** avec ROM incluse, **Böbl**, **Spacegulls** et une démo de **Super Bat Puncher**. Les pages distinguent les jeux vendus des téléchargements proposés autrement. Utilise le fichier `.nes` avec **Mesen**, déjà installé.

Autres pistes identifiées : [NESWorld — homebrews NES](https://www.nesworld.com/article.php?data=neshomebrew&system=nes), [The Mojon Twins](https://www.mojontwins.com/), [catalogue NES Libretro](https://buildbot.libretro.com/assets/cores/Nintendo%20-%20Nintendo%20Entertainment%20System/).

### Super Nintendo

| Source | Contenu | Cœur installé |
|---|---|---|
| [Dottie Flowers — Goldlocke](https://goldlocke.itch.io/dottie-flowers) | Page de l’auteur avec édition numérique | Snes9x ou bsnes |
| [Dottie dreads nought — Goldlocke](https://goldlocke.itch.io/dottie-dreads-nought) | Jeu de la SNESDEV Game Jam, ROM pour émulateur | Snes9x ou bsnes |
| [itch.io — SNES, gratuit et téléchargeable](https://itch.io/games/downloadable/free/tag-snes) | Découverte d’autres projets | Vérifier qu’un `.sfc` ou `.smc` est fourni |
| [Libretro — SNES](https://buildbot.libretro.com/assets/cores/Nintendo%20-%20Super%20Nintendo%20Entertainment%20System/) | Contenus classés SNES | Snes9x ou bsnes |

Une fiche portant seulement le tag « SNES » peut décrire un jeu PC inspiré de cette console. La présence d’une ROM dans les fichiers compte davantage que le style visuel.

### Nintendo 64, DS et 3DS

| Machine | Sources identifiées | Cœurs installés concernés | Précision |
|---|---|---|---|
| Nintendo 64 | [Libretro — N64](https://buildbot.libretro.com/assets/cores/Nintendo%20-%20Nintendo%2064/), [PDRoms](https://pdroms.de/files) | Mupen64Plus-Next, ParaLLEl N64 | Projets homebrew et démos ; pas un full set commercial |
| Nintendo DS | [GameBrew](https://www.gamebrew.org/wiki/Main_Page), [PDRoms](https://pdroms.de/files) | melonDS, melonDS DS, DeSmuME | Chercher la version `.nds` et conserver ses fichiers annexes |
| Nintendo 3DS | [Libretro — 3DS](https://buildbot.libretro.com/assets/cores/Nintendo%20-%20Nintendo%203DS/), [GameBrew](https://www.gamebrew.org/wiki/Main_Page) | Azahar, Citra, Panda3DS | Le format et la compatibilité du homebrew varient suivant le cœur |

GameBrew est un répertoire de projets, pas une garantie que chaque application conçue pour une console physique fonctionne dans son émulateur. Revenir au site ou au dépôt de l’auteur pour lire les instructions.

### GameCube, Wii et Wii U

| Machine | Point de départ | Cœur installé | Limite |
|---|---|---|---|
| GameCube / Wii | [Contenus Libretro](https://buildbot.libretro.com/assets/cores/Nintendo%20-%20GameCube%20-%20Wii/) | Dolphin | Catalogue limité |
| Wii | [Liste de jeux WiiBrew](https://www.wiibrew.org/wiki/List_of_homebrew_games) | Dolphin | Les accès SD, périphériques et fichiers annexes peuvent demander des réglages |
| Wii U | [GameBrew](https://www.gamebrew.org/wiki/Main_Page) | Cemu | Piste de recherche homebrew ; aucun pack prêt à jouer confirmé ici |

Pour WiiBrew, sélectionner un **jeu autonome**. Un port de moteur peut demander des données supplémentaires. Les formats Wii `.dol` ou `.elf` ne sont pas des ROM Game Boy ; ils doivent être ouverts avec le cœur de la bonne console.

### Virtual Boy et Pokémon Mini

| Machine | Sources | Cœur installé |
|---|---|---|
| Virtual Boy | [Planet Virtual Boy](https://www.virtual-boy.com/) — communauté et homebrew ; [Libretro](https://buildbot.libretro.com/assets/cores/Nintendo%20-%20Virtual%20Boy/) | Beetle VB |
| Pokémon Mini | [Libretro](https://buildbot.libretro.com/assets/cores/Nintendo%20-%20Pokemon%20Mini/), puis les fiches d’auteurs de PDRoms | PokeMini |

Pokémon Mini désigne une **machine particulière** : une ROM Game Boy de Pokémon ne fonctionne pas dans PokeMini.

## 4. Consoles Sega

### Master System, Game Gear, Mega Drive, Mega-CD et 32X

| Source | Machines / contenu | Remarque |
|---|---|---|
| [RetroSouls](https://www.retrosouls.net/) | Publications Mega Drive, dont Tourmaline, GraviBots et AlterEgo | Le site renvoie vers les fiches de téléchargement du studio |
| [The Mojon Twins](https://www.mojontwins.com/) | Plusieurs plateformes dont Mega Drive | Choisir la bonne version du jeu |
| [OrionSoft](https://orionsoft.itch.io/) | Jeux du développeur pour plusieurs machines rétro | Vérifier l’édition et les fichiers fournis avant achat |
| [Alice Sisters — annonce GBA et Mega Drive](https://orionsoft.itch.io/alice-sisters/devlog/748070/sega-megadrive-genesis-gameboy-advance-version-) | Confirmation de la disponibilité de ROM pour ces deux machines | Suivre la fiche produit liée par l’auteur |
| [itch.io — Sega Genesis téléchargeable](https://itch.io/games/downloadable/tag-sega-genesis) | Catalogue de créations | Vérifier l’auteur et la présence d’une ROM |
| [Libretro — Master System](https://buildbot.libretro.com/assets/cores/Sega%20-%20Master%20System%20-%20Mark%20III/) | Contenus classés par machine | Fichiers individuels |
| [Libretro — Game Gear](https://buildbot.libretro.com/assets/cores/Sega%20-%20Game%20Gear/) | Contenus classés par machine | Fichiers individuels |
| [Libretro — Mega Drive](https://buildbot.libretro.com/assets/cores/Sega%20-%20Mega%20Drive%20-%20Genesis/) | Contenus classés par machine | Fichiers individuels |

**Correspondances pratiques :** Gearsystem pour Master System/Game Gear ; Genesis Plus GX pour Mega Drive et plusieurs machines Sega ; PicoDrive pour les contenus 32X. La liste exacte des extensions de chaque cœur est en annexe. Pour Mega-CD, un téléchargement peut être une image de disque et demander un BIOS adapté.

Je n’ai pas confirmé de pack 32X ou Mega-CD d’auteur comparable aux compilations Action 53.

### Dreamcast et Saturn

| Source | Offre | Cœur installé |
|---|---|---|
| [Retroguru](https://www.retroguru.com/) | Jeux du studio, qui propose notamment des versions Dreamcast | Flycast |
| [OrionSoft](https://orionsoft.itch.io/) | Catalogue du développeur ; vérifier la machine sur chaque produit | Flycast pour les éditions Dreamcast |
| [Libretro — Dreamcast](https://buildbot.libretro.com/assets/cores/Sega%20-%20Dreamcast/) | Contenus Dreamcast | Flycast |
| [Libretro — Saturn](https://buildbot.libretro.com/assets/cores/Sega%20-%20Saturn/) | Contenus Saturn | Beetle Saturn, Kronos ou autres cœurs Saturn installés |

Un jeu disponible sur plusieurs plateformes peut proposer simultanément un exécutable Linux et une image Dreamcast : télécharger **l’édition Dreamcast** pour Flycast. Conserver ensemble les pistes référencées par un `.gdi` ou un `.cue`.

**Arcade Sega :** Supermodel et la partie Naomi de Flycast existent encore, car ils étaient rangés dans le groupe Sega du tableau précédent. Les 17 cœurs du groupe Arcade ont été supprimés. Aucun pack arcade n’est proposé dans ce guide.

## 5. Consoles Sony

| Machine | Sources / point de départ | Cœur installé | Ce qui est confirmé |
|---|---|---|---|
| PlayStation 1 | [PSXDEV](https://www.psxdev.net/index.html), [Libretro — PS1](https://buildbot.libretro.com/assets/cores/Sony%20-%20PlayStation/) | SwanStation, Beetle PSX | Publications homebrew et contenus classés PS1 |
| PSP | [Libretro — PSP](https://buildbot.libretro.com/assets/cores/Sony%20-%20PlayStation%20Portable/), [GameBrew](https://www.gamebrew.org/wiki/Main_Page) | PPSSPP | Pistes homebrew ; vérifier les besoins de chaque projet |
| PlayStation 2 | [GameBrew](https://www.gamebrew.org/wiki/Main_Page) | LRPS2, PCEE2, Play! | Annuaire de projets ; aucun pack de jeux compatible vérifié ici |
| PlayStation 3 | [GameBrew](https://www.gamebrew.org/wiki/Main_Page) | RPCS3 | Annuaire de projets ; aucun pack prêt à jouer vérifié ici |
| PocketStation | [PDRoms](https://pdroms.de/files) et pages des développeurs lorsqu’elles existent | pokketstation | Pas de catalogue complet confirmé pendant cette recherche |

Un jeu PC au style « PSX » ne constitue pas nécessairement un jeu PlayStation. De même, une application PSP destinée à manipuler une console physique peut ne pas avoir d’utilité dans PPSSPP. Chercher les **jeux autonomes** et les indications de compatibilité de l’auteur.

Pour les jeux PS1 sur plusieurs pistes, ouvrir le `.cue` plutôt qu’une piste `.bin` isolée. Les BIOS et les images de jeux sont deux éléments séparés ; télécharger l’un ne fournit pas automatiquement l’autre.

## 6. Atari et autres consoles

### Atari

| Machine | Source utilisable ou piste identifiée | Cœur installé |
|---|---|---|
| Atari 2600 | [Libretro — Atari 2600](https://buildbot.libretro.com/assets/cores/Atari%20-%202600/), homebrews de [PDRoms](https://pdroms.de/files) | Stella |
| Atari 5200 / ordinateurs 8 bits | PDRoms et publications originales des auteurs | a5200, Atari800 |
| Atari 7800 | PDRoms et publications originales des auteurs | ProSystem |
| Lynx | PDRoms ; versions Lynx explicitement proposées par leurs auteurs | Handy, Gearlynx, Holani, Beetle Lynx |
| Jaguar | PDRoms ; versions Jaguar explicitement proposées par leurs auteurs | Virtual Jaguar |
| ST / STE / TT / Falcon | Versions Atari de logiciels libres ou de jeux d’auteurs | Hatari, hatariB |

Pour les lignes sans lien spécialisé, il s’agit d’une **piste de recherche**, pas de la confirmation d’un pack disponible. Je n’ai pas validé une compilation complète d’auteur pour ces systèmes.

### NEC, SNK, Bandai, Coleco et autres

| Machine / famille | Source identifiée | Cœur installé ou famille |
|---|---|---|
| PC Engine / TurboGrafx-16 | [Libretro — PC Engine](https://buildbot.libretro.com/assets/cores/NEC%20-%20PC%20Engine%20-%20TurboGrafx%2016/) | Beetle PCE, Geargrafx |
| SuperGrafx | [Libretro — SuperGrafx](https://buildbot.libretro.com/assets/cores/NEC%20-%20PC%20Engine%20SuperGrafx/) | Beetle SuperGrafx, Geargrafx |
| WonderSwan Color | [Libretro — WonderSwan Color](https://buildbot.libretro.com/assets/cores/Bandai%20-%20WonderSwan%20Color/) | Beetle Wonderswan |
| Neo Geo Pocket | [Libretro — Neo Geo Pocket](https://buildbot.libretro.com/assets/cores/SNK%20-%20Neo%20Geo%20Pocket/) | Beetle NeoPop, RACE |
| ColecoVision | [Libretro — ColecoVision](https://buildbot.libretro.com/assets/cores/Coleco%20-%20Colecovision/) | Gearcoleco, blueMSX, JollyCV |
| Intellivision | [Libretro — Intellivision](https://buildbot.libretro.com/assets/cores/Mattel%20-%20Intellivision/) | FreeIntv |
| Vectrex | [Libretro — Vectrex](https://buildbot.libretro.com/assets/cores/GCE%20-%20Vectrex/) | vecx |
| Jeux électroniques portables | [Libretro — Handheld Electronic Game](https://buildbot.libretro.com/assets/cores/Handheld%20Electronic%20Game/) | GW |

Ces liens sont les répertoires présents dans l’index Libretro consulté. Leur taille et leur contenu varient ; la présence d’un dossier ne signifie pas qu’il contient une bibliothèque complète. [Index de référence](https://buildbot.libretro.com/assets/cores/).

Pour **Neo Geo AES/MVS/CD, PC-FX, 3DO, CD-i, Playdia, NUON, Odyssey²/Videopac, Channel F, Arcadia/Interton, Cassette Vision, Super Cassette Vision, Mega Duck, Supervision et Tamagotchi**, je n’ai pas confirmé de pack d’auteur ou de catalogue de téléchargement suffisamment documenté pour le présenter ici comme solution prête à l’emploi. PDRoms et Zophar peuvent servir de points de recherche ; il faut retrouver l’origine et les conditions de chaque publication.

## 7. Ordinateurs rétro

### DOS et anciens PC

| Source | Contenu | À vérifier |
|---|---|---|
| [DOS Games Archive](https://www.dosgamesarchive.com/) | Versions gratuites, shareware, démos et certaines publications intégrales | Le type de version est indiqué sur les fiches |
| [DOSGames.com](https://dosgames.com/) | Catalogue de jeux DOS distribués gratuitement | Les fichiers requis et les instructions du jeu |
| [Libretro — DOS](https://buildbot.libretro.com/assets/cores/DOS/) | Contenus classés DOS | Le fichier de lancement |

Avec **DOSBox Pure**, une archive ZIP contenant un jeu DOS peut être ouverte directement. Conserver la structure du jeu et choisir son exécutable dans le menu du cœur. Une archive contenant uniquement un installateur nécessite encore l’installation du jeu ; ce n’est pas forcément un dossier immédiatement jouable. [Documentation DOSBox Pure](https://docs.libretro.com/library/dosbox_pure/).

**PCem, VirtualXT et QEMU** émulent des machines plus générales : ils peuvent demander un système d’exploitation, des disques et une configuration matérielle. Un pack de programmes DOS ne constitue pas automatiquement une machine virtuelle prête à démarrer.

### Amiga

[Aminet](https://aminet.net/) est une archive historique de logiciels Amiga redistribuables, selon sa [présentation officielle](https://wiki.aminet.net/About_Aminet). Chercher les catégories de jeux et lire les fichiers README : certains téléchargements sont des jeux, d’autres des mises à jour, outils ou données complémentaires.

La page de présentation a été consultée ; l’arborescence `/tree/game` n’a pas pu être ouverte par mon outil. L’accès et le fichier précis restent donc à vérifier dans ton navigateur.

[Retroguru](https://www.retroguru.com/) constitue aussi une piste de jeux d’auteurs, mais il faut distinguer **Amiga classique**, **AmigaOS moderne** et **MorphOS** : une version proposée pour l’un n’est pas automatiquement utilisable dans PUAE ou Amiberry.

Cœurs installés : **PUAE, PUAE 2021, Amiberry, FS-UAE**. Formats et besoins Kickstart varient selon la machine choisie.

### Spectrum, CPC, ZX81, MSX et Commodore

| Machine | Sources / pistes | Cœurs installés |
|---|---|---|
| ZX Spectrum | [RetroSouls](https://www.retrosouls.net/), [The Mojon Twins](https://www.mojontwins.com/) | Fuse |
| Amstrad CPC / GX4000 | [The Mojon Twins](https://www.mojontwins.com/) | Caprice32, CrocoDS |
| ZX81 | [The Mojon Twins](https://www.mojontwins.com/) | EightyOne |
| MSX / SVI | [PDRoms](https://pdroms.de/files), puis les publications d’auteurs correspondant au modèle | blueMSX, fMSX |
| C64, C128, VIC-20, Plus/4, PET, CBM-II | Fiches d’auteurs dans PDRoms / itch.io ; vérifier la machine exacte | Famille VICE, Frodo |

Sur les ordinateurs, un même nom de jeu peut exister sur plusieurs machines incompatibles. Un fichier `.dsk` peut correspondre à différentes plateformes ; son extension ne suffit pas à déterminer quel émulateur utiliser.

### Ordinateurs plus spécialisés

Pour **Apple II, Macintosh 68k, BBC Micro, Enterprise, Galaksija, Sharp X68000, NEC PC-88/PC-98, Philips P2000T, Thomson MO/TO et Oberon**, aucun pack complet de jeux distribué par un auteur ou éditeur n’a été confirmé ici. Les fichiers doivent correspondre au modèle et au système émulé. Les archives communautaires citées plus haut sont des pistes, pas une garantie de disponibilité pour chacune de ces machines.

## 8. Machines spécialisées et plateformes virtuelles

| Plateforme | Source | Cœur installé | Précaution de compatibilité |
|---|---|---|---|
| CHIP-8 / Super-CHIP / XO-CHIP | [Chip8 Community Archive](https://github.com/JohnEarnest/chip8Archive) | JAXE | Choisir la variante attendue par le programme |
| PICO-8 | [BBS officiel Lexaloffle](https://www.lexaloffle.com/bbs/?cat=7) | Retro8 | Prendre une cartouche, pas une capture d’écran ; compatibilité partielle |
| Arduboy | [Communauté liée par le site officiel](https://www.arduboy.com/emulator), [Libretro — Arduous](https://buildbot.libretro.com/assets/cores/Arduous/) | Ardens, Arduous | Formats `.hex` ; Ardens déclare aussi `.arduboy` |
| Uzebox | [Libretro — Uzebox](https://buildbot.libretro.com/assets/cores/Uzebox/) | Uzem | Fichier `.uze` |
| VaporSpec | [Libretro — VaporSpec](https://buildbot.libretro.com/assets/cores/VaporSpec/) | VaporSpec | Fichier `.vaporbin` |
| Aventures textuelles Z-Machine | [IF Archive — Z-code](https://ifarchive.org/indexes/if-archive/games/zcode/) | MojoZork | Le cœur installé déclare `.z1`, `.z3`, `.dat` : ne pas supposer tous les Z-code compatibles |
| Calculatrices TI | [ticalc.org — TI-83](https://www.ticalc.org/pub/83/) | Numero | Vérifier TI-83 / Plus / SE et les formats du cœur |
| Dingoo / Gemei | [Retroguru](https://www.retroguru.com/), [PDRoms](https://pdroms.de/files) | DingooEmu | Une version Dingux/Linux n’est pas nécessairement une application native A320 compatible |
| Java ME | Publications de jeux Java par leurs auteurs ; GameBrew/PDRoms comme pistes | SquirrelJME | Tous les anciens fichiers JAR ne sont pas garantis compatibles |
| Palm OS | Publications originales de logiciels Palm gratuits | Mu | Aucun pack de jeux vérifié ici ; système Palm requis selon configuration |
| BBK, Longman 4980, Wenquxing | Publications des projets et auteurs | BBKEmu, GAM4980, WQXEmu | Aucun catalogue fiable de jeux vérifié ici ; firmware souvent spécifique |
| Native32, Nicai, SPMP8000 | Publications des projets et auteurs | Native32Emu, NicaiEmu, SPMP8000Emu | Aucun pack vérifié ici |

**PICO-8 :** Retro8 est une réimplémentation dont la compatibilité est limitée ; la disponibilité d’une cartouche sur le site officiel ne garantit pas son fonctionnement dans ce cœur. [Documentation Retro8](https://docs.libretro.com/library/retro8/).

## 9. Télécharger et installer dans RetroArch

### Une organisation simple

Ton dossier prévu pour les jeux est `~/Jeux/ROMs/`. Tu peux créer uniquement les sous-dossiers dont tu as besoin :

```text
~/Jeux/ROMs/
├── Game Boy/
├── Game Boy Color/
├── Game Boy Advance/
├── NES/
├── Super Nintendo/
├── Nintendo 64/
├── Nintendo DS/
├── Mega Drive/
├── PlayStation/
├── PSP/
├── Dreamcast/
└── DOS/
```

Ce rangement est une convention pratique, pas une obligation de RetroArch. Les ROM peuvent se trouver dans tout dossier auquel l’application a accès. [Organisation des contenus](https://docs.libretro.com/guides/roms-playlists-thumbnails/).

### Télécharger un jeu depuis son auteur

1. Ouvre sa page et lis la section des fichiers disponibles.
2. Choisis l’édition de la console : par exemple **GBA ROM**, et non **Windows**.
3. Télécharge le fichier ou achète l’édition numérique si elle est payante.
4. Extrais le ZIP lorsque nécessaire et conserve le README.
5. Range le jeu dans le dossier de sa machine.
6. Pour une image de disque composée de plusieurs fichiers, conserve tout le sous-dossier.

La mention « Download now » sur itch.io peut ouvrir une proposition de don. Si la page propose explicitement de continuer sans payer, c’est l’option gratuite prévue par l’auteur. Pour un jeu vendu à prix minimum, cette option n’existe pas nécessairement.

### Premier lancement : méthode directe

Dans RetroArch :

1. **Menu principal → Charger un cœur**.
2. Sélectionne le cœur correspondant à la machine.
3. **Charger un contenu**.
4. Ouvre le fichier du jeu.

Pour ta Game Boy : **Nintendo - Game Boy / Color (Gambatte)**, puis ton fichier `.gb` ou `.gbc`. Cette méthode permet de vérifier le jeu avant de créer une bibliothèque.

### Ajouter un dossier à la bibliothèque

Pour des homebrews non reconnus par les bases de données, utilise **Importer du contenu → Analyse manuelle**. Renseigne le dossier, le système ou un nom personnalisé, et le cœur par défaut. Pour une sélection GB/GBC, le filtre d’extensions peut être `gb gbc`, sans points. Lance ensuite l’analyse. Les libellés exacts peuvent varier avec la traduction.

Une analyse automatique ne détecte pas forcément un homebrew récent ; cela ne signifie pas qu’il est inutilisable. [Importation](https://docs.libretro.com/guides/import-content/) et [fonctionnement des listes](https://docs.libretro.com/guides/roms-playlists-thumbnails/).

### Utiliser le catalogue intégré

RetroArch propose le **Téléchargeur de contenu** dans sa mise à jour en ligne. Le [catalogue web correspondant](https://buildbot.libretro.com/assets/cores/) permet de voir les plateformes disponibles. Ne pas confondre ce catalogue avec le téléchargement des **cœurs**, qui installe les émulateurs.

Dans ta configuration, le dossier de téléchargement est `~/.config/retroarch/downloads/`. Un fichier obtenu par ce moyen peut être rangé ensuite dans ton dossier ROMs, avant de créer sa liste de lecture.

## 10. BIOS, formats et problèmes courants

### Où vont les fichiers ?

| Élément | Emplacement dans ton installation |
|---|---|
| Jeux / ROM / images de disques | `~/Jeux/ROMs/`, organisé par machine |
| Émulateurs | `~/.config/retroarch/cores/` |
| BIOS et données système | `~/.config/retroarch/system/` |
| Sauvegardes des jeux | `~/.config/retroarch/saves/` |
| Sauvegardes instantanées | `~/.config/retroarch/states/` |

Les BIOS se vérifient **cœur par cœur** : nom, casse, dossier et parfois empreinte du fichier. L’indication « installé » d’un émulateur ne certifie pas qu’un BIOS est présent. [Centre de documentation BIOS Libretro](https://docs.libretro.com/library/bios/).

Le catalogue de [compléments système Libretro](https://buildbot.libretro.com/assets/system/) fournit certaines données distribuées par les projets. Il ne constitue pas un pack universel de BIOS de consoles.

### Extensions fréquentes

| Machine | Exemples de fichiers | Note |
|---|---|---|
| GB / GBC | `.gb`, `.gbc` | À ouvrir dans Gambatte |
| GBA | `.gba` | À ouvrir dans mGBA |
| NES | `.nes` | Mesen ; `.fds` correspond au Famicom Disk System |
| SNES | `.sfc`, `.smc` | Snes9x ou autre cœur SNES |
| N64 | `.z64`, `.n64`, `.v64` | Variantes de format d’une ROM N64 |
| DS | `.nds` | Fichiers annexes possibles pour certains homebrews |
| Master System / Game Gear | `.sms`, `.gg` | Bien distinguer les deux machines |
| Mega Drive | `.md`, `.bin`, `.gen` | L’extension `.bin` seule n’identifie pas la console |
| PS1 / Saturn / autres consoles CD | `.cue` + pistes, parfois `.chd` | Le support précis dépend du cœur |
| Dreamcast | `.gdi`, `.cdi`, `.chd` | Conserver les pistes associées au `.gdi` |
| PSP | `.pbp`, `.iso`, `.cso` | Les homebrews peuvent demander un dossier complet |
| GameCube / Wii | `.iso`, `.rvz`, `.dol`, `.elf` | Le format ne suffit pas à garantir le fonctionnement |
| DOS | Dossier de jeu ou `.zip` | Ouvrir avec DOSBox Pure, pas comme programme Linux |

Ce tableau donne des exemples ; **l’annexe contient les formats déclarés par les versions réellement installées**.

### Quelques vérifications utiles

| Problème | À vérifier d’abord |
|---|---|
| Le jeu n’apparaît pas après un scan | Essayer le chargement direct puis l’analyse manuelle |
| Écran noir | Cœur choisi, BIOS, fichiers annexes et exigences de la fiche du jeu |
| Image CD sans musique | Présence de toutes les pistes et chargement du fichier `.cue` |
| Un jeu « Game Boy » fournit seulement du HTML ou un EXE | Il s’agit peut-être d’un jeu navigateur/PC inspiré de la console |
| Le ZIP ne contient que des fichiers source | Chercher une version compilée dans les Releases ou sur la page de l’auteur |
| Le téléchargement est `.ips`, `.bps` ou `.xdelta` | C’est un correctif, pas un jeu complet ; lire les instructions de la publication |
| Un pack propose un installeur ou une extension de navigateur pour obtenir une ROM | Revenir au site du créateur et vérifier les fichiers réellement annoncés |

Les exécutables ne sont pas tous suspects par nature : un jeu DOS ou un homebrew PS1 peut avoir une extension `.exe`. Il faut connaître sa plateforme et l’ouvrir avec le logiciel approprié, plutôt que l’exécuter arbitrairement sur le PC.

## 11. Repères de stockage

Les chiffres suivants sont des **budgets indicatifs pour une sélection personnelle**, pas des tailles de bibliothèques complètes ni des mesures des packs cités. Compression, vidéos, pistes audio et variantes régionales changent beaucoup le résultat.

| Type de sélection | Budget de rangement indicatif |
|---|---:|
| Quelques dizaines de jeux GB/GBC, NES, Atari 2600 ou CHIP-8 | 10 à 100 Mo |
| Quelques dizaines de jeux SNES / Mega Drive | 100 Mo à 1 Go |
| Quelques dizaines de jeux GBA / N64 | 0,5 à 3 Go |
| Sélection DS ou jeux DOS | 1 à 10 Go, selon les titres |
| Une dizaine de jeux sur CD | Plusieurs Go ; plus si multidisques |
| Une dizaine de jeux PSP / PS2 / GameCube / Wii | De quelques Go à plusieurs dizaines de Go |
| Jeux PS3 / Wii U | Prévoir le stockage jeu par jeu ; certains titres occupent plusieurs dizaines de Go |

Pour commencer petit : choisir un jeu GB/GBC, une compilation Action 53, puis quelques autres titres qui t’intéressent. Aucun besoin de constituer une collection pour chacun des 178 cœurs : plusieurs émulateurs utilisent les mêmes fichiers.

## 12. Formats déclarés par tes 178 cœurs

Cette annexe est extraite des fichiers `.info` associés aux cœurs présents sur ton PC. Ce sont les **extensions annoncées**, pas une validation de toutes leurs fonctionnalités. Des BIOS, données annexes, réglages ou licences peuvent encore être nécessaires. Les sources de jeux sont regroupées par machine dans les sections précédentes ; elles ne dépendent généralement pas du choix entre deux émulateurs du même système.

| Cœur installé | Formats déclarés |
|---|---|
| Sinclair - ZX 81 (EightyOne) | `.p`, `.tzx`, `.t81` |
| Nintendo - Game Boy / Color (DoubleCherryGB) | `.cgb`, `.dmg`, `.gb`, `.gbc`, `.sgb` |
| Atari - 5200 (a5200) | `.a52`, `.bin` |
| Arcadia 2001 / Interton VC 4000 (AmiArcadia) | `.bin`, `.tvc` |
| Commodore - Amiga (Amiberry) | `.adf`, `.adz`, `.dms`, `.fdi`, `.raw`, `.ipf`, `.hdf`, `.hdz`, `.lha`, `.lzh`, `.zip`, `.7z`, `.uae`, `.rp9`, `.m3u`, `.m3u8`, `.iso`, `.cue`, `.ccd`, `.nrg`, `.mds`, `.chd` |
| Apple II (AppleWin) | `.bin`, `.do`, `.dsk`, `.nib`, `.po`, `.gz`, `.woz`, `.zip`, `.2mg`, `.2img`, `.iie`, `.apl`, `.hdv`, `.yaml`, `.m3u` |
| Arduboy (Ardens) | `.hex`, `.arduboy` |
| Arduboy (Arduous) | `.hex` |
| Atari - 400/800/600XL/800XL/130XE/5200 (Atari800) | `.xfd`, `.atr`, `.dcm`, `.cas`, `.bin`, `.a52`, `.zip`, `.atx`, `.car`, `.rom`, `.com`, `.xex`, `.m3u` |
| Nintendo - 3DS (Azahar) | `.3ds`, `.3dsx`, `.z3dsx`, `.elf`, `.axf`, `.cci`, `.zcci`, `.cxi`, `.zcxi`, `.app` |
| Acorn - BBC Micro (b2) | `.ssd`, `.dsd` |
| BBKEmu (BBK Electronic Dictionary) | `.gam` |
| Sega - MS/GG/MD/CD/32X (BlastEm) | `.md`, `.gen`, `.smd`, `.68k`, `.sgd`, `.32x`, `.sms`, `.gg`, `.sg`, `.sg1`, `.sc`, `.sc3`, `.sf7`, `.col`, `.cue`, `.toc`, `.iso`, `.chd`, `.vgm`, `.vgz`, `.flac`, `.wav`, `.bin`, `.rom`, `.gz` |
| MSX/SVI/ColecoVision/SG-1000 (blueMSX) | `.rom`, `.ri`, `.mx1`, `.mx2`, `.dsk`, `.col`, `.sg`, `.sc`, `.sf`, `.cas`, `.m3u` |
| Nintendo - SNES / SFC (bsnes-jg) | `.smc`, `.sfc`, `.st`, `.gb`, `.gbc`, `.bs` |
| Nintendo - SNES / SFC (bsnes 2014 Accuracy) | `.sfc`, `.smc`, `.bml`, `.gb`, `.gbc`, `.st`, `.bs` |
| Nintendo - SNES / SFC (bsnes 2014 Balanced) | `.sfc`, `.smc`, `.bml`, `.gb`, `.gbc`, `.st`, `.bs` |
| Nintendo - SNES / SFC (bsnes 2014 Performance) | `.sfc`, `.smc`, `.bml`, `.gb`, `.gbc`, `.st`, `.bs` |
| Nintendo - SNES / SFC (bsnes C++98 (v085)) | `.sfc`, `.smc`, `.gb`, `.gbc`, `.st`, `.bs` |
| Nintendo - SNES / SFC (bsnes-hd beta) | `.smc`, `.sfc`, `.swc`, `.fig`, `.gb`, `.gbc`, `.bs` |
| Nintendo - SNES / SFC (bsnes) | `.smc`, `.sfc`, `.swc`, `.fig`, `.gb`, `.gbc`, `.bs` |
| Nintendo - SNES / SFC (bsnes-mercury Accuracy) | `.sfc`, `.smc`, `.bml`, `.gb`, `.gbc`, `.st`, `.bs` |
| Nintendo - SNES / SFC (bsnes-mercury Balanced) | `.sfc`, `.smc`, `.bml`, `.gb`, `.gbc`, `.st`, `.bs` |
| Nintendo - SNES / SFC (bsnes-mercury Performance) | `.sfc`, `.smc`, `.bml`, `.gb`, `.gbc`, `.st`, `.bs` |
| Amstrad - CPC/GX4000 (Caprice32) | `.dsk`, `.sna`, `.zip`, `.tap`, `.cdt`, `.voc`, `.cpr`, `.m3u` |
| Philips CDi (CDi 2015) | `.chd` |
| Nintendo - Wii U (Cemu) | `.wud`, `.wux`, `.wua`, `.iso`, `.rpx`, `.elf`, `.tmd` |
| Nintendo - 3DS (Citra 2018) | `.3ds`, `.3dsx`, `.elf`, `.axf`, `.cci`, `.cxi`, `.app` |
| Nintendo - 3DS (Citra) | `.3ds`, `.3dsx`, `.elf`, `.axf`, `.cci`, `.cxi`, `.app` |
| Sega - MD/CD (ClownMDEmu) | `.bin`, `.md`, `.gen`, `.cue`, `.iso`, `.chd` |
| Amstrad - CPC (CrocoDS) | `.dsk`, `.sna`, `.kcr` |
| Nintendo - DS (DeSmuME 2015) | `.nds`, `.ids`, `.bin` |
| Nintendo - DS (DeSmuME) | `.nds`, `.ids`, `.bin` |
| Dingoo A320 / Gemei A330 (DingooEmu) | `.app`, `.cc`, `.c2s`, `.c3s` |
| Nintendo - GameCube / Wii (Dolphin) | `.gcm`, `.iso`, `.wbfs`, `.ciso`, `.gcz`, `.elf`, `.dol`, `.dff`, `.tgc`, `.wad`, `.rvz`, `.m3u`, `.wia` |
| DOS (DOSBox-core) | `.exe`, `.com`, `.bat`, `.conf`, `.cue`, `.iso`, `.img`, `./` |
| DOS (DOSBox) | `.exe`, `.com`, `.bat`, `.conf` |
| DOS (DOSBox-Pure) | `.zip`, `.dosz`, `.exe`, `.com`, `.bat`, `.iso`, `.chd`, `.cue`, `.ins`, `.img`, `.ima`, `.vhd`, `.jrc`, `.tc`, `.m3u`, `.m3u8`, `.conf`, `./` |
| DOS (DOSBox-SVN) | `.exe`, `.com`, `.bat`, `.conf`, `.cue`, `.iso`, `.img`, `./` |
| EPOCH/YENO Super Cassette Vision (EmuSCV) | `.cart`, `.bin`, `.rom`, `.0`, `.zip` |
| Enterprise - 64/128 (ep128emu) | `.img`, `.dsk`, `.tap`, `.dtf`, `.com`, `.trn`, `.128`, `.bas`, `.cas`, `.cdt`, `.tzx`, `.wav`, `.tvcwav`, `..` |
| Nintendo - NES / Famicom (FCEUmm) | `.fds`, `.nes`, `.unif`, `.unf` |
| Nintendo - Game Boy / Color (fixGB) | `.gb`, `.gbc`, `.gbs` |
| Nintendo - NES / Famicom (fixNES) | `.nes`, `.fds`, `.qd`, `.nsf` |
| Sega - Dreamcast/Naomi (Flycast) | `.chd`, `.cdi`, `.elf`, `.bin`, `.cue`, `.gdi`, `.lst`, `.zip`, `.rar`, `.dat`, `.7z`, `.m3u` |
| Microsoft - MSX (fMSX) | `.rom`, `.mx1`, `.mx2`, `.dsk`, `.fdi`, `.cas`, `.m3u` |
| Fairchild - ChannelF (FreeChaF) | `.bin`, `.chf` |
| Mattel - Intellivision (FreeIntv) | `.int`, `.bin`, `.rom` |
| Commodore - C64 (Frodo) | `.d64`, `.t64`, `.x64`, `.p00`, `.lnx`, `.lyx`, `.zip` |
| Commodore - Amiga (FS-UAE) | `.adf`, `.ipf`, `.fs-uae` |
| Sinclair - ZX Spectrum (Fuse) | `.tzx`, `.tap`, `.z80`, `.rzx`, `.scl`, `.trd`, `.dsk`, `.dck`, `.sna`, `.szx`, `.zip`, `.ipf` |
| Elektronika Inženjering - Galaksija (Galaksija) | `.gal` |
| GAM4980 | `.gam` |
| Nintendo - Game Boy / Color (Gambatte) | `.gb`, `.gbc`, `.dmg` |
| Nintendo - Game Boy / Color / Super Game Boy (Gearboy) | `.gb`, `.dmg`, `.gbc`, `.cgb`, `.sgb` |
| Coleco - ColecoVision / ADAM (Gearcoleco) | `.col`, `.cv`, `.bin`, `.rom`, `.zip`, `.ddp`, `.dsk`, `.m3u` |
| NEC - PC Engine / SuperGrafx / CD / LaserActive (Geargrafx) | `.pce`, `.sgx`, `.hes`, `.cue`, `.chd`, `.mmi` |
| Atari - Lynx (Gearlynx) | `.lnx`, `.lyx`, `.o`, `.bin` |
| Sega - MS/GG/SG-1000 (Gearsystem) | `.sms`, `.gg`, `.sg`, `.mv`, `.bin`, `.rom` |
| Sega - MS/GG/MD/CD (Genesis Plus GX) | `.mdx`, `.md`, `.smd`, `.gen`, `.bin`, `.cue`, `.iso`, `.sms`, `.bms`, `.gg`, `.sg`, `.68k`, `.sgd`, `.chd`, `.m3u` |
| Sega - MS/GG/MD/CD (Genesis Plus GX Wide) | `.mdx`, `.md`, `.smd`, `.gen`, `.bin`, `.cue`, `.iso`, `.sms`, `.bms`, `.gg`, `.sg`, `.68k`, `.sgd`, `.chd`, `.m3u` |
| SNK - Neo Geo AES/MVS/CD (Geolith) | `.neo`, `.cue`, `.chd` |
| Nintendo - Game Boy Advance (gpSP) | `.gba`, `.bin` |
| Handheld Electronic (GW) | `.mgw` |
| Atari - Lynx (Handy) | `.lnx`, `.lyx`, `.o` |
| Atari - ST / STE / TT / Falcon (Hatari 2014) | `.st`, `.msa`, `.zip`, `.stx`, `.dim`, `.ipf`, `.vhd`, `.gem`, `.ide`, `.m3u` |
| Atari - ST / STE / TT / Falcon (Hatari) | `.st`, `.msa`, `.zip`, `.stx`, `.dim`, `.ipf`, `.vhd`, `.gem`, `.ide`, `.m3u` |
| Atari - ST/STE/TT/Falcon (hatariB) | `.st`, `.msa`, `.dim`, `.stx`, `.ipf`, `.ctr`, `.m3u`, `.m3u8`, `.zip`, `.zst`, `.gz`, `.acsi`, `.ahd`, `.vhd`, `.scsi`, `.shd`, `.ide`, `.gem` |
| Atari - Lynx (Holani) | `.lnx`, `.o` |
| Nintendo - Game Boy / Color (IroGB) | `.gb`, `.gbc`, `.dmg`, `.cgb` |
| CHIP-8/S-CHIP/XO-CHIP (JAXE) | `.ch8`, `.sc8`, `.xo8` |
| ColecoVision/CreatiVision/My Vision (JollyCV) | `.col`, `.rom`, `.myv`, `.bin` |
| Sega - Saturn/ST-V (Kronos) | `.ccd`, `.chd`, `.cue`, `.iso`, `.mds`, `.zip`, `.m3u` |
| Philips - P2000T (M2000) | `.cas` |
| Nintendo - Game Boy Advance (Beetle GBA) | `.gba`, `.agb`, `.bin` |
| Atari - Lynx (Beetle Lynx) | `.lnx`, `.lyx`, `.bll`, `.o` |
| SNK - Neo Geo Pocket / Color (Beetle NeoPop) | `.ngp`, `.ngc`, `.ngpc`, `.npc` |
| NEC - PC Engine / CD (Beetle PCE FAST) | `.pce`, `.cue`, `.ccd`, `.chd`, `.toc`, `.m3u` |
| NEC - PC Engine / SuperGrafx / CD (Beetle PCE) | `.pce`, `.sgx`, `.cue`, `.ccd`, `.chd`, `.toc`, `.m3u` |
| NEC - PC-FX (Beetle PC-FX) | `.cue`, `.ccd`, `.toc`, `.chd` |
| Sony - PlayStation (Beetle PSX HW) | `.cue`, `.toc`, `.m3u`, `.ccd`, `.exe`, `.pbp`, `.chd`, `.bin` |
| Sony - PlayStation (Beetle PSX) | `.cue`, `.toc`, `.m3u`, `.ccd`, `.exe`, `.pbp`, `.chd`, `.bin` |
| Sega - Saturn (Beetle Saturn) | `.ccd`, `.chd`, `.cue`, `.toc`, `.m3u`, `.zip` |
| Nintendo - SNES / SFC (Beetle bsnes) | `.smc`, `.fig`, `.bs`, `.st`, `.sfc` |
| Nintendo - SNES / SFC (Beetle Supafaust) | `.smc`, `.fig`, `.sfc`, `.gd3`, `.gd7`, `.dx2`, `.bsx`, `.swc` |
| NEC - PC Engine SuperGrafx (Beetle SuperGrafx) | `.pce`, `.sgx`, `.cue`, `.ccd`, `.chd` |
| Nintendo - Virtual Boy (Beetle VB) | `.vb`, `.vboy`, `.bin` |
| Bandai - WonderSwan/Color (Beetle Wonderswan) | `.ws`, `.wsc`, `.pc2`, `.pcv2` |
| Nintendo - DS (melonDS) | `.nds`, `.ids`, `.dsi` |
| Nintendo - DS (melonDS DS) | `.nds`, `.ids`, `.dsi` |
| Nintendo - SNES / SFC / Game Boy / Color (Mesen-S) | `.sfc`, `.smc`, `.fig`, `.swc`, `.bs`, `.gb`, `.gbc` |
| Nintendo - NES / FC / FDS / SNES / SFC / GB / GBC / GBA / NEC - PCE / PCE-CD / Sega - SMS / GG / Bandai - Wswan (MesenCE) | `.sfc`, `.smc`, `.fig`, `.swc`, `.bs`, `.gb`, `.gbc`, `.gba`, `.pce`, `.cue`, `.nes`, `.sms`, `.fc`, `.fds`, `.unf`, `.unif`, `.ws`, `.wsc`, `.pc2`, `.pcv2`, `.sms`, `.gg`, `.sg`, `.mv` |
| Nintendo - NES / Famicom (Mesen) | `.nes`, `.fds`, `.unf`, `.unif` |
| Nintendo - Game Boy Advance (Meteor) | `.gba` |
| Nintendo - Game Boy Advance (mGBA) | `.gb`, `.gbc`, `.gba` |
| Mac II (minivmac) | `.dsk`, `.img`, `.zip`, `.hvf`, `.cmd` |
| Infocom Z-Machine (MojoZork) | `.dat`, `.z1`, `.z3` |
| Palm OS (Mu) | `.prc`, `.pqa`, `.img`, `.pdb`, `.zip` |
| Nintendo - Nintendo 64 (Mupen64Plus-Next) | `.n64`, `.v64`, `.z64`, `.ndd`, `.bin`, `.u1` |
| Native32 (Native32Emu) | `.smf`, `.sgm`, `.ssl`, `.zip` |
| NEC - PC-98 (Neko Project II) | `.d98`, `.zip`, `.98d`, `.fdi`, `.fdd`, `.2hd`, `.tfd`, `.d88`, `.88d`, `.hdm`, `.xdf`, `.dup`, `.cmd`, `.hdi`, `.thd`, `.nhd`, `.hdd` |
| SNK - Neo Geo CD (NeoCD) | `.cue`, `.chd` |
| Nintendo - NES / Famicom (Nestopia) | `.nes`, `.fds`, `.unf`, `.unif`, `.nsf` |
| Nicai (NicaiEmu) | `.cbe` |
| Nintendo - DS (NooDS) | `.nds`, `.gba` |
| NEC - PC-98 (Neko Project II Kai) | `.d98`, `.zip`, `.98d`, `.fdi`, `.fdd`, `.2hd`, `.tfd`, `.d88`, `.88d`, `.hdm`, `.xdf`, `.dup`, `.cmd`, `.hdi`, `.thd`, `.nhd`, `.hdd`, `.hdn` |
| Nintendo - SNES / SFC (nSide Balanced) | `.sfc`, `.smc`, `.gb`, `.gbc`, `.bml`, `.rom` |
| VM Labs - NUON (Nuance) | `.run`, `.cof`, `.nuon`, `.cd`, `.iso`, `.img`, `.chd` |
| Texas Instruments TI-83 (Numero) | `.8xp`, `.8xk`, `.8xg` |
| Magnavox - Odyssey2 / Philips Videopac+ (O2EM) | `.bin` |
| Oberon RISC Emulator | `.dsk` |
| The 3DO Company - 3DO (Opera) | `.iso`, `.bin`, `.chd`, `.cue` |
| Nintendo - 3DS (Panda3DS) | `.3ds`, `.3dsx`, `.elf`, `.axf`, `.cci`, `.cxi`, `.app` |
| Nintendo - Nintendo 64 (ParaLLEl N64) | `.n64`, `.v64`, `.z64`, `.bin`, `.u1`, `.ndd` |
| Sony - PlayStation 2 (PCEE2) | `.iso`, `.chd`, `.cso`, `.zso`, `.gz`, `.bin`, `.mdf`, `.nrg`, `.elf`, `.irx` |
| PC (PCem) | `.exe`, `.com`, `.bat`, `.conf` |
| Sony - PlayStation 2 (LRPS2) | `.elf`, `.iso`, `.ciso`, `.cue`, `.bin`, `.gz`, `.chd`, `.cso`, `.zso`, `.mdf`, `.nrg`, `.dump`, `.img`, `.m3u` |
| Sony - PlayStation (PCSX ReARMed) | `.bin`, `.cue`, `.img`, `.mdf`, `.pbp`, `.toc`, `.cbn`, `.m3u`, `.ccd`, `.chd`, `.iso`, `.exe` |
| Epoch - Cassette Vision (PD777) | `.zip`, `.bin777`, `.ptn777` |
| Sega - MS/GG/MD/CD/32X (PicoDrive) | `.bin`, `.gen`, `.smd`, `.md`, `.32x`, `.cue`, `.iso`, `.chd`, `.sms`, `.gg`, `.sg`, `.sc`, `.m3u`, `.68k`, `.sgd`, `.pco` |
| Sony - PlayStation 2 (Play!) | `.chd`, `.cso`, `.cue`, `.elf`, `.iso`, `.isz` |
| Playdia (PlaydiaEmu) | `.cue`, `.zip`, `.iso`, `.bin` |
| Nintendo - Pokemon Mini (PokeMini) | `.min` |
| Sony - PocketStation (pokketstation) | `.bin`, `.gme`, `.mcr`, `.mcs`, `.pss` |
| Watara - Supervision (Potator) | `.bin`, `.sv` |
| Sony - PlayStation Portable (PPSSPP) | `.elf`, `.iso`, `.cso`, `.prx`, `.pbp`, `.chd` |
| Atari - 7800 (ProSystem) | `.a78`, `.bin`, `.cdf` |
| Commodore - Amiga (PUAE 2021) | `.adf`, `.adz`, `.dms`, `.fdi`, `.ipf`, `.hdf`, `.hdz`, `.lha`, `.slave`, `.info`, `.cue`, `.ccd`, `.nrg`, `.mds`, `.iso`, `.chd`, `.uae`, `.m3u`, `.zip`, `.7z`, `.rp9`, `./` |
| Commodore - Amiga (PUAE) | `.adf`, `.adz`, `.dms`, `.fdi`, `.ipf`, `.hdf`, `.hdz`, `.lha`, `.slave`, `.info`, `.cue`, `.ccd`, `.nrg`, `.mds`, `.iso`, `.chd`, `.uae`, `.m3u`, `.zip`, `.7z`, `.rp9`, `./` |
| Sharp - X68000 (PX68k) | `.dim`, `.img`, `.d88`, `.88d`, `.hdm`, `.dup`, `.2hd`, `.xdf`, `.hdf`, `.cmd`, `.m3u` |
| QEMU | `.qemu_cmd_line`, `.iso`, `.img`, `.qcow`, `.qcow2` |
| NEC - PC-88 series (QUASI88) | `.d88`, `.u88`, `.m3u` |
| Nintendo - NES / Famicom (QuickNES) | `.nes` |
| SNK - Neo Geo Pocket / Color (RACE) | `.ngp`, `.ngc`, `.ngpc`, `.npc` |
| PICO-8 (Retro8) | `.p8`, `.png` |
| Sony - PlayStation 3 (RPCS3) | `.bin`, `.self`, `.elf`, `.iso`, `.pkg`, `.sfo`, `.sfb` |
| Nintendo - NES / Famicom (RustyNES) | `.nes`, `.fds`, `.unf`, `.unif` |
| Philips - CDi (SAME CDi) | `.chd`, `.iso`, `.cue`, `.m3u` |
| Nintendo - Game Boy / Color (SameBoy) | `.gb`, `.gbc` |
| Mega Duck / Cougar Boy (SameDuck) | `.bin`, `.duck` |
| Nintendo - Game Boy/GBA/NDS (SkyEmu) | `.gb`, `.gbx`, `.gba`, `.nds` |
| Sega - MS/GG (SMS Plus GX) | `.sms`, `.bin`, `.rom`, `.col`, `.gg`, `.sg` |
| Nintendo - SNES / SFC (Snes9x 2002) | `.smc`, `.fig`, `.sfc`, `.gd3`, `.gd7`, `.dx2`, `.bsx`, `.swc` |
| Nintendo - SNES / SFC (Snes9x 2005) | `.smc`, `.fig`, `.sfc`, `.gd3`, `.gd7`, `.dx2`, `.bsx`, `.swc` |
| Nintendo - SNES / SFC (Snes9x 2005 Plus) | `.smc`, `.fig`, `.sfc`, `.gd3`, `.gd7`, `.dx2`, `.bsx`, `.swc` |
| Nintendo - SNES / SFC (Snes9x 2010) | `.smc`, `.fig`, `.sfc`, `.gd3`, `.gd7`, `.dx2`, `.bsx`, `.swc` |
| Nintendo - SNES / SFC (Snes9x) | `.smc`, `.sfc`, `.swc`, `.fig`, `.bs`, `.st` |
| SPMP8000 (SPMP8000Emu) | `.bin` |
| Java ME (SquirrelJME) | `.jar`, `.sqc`, `.jam`, `.jad`, `.kjx`, `.adf`, `.sec`, `.sto`, `.sp`, `.sp0`, `.sp1`, `.sp2`, `.sp3`, `.sp4`, `.sp5`, `.sp6`, `.sp7`, `.sp8`, `.sp9` |
| Atari - 2600 (Stella 2014) | `.a26`, `.bin` |
| Atari - 2600 (Stella 2023) | `.a26`, `.bin` |
| Atari - 2600 (Stella) | `.a26`, `.bin` |
| Sega - Model 3 (Supermodel) | `.zip`, `.chd`, `.7z` |
| Sony - PlayStation (SwanStation) | `.exe`, `.psexe`, `.cue`, `.bin`, `.img`, `.iso`, `.chd`, `.pbp`, `.ecm`, `.mds`, `.psf`, `.m3u` |
| Bandai - Tamagotchi P1 (TamaLIBretro) | `.b`, `.bin`, `.rom` |
| Nintendo - Game Boy / Color (TGB Dual) | `.cgb`, `.dmg`, `.gb`, `.gbc`, `.sgb` |
| Thomson - MO/TO (Theodore) | `.fd`, `.sap`, `.k7`, `.m7`, `.m5`, `.rom` |
| Atari - 2600 (Tia) | `.a26`, `.bin` |
| Uzebox (Uzem) | `.uze` |
| VaporSpec | `.vaporbin` |
| Nintendo - Game Boy Advance (VBA Next) | `.gba` |
| Nintendo - Game Boy Advance (VBA-M) | `.dmg`, `.gb`, `.gbc`, `.cgb`, `.sgb`, `.gba` |
| GCE - Vectrex (vecx) | `.bin`, `.vec` |
| Commodore - C128 (VICE x128) | `.d64`, `.d71`, `.d80`, `.d81`, `.d82`, `.g64`, `.g41`, `.x64`, `.t64`, `.tap`, `.prg`, `.p00`, `.crt`, `.bin`, `.zip`, `.gz`, `.d6z`, `.d7z`, `.d8z`, `.g6z`, `.g4z`, `.x6z`, `.cmd`, `.m3u`, `.vfl`, `.vsf`, `.nib`, `.nbz`, `.d2m`, `.d4m`, `./` |
| Commodore - C64 (VICE x64, fast) | `.d64`, `.d71`, `.d80`, `.d81`, `.d82`, `.g64`, `.g41`, `.x64`, `.t64`, `.tap`, `.prg`, `.p00`, `.crt`, `.bin`, `.zip`, `.gz`, `.d6z`, `.d7z`, `.d8z`, `.g6z`, `.g4z`, `.x6z`, `.cmd`, `.m3u`, `.vfl`, `.vsf`, `.nib`, `.nbz`, `.d2m`, `.d4m`, `./` |
| Commodore - C64 (VICE x64sc, accurate) | `.d64`, `.d71`, `.d80`, `.d81`, `.d82`, `.g64`, `.g41`, `.x64`, `.t64`, `.tap`, `.prg`, `.p00`, `.crt`, `.bin`, `.zip`, `.gz`, `.d6z`, `.d7z`, `.d8z`, `.g6z`, `.g4z`, `.x6z`, `.cmd`, `.m3u`, `.vfl`, `.vsf`, `.nib`, `.nbz`, `.d2m`, `.d4m`, `./` |
| Commodore - CBM-II 6x0/7x0 (VICE xcbm2) | `.d64`, `.d71`, `.d80`, `.d81`, `.d82`, `.g64`, `.g41`, `.x64`, `.t64`, `.tap`, `.prg`, `.p00`, `.crt`, `.bin`, `.zip`, `.gz`, `.d6z`, `.d7z`, `.d8z`, `.g6z`, `.g4z`, `.x6z`, `.cmd`, `.m3u`, `.vfl`, `.vsf`, `.nib`, `.nbz`, `.d2m`, `.d4m`, `./` |
| Commodore - CBM-II 5x0 (VICE xcbm5x0) | `.d64`, `.d71`, `.d80`, `.d81`, `.d82`, `.g64`, `.g41`, `.x64`, `.t64`, `.tap`, `.prg`, `.p00`, `.crt`, `.bin`, `.zip`, `.gz`, `.d6z`, `.d7z`, `.d8z`, `.g6z`, `.g4z`, `.x6z`, `.cmd`, `.m3u`, `.vfl`, `.vsf`, `.nib`, `.nbz`, `.d2m`, `.d4m`, `./` |
| Commodore - PET (VICE xpet) | `.d64`, `.d71`, `.d80`, `.d81`, `.d82`, `.g64`, `.g41`, `.x64`, `.t64`, `.tap`, `.prg`, `.p00`, `.crt`, `.bin`, `.zip`, `.gz`, `.d6z`, `.d7z`, `.d8z`, `.g6z`, `.g4z`, `.x6z`, `.cmd`, `.m3u`, `.vfl`, `.vsf`, `.nib`, `.nbz`, `.d2m`, `.d4m`, `./` |
| Commodore - PLUS/4 (VICE xplus4) | `.d64`, `.d71`, `.d80`, `.d81`, `.d82`, `.g64`, `.g41`, `.x64`, `.t64`, `.tap`, `.prg`, `.p00`, `.crt`, `.bin`, `.zip`, `.gz`, `.d6z`, `.d7z`, `.d8z`, `.g6z`, `.g4z`, `.x6z`, `.cmd`, `.m3u`, `.vfl`, `.vsf`, `.nib`, `.nbz`, `.d2m`, `.d4m`, `./` |
| Commodore - C64 SuperCPU (VICE xscpu64) | `.d64`, `.d71`, `.d80`, `.d81`, `.d82`, `.g64`, `.g41`, `.x64`, `.t64`, `.tap`, `.prg`, `.p00`, `.crt`, `.bin`, `.zip`, `.gz`, `.d6z`, `.d7z`, `.d8z`, `.g6z`, `.g4z`, `.x6z`, `.cmd`, `.m3u`, `.vfl`, `.vsf`, `.nib`, `.nbz`, `.d2m`, `.d4m`, `./` |
| Commodore - VIC-20 (VICE xvic) | `.d64`, `.d71`, `.d80`, `.d81`, `.d82`, `.g64`, `.g41`, `.x64`, `.t64`, `.tap`, `.prg`, `.p00`, `.crt`, `.bin`, `.zip`, `.gz`, `.d6z`, `.d7z`, `.d8z`, `.g6z`, `.g4z`, `.x6z`, `.cmd`, `.m3u`, `.vfl`, `.vsf`, `.nib`, `.nbz`, `.d2m`, `.d4m`, `.20`, `.40`, `.60`, `.a0`, `.b0`, `.rom`, `./` |
| Atari - Jaguar (Virtual Jaguar) | `.j64`, `.jag`, `.rom`, `.abs`, `.cof`, `.bin`, `.prg`, `.cue`, `.cdi`, `.chd` |
| VirtualXT | `.img`, `.zip` |
| Wenquxing (WQXEmu) | Non renseignés dans les métadonnées |
| Sega - Saturn (YabaSanshiro) | `.bin`, `.ccd`, `.chd`, `.cue`, `.iso`, `.mds`, `.zip` |
| Sega - Saturn (Yabause) | `.bin`, `.ccd`, `.chd`, `.cue`, `.iso`, `.mds`, `.zip`, `.m3u` |
| Sega - Saturn (Emir) | `.cue`, `.chd`, `.mds`, `.ccd`, `.iso`, `.m3u` |
