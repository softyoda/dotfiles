# Dotfiles — CachyOS / Arch + KDE Plasma

Mon environnement découpé en **modules** : chaque fonctionnalité (Snap Assist,
bouton power sans confirmation, F9 = lecture/pause, manettes Xbox, montage NTFS
propre, worker Immich GPU, Spicetify, Vesktop, Mullvad, ES-DE…) s'installe,
se met à jour et se vérifie séparément, sur n'importe quelle machine.

Ce repo sert aussi d'**aide-mémoire** : la liste des modules ci-dessous dit ce
que j'ai déjà mis au point et comment (voir le `README.md` de chaque module).

## Démarrage

```bash
git clone https://github.com/softyoda/dotfiles.git ~/dotfiles
bash ~/dotfiles/install.sh
```

`install.sh` installe l'appli **Dotfiles** (menu + icône de notification) puis l'ouvre :

- **Nouvelle installation** : tous les modules du profil de la machine sont cochés.
- **Mises à jour** : seulement ce qui n'est pas à jour (module modifié dans le repo,
  pas encore installé, ou modifié localement).

L'icône de notification synchronise le repo toutes les 6 h, signale les modules
à mettre à jour et les **secrets qui vont expirer**.

## En ligne de commande (SSH, agent IA…)

```bash
dotctl list                  # catalogue
dotctl info snap-assist      # détail + notes d'un module
dotctl status [--all]        # état sur cette machine
dotctl apply mullvad vesktop # installer / mettre à jour
dotctl apply --profile       # tout le profil de la machine
dotctl diff fish-shell       # différences repo ↔ machine
dotctl capture fish-shell    # remonter dans le repo une modif faite sur la machine
dotctl sync                  # git pull
```

## Public / privé

| | Où | Contenu |
|---|---|---|
| **Public** | ce repo | modules génériques, aucun secret, aucune valeur propre à mon réseau |
| **Privé** | bibliothèque Seafile **chiffrée** `dotfiles-private` | `hosts/<hostname>.toml` (modules + variables : NAS, IP, chemins…), `secrets.env`, clés publiques |
| **Local** | `~/.config/dotfiles/secrets.env` | surcharge locale des secrets (optionnel) |

Profil machine (`hosts/<hostname>.toml`) :

```toml
modules = ["base-system", "kde-theme", "snap-assist", "immich-worker"]

[vars]
NAS_HOST = "nas.local"
IMMICH_URL = "https://photos.example.org"
```

`secrets.env` :

```bash
IMMICH_DB_PASSWORD=…
HF_TOKEN=hf_…   # expire: 2027-01-31   ← l'icône prévient 3 semaines avant
```

Sans dossier privé, tout fonctionne quand même ; les modules qui ont besoin
d'une variable manquante sont simplement ignorés avec un message.

## Écrire un module

Voir [`modules/README.md`](modules/README.md) : un dossier, un `module.toml`
(paquets, fichiers, variables), un `apply.sh` idempotent, un `check.sh` optionnel.
Les applis « juste un paquet » vont dans [`catalog/apps.toml`](catalog/apps.toml).

Après ajout d'un module : `dotctl list --md` régénère le catalogue ci-dessous
(`bin/update-readme`).

## Catalogue

<!-- modules -->

### Système de base

| Module | Ce que ça fait |
|---|---|
| [`autologin`](modules/autologin/) | Ouvre automatiquement la session de l'utilisateur au démarrage (Plasma Login Manager). ✋ |
| [`base-system`](modules/base-system/) | Prépare le système : paru, Flathub, pacman plus rapide et coloré, paru sans revue des PKGBUILD, mot de passe sudo graphique (ksshaskpass). |
| [`cache-cleanup`](modules/cache-cleanup/) | Supprime chaque jour les paquets en cache (pacman et paru) de plus de 7 jours. |
| [`cachy-update`](modules/cachy-update/) | Ajoute le choix « A » à Cachy-Update : mise à jour complète (pacman, AUR, Flatpak, nettoyages) sans confirmations. |
| [`dns-over-tls`](modules/dns-over-tls/) | Résolution DNS chiffrée via Cloudflare et Quad9 (systemd-resolved, DNS over TLS). |
| [`docker-nvidia`](modules/docker-nvidia/) | Docker avec accès au GPU NVIDIA dans les conteneurs (nvidia-container-toolkit), utilisateur dans le groupe docker. |
| [`dotfiles-app`](modules/dotfiles-app/) | Commande `dotctl`, entrée « Dotfiles » dans le menu et icône de notification qui synchronise le repo et signale les mises à jour et les secrets qui expirent. |
| [`fish-shell`](modules/fish-shell/) | fish comme shell par défaut, avec la config CachyOS, le prompt Pure, fzf (Ctrl+R/Ctrl+T) et les secrets dans un fichier local. |
| [`plymouth-theme`](modules/plymouth-theme/) | Écran de démarrage « Cogwheel spinner » : roue crantée animée et barre de progression pendant le boot. ✋ |
| [`terminals`](modules/terminals/) | WezTerm (thème Tokyo Night, JetBrains Mono, clic droit = coller) et profil Konsole (copie à la sélection, historique de 100 000 lignes). |

