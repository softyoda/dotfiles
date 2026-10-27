# ES-DE + RetroArch

Frontend **ES-DE 3.5.0** (AppImage) lançant RetroArch en plein écran, avec le thème **Aura** et un menu RetroArch épuré.
Le module ne contient **ni cœurs, ni BIOS, ni ROMs**.

## Variables et secrets

| Nom | Rôle | Valeur sur ryzen |
|---|---|---|
| `ROMS_DIR` (var) | dossier local des ROMs (`ROMDirectory` d'ES-DE, systèmes locaux) | `/home/ryzen/Jeux/ROMs` |
| `NAS_ROMS_DIR` (var) | dossier du set de ROMs sur le NAS (systèmes et collections) | `/mnt/nas/01_MEDIA/05_GAMES/retro-roms-best-set` |
| `SCREENSCRAPER_USER`, `SCREENSCRAPER_PASSWORD` (secrets) | compte ScreenScraper pour le scraper d'ES-DE | `~/.config/dotfiles/secrets.env` |

`es_settings.xml` est un **template** : `dotctl capture` ne le remonte pas, reporter les changements à la main
(en laissant les `${…}` à la place des identifiants).

## Ce que fait `apply.sh`

1. Télécharge l'AppImage ES-DE (version épinglée) dans `~/Applications/`.
2. Reconstruit `~/ES-DE/settings/retroarch-autoconfig/` depuis le dépôt libretro (révision épinglée), sans les lignes `input_menu_toggle_btn`, plus le profil Xbox Series local (`files/settings/`).
3. Clone le thème Aura (révision épinglée + `files/patches/aura-es-de.patch` + cartes « multijoueur ») et le thème Adroit d'origine.
   Le variant local `adroit-retrorama-es-de` n'est **pas** reproduit.
4. Règle `~/.config/retroarch/retroarch.cfg` clé par clé (pilote vidéo glcore, menu XMB, A/B inversés, rubriques masquées…).

Déployés : `es_systems.xml` (33 systèmes, commande `retroarch --appendconfig retroarch-session.cfg -f -L <cœur> %ROM%`), `retroarch-session.cfg` (surcharge propre à ES-DE : quitter à la fermeture, combo de menu manette, XMB), les 3 collections multijoueur.

## À faire à la main

- Installer les cœurs (menu RetroArch → Online Updater, ou `~/.config/retroarch/cores/`) et les BIOS nécessaires.
- Les fonds/icônes XMB « Retrorama » (`~/.config/retroarch/assets-vriom`, référencé par la session) ne sont pas dans le repo.
- Les médias scrapés (`~/ES-DE/downloaded_media`, `gamelists`) ne sont pas sauvegardés.

## Lanceurs hors RetroArch (non déployés)

- **xemu** (Xbox) : `~/.local/bin/xemu` est un script `exec` vers l'AppImage dans `~/Applications/` (nom à hash installé par AppImageLauncher) ; ES-DE l'appelle avec `-full-screen -dvd_path %ROM%`.
- **suyu** (Switch) : v0.0.10 dans `~/.local/opt/suyu-v0.0.10/` ; `launch-suyu` ajoute `compat/usr/lib/x86_64-linux-gnu` à `LD_LIBRARY_PATH` puis lance `suyu`. Lanceur de menu : `~/.local/share/applications/suyu.desktop`.
  Binaire non redistribué ici : à réinstaller manuellement.

## Mode salon (gamescope)

La session gamescope (`gamescope-session`, paquet `gamescope-session-cachyos`) permet de démarrer directement dans un mode console.
Elle se choisit via le module `autologin` (variable `AUTOLOGIN_SESSION = "gamescope-session"`) ; attention au fichier
`zz-steamos-autologin.conf` de `/etc/plasmalogin.conf.d/` qui prime sur `autologin.conf` (voir le README d'`autologin`).
ES-DE se lance alors comme application Steam non-Steam ou depuis le bureau.

## `tools/` (scripts Python d'installation, d'audit et de maintenance, tels que conservés)

Ils contiennent encore des chemins de la machine d'origine ; à relire avant usage.

| Fichier | Rôle |
|---|---|
| `setup-esde.py`, `setup-visual.py`, `fix-frontends.py` | installation initiale d'ES-DE, thème XMB/effets visuels, comportement à la fermeture |
| `link-nas-retroarch.py`, `nas-extract-roms.py`, `nas-roms-inventory.py`, `nas-progress.py`, `nas-record-integration.py` | liaison avec le set de ROMs du NAS, extraction, inventaire, suivi |
| `incoming-plan.py`, `incoming-stage.py`, `incoming-apply.py`, `incoming-finish.py` | intégration de nouveaux jeux (dédoublonnage, mise en place, finitions) |
| `bulk-metadata.py`, `plan-bulk-media.py`, `download-bulk-media.py`, `esde-scrape-monitor.py` | métadonnées et médias en masse, suivi du scraper |
| `game-artwork.py`, `install-game-artwork.py`, `supplement-artwork.py`, `repair-artwork.py`, `audit-game-artwork.py`, `audit-bulk-final.py` | illustrations des jeux : installation, complément, réparation, audit |
| `RETROARCH.md`, `NAS-RETROARCH.md`, `INVENTAIRE-EMULATEURS.md`, `SOURCES-ROM-RETROARCH.md` | notes d'installation, inventaire des émulateurs, sources |
