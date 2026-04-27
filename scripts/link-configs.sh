#!/bin/bash
source "$(dirname "$0")/utils.sh"

DOTFILES="$(cd "$(dirname "$0")/.." && pwd)"

symlink() {
  local src="$1" dst="$2"
  mkdir -p "$(dirname "$dst")"
  [[ -f "$dst" && ! -L "$dst" ]] && mv "$dst" "$dst.bak" && info "  Backup: $dst.bak"
  ln -sf "$src" "$dst"
  success "  $dst"
}

run() {
  header "Configs (symlinks)"

  symlink "$DOTFILES/config/fish/config.fish"           ~/.config/fish/config.fish
  symlink "$DOTFILES/config/konsole/Default.profile"    ~/.local/share/konsole/Default.profile
  symlink "$DOTFILES/config/wezterm/wezterm.lua"        ~/.config/wezterm/wezterm.lua

  # Flatpak — handler .flatpakref
  mkdir -p ~/.local/share/applications ~/.local/bin
  cat > ~/.local/share/applications/flatpakref-handler.desktop << EOF
[Desktop Entry]
Name=Flatpak Installer
Exec=$HOME/.local/bin/flatpakref-install %f
MimeType=application/vnd.flatpak.ref;
Type=Application
NoDisplay=true
EOF
  printf '#!/bin/fish\nflatpak install $argv[1]\n' > ~/.local/bin/flatpakref-install
  chmod +x ~/.local/bin/flatpakref-install
  xdg-mime default flatpakref-handler.desktop application/vnd.flatpak.ref 2>/dev/null || true
  success "  Handler .flatpakref"
}

run
