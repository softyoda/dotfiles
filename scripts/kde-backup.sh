#!/bin/bash
source "$(dirname "$0")/utils.sh"

DOTFILES="$(cd "$(dirname "$0")/.." && pwd)"
KDE_DIR="$DOTFILES/kde"

run() {
  header "Sauvegarde de l'environnement KDE"

  mkdir -p "$KDE_DIR/look-and-feel"

  # Fichiers de config
  local configs=(
    kdeglobals kwinrc plasmarc plasmashellrc
    kglobalshortcutsrc plasma-org.kde.plasma.desktop-appletsrc
    ksplashrc plasma-localerc kscreenlockerrc
  )
  info "Configs ~/.config/ ..."
  for f in "${configs[@]}"; do
    if [[ -f "$HOME/.config/$f" ]]; then
      cp "$HOME/.config/$f" "$KDE_DIR/$f"
      success "  $f"
    else
      warn "  $f introuvable"
    fi
  done

  # Répertoires de config
  local dirs=(kdedefaults)
  for d in "${dirs[@]}"; do
    if [[ -d "$HOME/.config/$d" ]]; then
      mkdir -p "$KDE_DIR/$d"
      cp -r "$HOME/.config/$d/." "$KDE_DIR/$d/"
      success "  $d/"
    fi
  done

  # Splash screen Watch_Dogs_Theme
  local splash="$HOME/.local/share/plasma/look-and-feel/Watch_Dogs_Theme"
  if [[ -d "$splash" ]]; then
    cp -r "$splash" "$KDE_DIR/look-and-feel/"
    success "  Watch_Dogs_Theme (splash)"
  else
    warn "  Watch_Dogs_Theme introuvable (non installé ?)"
  fi

  echo ""
  success "Sauvegarde terminée dans $KDE_DIR"
  info "Pense à faire : cd $DOTFILES && git add kde/ && git commit -m 'update KDE config'"
}

run
