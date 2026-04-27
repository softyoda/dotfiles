#!/bin/bash
source "$(dirname "$0")/utils.sh"

DOTFILES="$(cd "$(dirname "$0")/.." && pwd)"
KDE_DIR="$DOTFILES/kde"

run() {
  header "Restauration de l'environnement KDE"

  if [[ ! -d "$KDE_DIR" ]]; then
    error "Pas de backup KDE trouvé dans $KDE_DIR"
    return 1
  fi

  # Packages thème CachyOS
  info "Installation des thèmes CachyOS..."
  paru -S --needed --noconfirm \
    cachyos-emerald-kde-theme-git \
    cachyos-iridescent-kde \
    cachyos-kde-settings 2>/dev/null || warn "Certains thèmes CachyOS non disponibles"

  # Icônes Papirus (repos officiels)
  if ! pacman -Qq papirus-icon-theme &>/dev/null; then
    info "Installation de papirus-icon-theme..."
    sudo pacman -S --needed --noconfirm papirus-icon-theme && success "papirus-icon-theme installé"
  fi

  # Icônes We10X (AUR)
  if ! paru -Qq we10x-icon-theme-git &>/dev/null; then
    info "Installation de we10x-icon-theme-git (AUR)..."
    paru -S --needed --noconfirm we10x-icon-theme-git && success "we10x-icon-theme-git installé"
  fi

  # Fichiers de config
  info "Copie des configs KDE..."
  local configs=(
    kdeglobals kwinrc plasmarc plasmashellrc
    kglobalshortcutsrc plasma-org.kde.plasma.desktop-appletsrc
    ksplashrc plasma-localerc kscreenlockerrc
  )
  for f in "${configs[@]}"; do
    if [[ -f "$KDE_DIR/$f" ]]; then
      cp "$KDE_DIR/$f" "$HOME/.config/$f"
      info "  $f"
    fi
  done
  [[ -d "$KDE_DIR/kdedefaults" ]] && cp -r "$KDE_DIR/kdedefaults" "$HOME/.config/"

  # Splash screen Watch_Dogs_Theme
  if [[ -d "$KDE_DIR/look-and-feel/Watch_Dogs_Theme" ]]; then
    mkdir -p "$HOME/.local/share/plasma/look-and-feel"
    cp -r "$KDE_DIR/look-and-feel/Watch_Dogs_Theme" "$HOME/.local/share/plasma/look-and-feel/"
    success "  Watch_Dogs_Theme (splash)"
  fi

  # Recharge Plasma
  info "Rechargement de Plasma..."
  kbuildsycoca6 --noincremental 2>/dev/null || true
  qdbus6 org.kde.KWin /KWin reconfigure 2>/dev/null || true

  success "Environnement KDE restauré ! (redémarre la session pour finaliser)"
}

run