### KDE Plasma

| Module | Ce que ça fait |
|---|---|
| [`kde-shortcuts`](modules/kde-shortcuts/) | Raccourcis globaux : Meta+C bascule le cube, Meta+A / Meta+Maj+A parcourent les activités, Ctrl+Alt+T n'ouvre plus Konsole. |
| [`kde-theme`](modules/kde-theme/) | Apparence complète du bureau : thème We10XOS sombre, accent gris, icônes We10X, effets KWin (verre, flou, fenêtres molles), splash Watch_Dogs et fond d'écran flouté en diaporama. ✋ |
| [`media-key-f9`](modules/media-key-f9/) | La touche F9 met en pause ou relance la musique/vidéo en cours, pour les claviers sans touches multimédia. |
| [`mission-center-shortcut`](modules/mission-center-shortcut/) | Le raccourci Ctrl+Maj+Échap ouvre Mission Center (moniteur système), comme le gestionnaire de tâches de Windows. |
| [`power-button`](modules/power-button/) | Le bouton d'alimentation éteint immédiatement, sans dialogue ni inhibition. |
| [`snap-assist`](modules/snap-assist/) | Quand on colle une fenêtre sur un bord, propose les autres fenêtres pour remplir le reste (comme Windows). |
| [`touchpad-gestures`](modules/touchpad-gestures/) | Gestes multi-doigts façon macOS/Windows : 3 doigts pour précédent/suivant, vue d'ensemble et grille ; 4 doigts pour minimiser/agrandir et changer de bureau. |

### Matériel

