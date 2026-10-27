#!/usr/bin/env bash
# Helpers communs aux apply.sh / check.sh des modules.
# Usage : source "$DOTFILES_LIB"

BLUE='\033[0;34m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'; BOLD='\033[1m'
info()    { echo -e "${BLUE}  →${NC} $*"; }
success() { echo -e "${GREEN}  ✓${NC} $*"; }
warn()    { echo -e "${YELLOW}  ⚠${NC} $*"; }
error()   { echo -e "${RED}  ✗${NC} $*" >&2; }

# Exécute en root ; utilise SUDO_ASKPASS (ksshaskpass) hors terminal.
as_root() {
    if [[ $EUID -eq 0 ]]; then "$@"
    elif [[ ! -t 0 && -n "${SUDO_ASKPASS:-}" ]]; then sudo -A "$@"
    else sudo "$@"; fi
}

has()        { command -v "$1" &>/dev/null; }
has_pkg()    { pacman -Qq "$1" &>/dev/null; }
in_session() { [[ -n "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ]]; }

# Exige des variables (profil privé ou ~/.config/dotfiles/secrets.env)
need_vars() {
    local v missing=()
    for v in "$@"; do [[ -n "${!v:-}" ]] || missing+=("$v"); done
    if ((${#missing[@]})); then error "variables manquantes : ${missing[*]}"; exit 1; fi
}

# Active un service système / utilisateur (idempotent)
enable_system() { as_root systemctl enable --now "$@"; }
enable_user()   { systemctl --user daemon-reload; systemctl --user enable --now "$@"; }

# Ajoute une ligne à un fichier root si absente
ensure_line_root() {
    local line="$1" file="$2"
    as_root grep -qxF -- "$line" "$file" 2>/dev/null || echo "$line" | as_root tee -a "$file" >/dev/null
}

# Ajoute l'utilisateur à des groupes
ensure_groups() {
    local g
    for g in "$@"; do
        getent group "$g" >/dev/null || as_root groupadd -r "$g"
        id -nG "$USER" | tr ' ' '\n' | grep -qx "$g" || { as_root usermod -aG "$g" "$USER"; info "groupe $g ajouté (reconnexion requise)"; }
    done
}
