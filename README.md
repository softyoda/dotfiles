# Dotfiles — CachyOS / Arch Linux + KDE Plasma

Setup complet de mon environnement en une commande.

## Démarrage rapide

```bash
# 1. Cloner le repo
git clone https://github.com/TON_USER/dotfiles.git ~/dotfiles
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
└── scripts/
    ├── setup-system.sh           # paru, Flathub, autologin SDDM
    ├── kde-restore.sh            # Restaure le thème KDE
    ├── link-configs.sh           # Crée les symlinks configs
    └── utils.sh                  # Fonctions utilitaires bash
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