| Module | Ce que ça fait |
|---|---|
| [`hdmi-tv-recovery`](modules/hdmi-tv-recovery/) | Quand la TV HDMI reste « sans signal » (au rallumage ou en changeant d'entrée), le signal est relancé tout seul ; Alt+F9 force une re-détection. |
| [`ntfs-automount`](modules/ntfs-automount/) | Les disques externes NTFS (Windows) se montent tout seuls au branchement, en lecture-écriture et au nom de l'utilisateur. |
| [`usb-no-autosuspend`](modules/usb-no-autosuspend/) | Désactive la mise en veille automatique des périphériques USB (évite les souris, claviers, DAC ou dongles qui décrochent). |
| [`xbox-controllers`](modules/xbox-controllers/) | Manettes Xbox en Bluetooth (xpadneo) et via le dongle sans fil Xbox (xone), avec un Bluetooth stable pour les manettes. |

### Applications

| Module | Ce que ça fait |
|---|---|
| [`firefox-second-profile`](modules/firefox-second-profile/) | Un profil Firefox séparé (marque-pages, mots de passe, sessions) avec son propre lanceur « Firefox (<nom>) » dans le menu. |
| [`flatpakref-handler`](modules/flatpakref-handler/) | Un double-clic sur un fichier .flatpakref lance l'installation Flatpak correspondante. |
| [`mullvad`](modules/mullvad/) | VPN Mullvad connecté automatiquement (sortie en Belgique, WireGuard post-quantique + DAITA, LAN accessible), interface démarrée réduite. ✋ |
| [`rustdesk`](modules/rustdesk/) | Bureau à distance RustDesk en service système : accessible sans session ouverte, avec mot de passe permanent. ✋ |
| [`seafile`](modules/seafile/) | Client de synchronisation Seafile (Flatpak) pointant sur le serveur du profil, démarré au login sans fenêtre. ✋ |
| [`spicetify`](modules/spicetify/) | Spotify (Flatpak utilisateur) personnalisé par Spicetify avec le Marketplace, ré-appliqué automatiquement après chaque mise à jour de Spotify. |
| [`vesktop`](modules/vesktop/) | Client Discord Vesktop (Vencord intégré), démarré réduit dans la barre système, hors VPN Mullvad, gestionnaire des liens discord://. |

### IA & agents

| Module | Ce que ça fait |
|---|---|
| [`claude-code`](modules/claude-code/) | Installe Claude Code (installeur natif officiel) avec ma config, l’agent gemini et un shell nettoyé des variables API pour utiliser l’abonnement. ✋ |
| [`codex`](modules/codex/) | Installe Codex CLI d’OpenAI (paquet CachyOS) avec le grand contexte, à utiliser avec l’abonnement ChatGPT. ✋ |
| [`opencode-poe`](modules/opencode-poe/) | Installe OpenCode, réservé aux modèles Poe, avec la config partagée du NAS (liens) ou une copie autonome sans NAS. ✋ |
| [`paseo`](modules/paseo/) | Une seule interface (bureau + mobile) pour piloter les agents Claude Code, Codex et OpenCode, chacun avec son abonnement. ✋ |

### Création

| Module | Ce que ça fait |
|---|---|
| [`helios-laser`](modules/helios-laser/) | Pilotage d'un DAC laser Helios en USB depuis TouchDesigner : règle udev, bibliothèque SDK compilée, pont UDP vers USB en service utilisateur et scripts d'envoi côté TouchDesigner. |
| [`metashape`](modules/metashape/) | Photogrammétrie Agisoft Metashape Professional 2.1.3 dans /opt/metashape-pro, lanceurs (Metashape, Viewer, Network Monitor) et commande fish « metashape ». ✋ |
| [`mixxx-rgb`](modules/mixxx-rgb/) | Mixxx 2.5.6 recompilé avec des formes d'onde RGB façon Rekordbox (patch maison), installé dans ~/.local/opt, avec raccourcis clavier perso, alias Espace → lecture et lanceur XWayland. |
| [`orcaslicer-waveoverhangs`](modules/orcaslicer-waveoverhangs/) | Fork d'OrcaSlicer avec surplombs en vagues (impression de surplombs à 90° sans support), en AppImage téléchargé et lancé sur le GPU dédié. |
| [`touchdesigner`](modules/touchdesigner/) | TouchDesigner Windows lancé sous Wine : lanceur Wayland/XWayland qui injecte automatiquement les correctifs d'interface dans les projets .toe, associations de fichiers .toe/.tox et icônes. ✋ |
| [`wine`](modules/wine/) | Wine TkG staging en wow64 (un seul préfixe 64 bits pour les applis 32 et 64 bits), lanceur de réglages et surcharges DLL ddraw/dinput natives pour les vieux jeux. |

### Rétro & salon

| Module | Ce que ça fait |
|---|---|
| [`es-de-retroarch`](modules/es-de-retroarch/) | Frontend ES-DE (thème Aura) branché sur RetroArch : systèmes personnalisés, collections multijoueur, manette Xbox, menu RetroArch épuré. Sans cœurs, BIOS ni ROMs. ✋ |
| [`retro-screensaver`](modules/retro-screensaver/) | Économiseur animé XScreenSaver (pipes, matrix, flurry…) avec menu clic droit du bureau et protection automatique pendant les jeux, films, musique et applis en plein écran. |

### NAS & homelab

| Module | Ce que ça fait |
|---|---|
| [`diskover`](modules/diskover/) | Moteur de recherche de fichiers Diskover Community en local (http://localhost:8000) : catalogue du poste et du NAS, rescan hebdomadaire automatique le dimanche à 04:00. ✋ |
| [`immich-worker`](modules/immich-worker/) | Déporte les jobs lourds d'Immich (miniatures, transcodage, reconnaissance) du NAS vers le GPU de cette machine, avec mise à jour sûre NAS + worker. |
| [`nas-mounts`](modules/nas-mounts/) | Monte automatiquement les partages du NAS (SMB, et NFS Immich en option) au premier accès, avec une petite fenêtre pour monter/démonter. |
| [`remote-workstation`](modules/remote-workstation/) | Monte le dossier personnel d’une ou plusieurs machines du réseau (ex. flystation) dans ~/Mounts, avec un raccourci Dolphin et « Exécuter sur la machine distante » au clic droit. ✋ |
| [`ssh-home-share`](modules/ssh-home-share/) | Rend cette machine accessible depuis les autres PC (module remote-workstation) : SSH par clé uniquement et nom <machine>.local sur le réseau. |

### Applications simples (84, `catalog/apps.toml`)

- **3D / Graphisme** : Blender Launcher, CloudCompare, Darktable, GIMP, Google Earth Pro, QGIS, RapidRAW, XnView MP
- **Communication** : Discord, Element, Slack
- **Crypto** : Electrum-LTC, Monero GUI
- **Développement** : Alacritty, DB Browser, Git, Jan, Meld, Notepadqq, VSCodium
- **Gaming** : Gamescope, Lutris, Mari0, Moonlight, Parsec, Pokete, Protontricks, ProtonUp-Qt, Steam
- **Médias** : Ardour, Bespoke Synth, DaVinci Resolve, FreeTube, Haruna, Jellyfin Desktop, Jellyfin Server, Kid3, Kodi, mpc-qt, mpv, OBS Studio, Shotcut, SMPlayer, SoundConverter, Spotify, Stremio, Tenacity, VLC, yt-dlp
- **Outils** : AppImageLauncher, Btop, Btrfs Assistant, Chromium, ClipQR, CoolerControl, Corex, Cryptomator, Filelight, FileZilla, Firefox Nightly, Glances, GParted, Hugo, KDE Connect, KeePassXC, Krokiet, lazydocker, Mission Center, PavuControl, qBittorrent, QDirStat, Remmina, Scrcpy, Sigma, SnapX, Syncthing, Vivaldi, VMware Workstation
- **Productivité** : Calibre, Dropbox, LibreWolf, Obsidian, OnlyOffice, Variety

✋ = étapes manuelles (voir le README du module)
<!-- /modules -->
