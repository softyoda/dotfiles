#!/bin/bash
source "$(dirname "$0")/utils.sh"

run() {
  header "Paramètres système"

  # SDDM autologin
  local user
  user=$(whoami)
  if [[ ! -f /etc/sddm.conf.d/autologin.conf ]]; then
    info "Activation de l'autologin SDDM pour $user..."
    sudo mkdir -p /etc/sddm.conf.d
    printf "[Autologin]\nUser=%s\nSession=plasma\n" "$user" | sudo tee /etc/sddm.conf.d/autologin.conf > /dev/null
    success "Autologin activé (effectif au prochain démarrage)"
  else
    info "Autologin déjà configuré"
  fi

  # Flatpak — ajout remote flathub
  if ! flatpak remotes 2>/dev/null | grep -q flathub; then
    info "Ajout de Flathub..."
    flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
    success "Flathub ajouté"
  fi

  # paru — installé si absent
  if ! is_installed_cmd paru; then
    info "Installation de paru (AUR helper)..."
    sudo pacman -S --needed --noconfirm base-devel
    git clone https://aur.archlinux.org/paru.git /tmp/paru-install
    (cd /tmp/paru-install && makepkg -si --noconfirm)
    rm -rf /tmp/paru-install
    success "paru installé"
  fi

  # Claude Code — setup POE API
  if is_installed_cmd claude; then
    info "Claude Code déjà installé"
  else
    warn "Claude Code non installé — sélectionne-le dans la liste des apps"
  fi
}

run
