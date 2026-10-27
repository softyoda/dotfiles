#!/usr/bin/env bash
# Lanceur + autostart : passent par mullvad-exclude si Mullvad est installé
# (Discord n’aime pas les IP de VPN : captchas, vocal dégradé).
set -euo pipefail
source "$DOTFILES_LIB"

apps="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
autostart="${XDG_CONFIG_HOME:-$HOME/.config}/autostart"
mkdir -p "$apps" "$autostart"

prefix=""
if [[ -x /usr/bin/mullvad-exclude ]]; then
    prefix="/usr/bin/mullvad-exclude "
else
    info "Mullvad absent : Vesktop lancé sans mullvad-exclude"
fi

cat > "$apps/vesktop.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Discord Vesktop
GenericName=Internet Messenger
Comment=Client Discord Vesktop (Vencord intégré)
Exec=${prefix}/usr/bin/vesktop %U
Icon=vesktop
StartupWMClass=vesktop
StartupNotify=true
Terminal=false
Categories=Network;
Keywords=discord;vencord;electron;chat;
MimeType=x-scheme-handler/discord
EOF

cat > "$autostart/vesktop.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Vesktop
Comment=Démarrage de Vesktop réduit dans la barre système
Exec=${prefix}/usr/bin/vesktop --start-minimized
Icon=vesktop
StartupNotify=false
Terminal=false
EOF

update-desktop-database "$apps" 2>/dev/null || true
xdg-mime default vesktop.desktop x-scheme-handler/discord
success "Vesktop : lanceur, démarrage automatique et liens discord:// configurés"
