#!/usr/bin/env bash
# Point d'entrée sur une machine CachyOS / Arch + KDE (neuve ou existante).
#   git clone https://github.com/softyoda/dotfiles.git ~/dotfiles && bash ~/dotfiles/install.sh
# Ensuite tout se fait depuis l'appli « Dotfiles » (menu) ou `dotctl`.
set -euo pipefail
DOTFILES="$(cd "$(dirname "$0")" && pwd)"
source "$DOTFILES/lib/lib.sh"

echo -e "\n${BOLD}${BLUE}━━ Dotfiles ━━${NC}  $DOTFILES\n"

# Prérequis de l'interface
missing=()
for p in python python-pyqt6 git ksshaskpass; do has_pkg "$p" || missing+=("$p"); done
((${#missing[@]})) && { info "installation : ${missing[*]}"; as_root pacman -S --needed --noconfirm "${missing[@]}"; }

export SUDO_ASKPASS="${SUDO_ASKPASS:-/usr/bin/ksshaskpass}"
"$DOTFILES/bin/dotctl" apply dotfiles-app

# Dossier privé (profils machines + secrets) : bibliothèque Seafile chiffrée
if ! PYTHONPATH="$DOTFILES" python3 -c 'from dotctl import core; import sys; sys.exit(0 if core.private_dir() else 1)'; then
    warn "Dossier privé introuvable. Pour retrouver le profil de cette machine :"
    echo "    1. dotctl apply seafile   (puis se connecter et synchroniser « dotfiles-private »)"
    echo "    2. relancer l'appli Dotfiles"
    echo "  Sans dossier privé, l'appli fonctionne quand même (aucun module pré-coché)."
fi

if in_session; then
    nohup "$HOME/.local/bin/dotctl" tray >/dev/null 2>&1 &
    exec "$HOME/.local/bin/dotctl" gui
else
    success "Installé. Hors session graphique : dotctl status | dotctl apply --profile"
fi
