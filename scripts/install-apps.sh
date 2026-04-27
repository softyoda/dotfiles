#!/bin/bash
source "$(dirname "$0")/utils.sh"

# Format: "id|label|méthode|paquet|installé_par_défaut"
# méthode: pacman | paru | flatpak
APPS=(
  # Communication
  "discord|Discord — chat & gaming|pacman|discord|ON"
  "slack|Slack — chat pro|flatpak|com.slack.Slack|OFF"
  "element|Element — Matrix/Signal|flatpak|im.riot.Riot|OFF"
  # Productivité
  "obsidian|Obsidian — notes|flatpak|md.obsidian.Obsidian|ON"
  "onlyoffice|OnlyOffice — suite bureautique|paru|onlyoffice-bin|ON"
  "calibre|Calibre — ebooks|pacman|calibre|OFF"
  "librewolf|LibreWolf — Firefox sans tracking|flatpak|io.gitlab.librewolf-community.LibreWolf|OFF"
  "dropbox|Dropbox — sync cloud|pacman|dropbox|ON"
  # Développement
  "vscodium|VSCodium — éditeur de code|pacman|vscodium|ON"
  "git|Git|pacman|git|ON"
  "meld|Meld — diff visuel|pacman|meld|ON"
  "python|Python 3|pacman|python|ON"
  "sqlitebrowser|DB Browser for SQLite|pacman|sqlitebrowser|OFF"
  "claude-code|Claude Code — IA terminal|npm|@anthropic-ai/claude-code|OFF"
  # Médias
  "vlc|VLC — lecteur vidéo|pacman|vlc|ON"
  "obs|OBS Studio — stream/record|pacman|obs-studio|OFF"
  "spotify|Spotify|flatpak|com.spotify.Client|OFF"
  "shotcut|Shotcut — montage vidéo|pacman|shotcut|ON"
  "freetube|FreeTube — YouTube sans pub|flatpak|io.freetubeapp.FreeTube|OFF"
  "tenacity|Tenacity — audio (fork Audacity)|flatpak|org.tenacityaudio.Tenacity|OFF"
  "davinci|DaVinci Resolve|flatpak|com.blackmagicdesign.resolve|OFF"
  # 3D / Graphisme
  "blender|Blender Launcher — gère toutes versions Blender|paru|blender-launcher-v2-bin|ON"
  "darktable|Darktable — RAW photo|pacman|darktable|OFF"
  "gimp|GIMP — retouche image|pacman|gimp|OFF"
  "qgis|QGIS — SIG/cartographie|pacman|qgis|OFF"
  "cloudcompare|CloudCompare — nuages de points|flatpak|org.cloudcompare.CloudCompare|OFF"
  "orcaslicer|OrcaSlicer — slicer 3D print|paru|orcaslicer-bin|OFF"
  # Gaming
  "steam|Steam|pacman|steam|ON"
  "lutris|Lutris — launcher multi-plateformes|pacman|lutris|OFF"
  # Outils système
  "qbittorrent|qBittorrent — torrents|pacman|qbittorrent|ON"
  "kdeconnect|KDE Connect — téléphone ↔ PC|pacman|kdeconnect|ON"
  "gparted|GParted — partitions|pacman|gparted|OFF"
  "syncthing|Syncthing — sync P2P (alternative Dropbox)|pacman|syncthing|OFF"
  "remmina|Remmina — bureau à distance RDP|pacman|remmina|OFF"
  "filezilla|FileZilla — FTP/SFTP|pacman|filezilla|ON"
  "snapx|SnapX — screenshot/gif/upload (ShareX)|pacman|snapx|ON"
  "missioncenter|Mission Center — moniteur système|flatpak|io.missioncenter.MissionCenter|ON"
)

build_checklist() {
  local items=()
  for app in "${APPS[@]}"; do
    IFS='|' read -r id label method pkg default <<< "$app"
    # Vérifie si déjà installé
    local status="$default"
    case "$method" in
      pacman|paru) is_installed_pacman "$pkg" && status="ON" ;;
      flatpak) is_installed_flatpak "$pkg" && status="ON" ;;
      npm) is_installed_cmd "claude" && status="ON" ;;
    esac
    items+=("$id" "$label" "$status")
  done
  echo "${items[@]}"
}

install_app() {
  local id="$1"
  for app in "${APPS[@]}"; do
    IFS='|' read -r aid label method pkg default <<< "$app"
    if [[ "$aid" == "$id" ]]; then
      info "Installation de $label..."
      case "$method" in
        pacman) sudo pacman -S --needed --noconfirm "$pkg" ;;
        paru)   paru -S --needed --noconfirm "$pkg" ;;
        flatpak)
          flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo 2>/dev/null
          flatpak install -y flathub "$pkg"
          ;;
        npm)
          if ! is_installed_cmd node; then
            sudo pacman -S --needed --noconfirm nodejs npm
          fi
          sudo npm install -g "$pkg"
          ;;
      esac
      success "$label installé"
      return
    fi
  done
}

run() {
  header "Sélection des applications"

  local items
  items=($(build_checklist))

  local selected
  selected=$(whiptail --title "Dotfiles — Apps à installer" \
    --checklist "\nCoche les apps à installer (Espace = sélectionner, Entrée = confirmer)\nLes apps déjà installées sont pré-cochées." \
    36 72 24 \
    "${items[@]}" \
    3>&1 1>&2 2>&3) || { warn "Annulé."; return; }

  # Supprime les guillemets
  selected=$(echo "$selected" | tr -d '"')

  if [[ -z "$selected" ]]; then
    warn "Aucune app sélectionnée."; return
  fi

  header "Installation"
  for id in $selected; do
    install_app "$id"
  done

  success "Toutes les apps sélectionnées sont installées !"
}

run
