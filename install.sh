#!/bin/bash
set -e
DOTFILES="$(cd "$(dirname "$0")" && pwd)"
source "$DOTFILES/scripts/utils.sh"

header "Dotfiles Installer"
echo -e "  Répertoire : ${BOLD}$DOTFILES${NC}\n"

# 1. Système (paru, flathub, autologin)
bash "$DOTFILES/scripts/setup-system.sh"

# 2. Symlinks configs (fish, konsole, wezterm)
bash "$DOTFILES/scripts/link-configs.sh"

# 3. GUI : clé API + sélection des apps (PyQt6)
if ! python3 -c "import PyQt6" 2>/dev/null; then
  info "Installation de PyQt6..."
  sudo pacman -S --needed --noconfirm python-pyqt6
fi

python3 "$DOTFILES/installer.py"

# 4. Restauration thème KDE
bash "$DOTFILES/scripts/kde-restore.sh"

echo ""
success "Installation terminée ! Redémarre ta session KDE pour finaliser."
