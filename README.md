# Dotfiles — CachyOS / Arch Linux + KDE Plasma

Setup complet de mon environnement en une commande.

## Démarrage rapide

```bash
# 1. Cloner le repo
git clone https://github.com/softyoda/dotfiles.git ~/dotfiles
cd ~/dotfiles

# 2. Lancer l'installeur
bash install.sh
```

C'est tout. L'installeur se charge du reste.

## Ce qui est fait automatiquement

| Étape | Détail |
|-------|--------|
| **Système** | Installation de `paru` (AUR helper), activation de Flathub, autologin SDDM |
| **Configs** | Symlinks fish shell, WezTerm, Konsole |
| **Clé API** | Saisie de la clé Anthropic → sauvegardée dans `~/.config/fish/secrets.fish` |
| **Applications** | GUI avec sélection des apps à installer |
| **KDE Plasma** | Restauration du thème, raccourcis, layout bureau |

## Sélection des applications (GUI)

L'installeur ouvre une interface graphique pour choisir les apps :

- **Communication** : Discord, Slack, Element
- **Productivité** : Obsidian, OnlyOffice, LibreWolf, Dropbox
- **Développement** : VSCodium, Git, Meld, Claude Code
- **Médias** : VLC, OBS, Spotify, Shotcut, DaVinci Resolve
- **3D / Graphisme** : Blender Launcher, GIMP, OrcaSlicer, QGIS
- **Gaming** : Steam, Lutris
- **Outils** : qBittorrent, KDE Connect, FileZilla, GParted, SnapX…

Les apps déjà installées sont détectées et pré-cochées.

## Clé API Claude

Obtiens ta clé sur [console.anthropic.com](https://console.anthropic.com) → API Keys.

La clé est sauvegardée dans `~/.config/fish/secrets.fish` (fichier non commité, ignoré par git).

## Structure du repo

```
dotfiles/
├── install.sh                    # Point d'entrée unique
├── installer.py                  # GUI PyQt6 (clé API + sélection apps)
├── config/
│   ├── fish/config.fish          # Config fish shell
│   ├── konsole/Default.profile   # Profil terminal Konsole
│   └── wezterm/wezterm.lua       # Config WezTerm
├── kde/                          # Backup configs KDE Plasma
│   ├── kdeglobals
│   ├── kwinrc
│   ├── plasmarc
│   ├── plasmashellrc
│   ├── kglobalshortcutsrc
│   ├── plasma-org.kde.plasma.desktop-appletsrc
│   └── kdedefaults/
├── scripts/
│   ├── setup-system.sh           # paru, Flathub, autologin SDDM
│   ├── kde-restore.sh            # Restaure le thème KDE
│   ├── link-configs.sh           # Crée les symlinks configs
│   ├── setup-spicetify-hook.sh   # Hook auto-reapply Spicetify post-update
│   ├── spicetify-reapply         # Bin appelé par le hook systemd
│   ├── cache-cleanup.sh          # Purge caches pacman/paru > 7 jours
│   ├── setup-cache-cleanup.sh    # Installe le timer systemd de nettoyage
│   └── utils.sh                  # Fonctions utilitaires bash
├── systemd/user/
│   ├── spicetify-reapply.service # Lance spicetify backup apply
│   └── spicetify-reapply.path    # Watch le deployment Flatpak Spotify
└── systemd/system/
    ├── cache-cleanup.service     # Oneshot : purge des caches
    └── cache-cleanup.timer       # Timer quotidien (Persistent)
```

## Hook auto-reapply Spicetify

Si Spicetify est sélectionné lors de l'install, un hook systemd user est activé : il
détecte chaque update de Spotify (Flatpak) via le symlink de deployment et relance
automatiquement `spicetify backup apply`. Plus besoin de le refaire à la main après
chaque `flatpak update` / `Cachy-Update`.

## Nettoyage automatique des caches

Les caches de paquets ne sont **jamais** purgés automatiquement sur Arch/CachyOS :
`/var/cache/pacman/pkg` et `~/.cache/paru/clone` grossissent indéfiniment (facilement
plusieurs dizaines de Go, ex. les versions successives de `cuda` ou les nightlies Firefox).

Ce repo installe un timer systemd qui supprime **chaque jour** les fichiers de cache
(`*.pkg.tar.*`, archives sources, AppImage, .deb…) de **plus de 7 jours**, côté pacman
comme côté paru.

```bash
bash scripts/setup-cache-cleanup.sh
```

Vérifier / déclencher manuellement :

```bash
systemctl list-timers cache-cleanup.timer   # prochaine exécution
journalctl -u cache-cleanup.service          # ce qui a été supprimé
sudo /usr/local/bin/cache-cleanup.sh         # lancer maintenant
```

## Prérequis

- CachyOS ou Arch Linux avec KDE Plasma installé
- Connexion internet
- Python 3 (inclus dans CachyOS)

## Mettre à jour les configs KDE

Pour sauvegarder tes configs KDE actuelles dans le repo :

```bash
cp ~/.config/kdeglobals kde/
cp ~/.config/kwinrc kde/
cp ~/.config/plasmarc kde/
cp ~/.config/plasmashellrc kde/
cp ~/.config/kglobalshortcutsrc kde/
cp ~/.config/plasma-org.kde.plasma.desktop-appletsrc kde/
cp -r ~/.config/kdedefaults kde/
git add kde/ && git commit -m "update KDE config"
```
