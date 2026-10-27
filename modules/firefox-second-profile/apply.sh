#!/usr/bin/env bash
# Crée le profil FIREFOX_EXTRA_PROFILE (s’il n’existe pas) et son lanceur.
set -euo pipefail
source "$DOTFILES_LIB"
need_vars FIREFOX_EXTRA_PROFILE

name="$FIREFOX_EXTRA_PROFILE"
slug=${name,,}; slug=${slug// /-}; slug=$(tr -cd 'a-z0-9-' <<<"$slug")

# Firefox ≥ 147 range les profils dans ~/.config/mozilla/firefox (XDG) ;
# les installations plus anciennes dans ~/.mozilla/firefox.
root="${XDG_CONFIG_HOME:-$HOME/.config}/mozilla/firefox"
[[ -f "$root/profiles.ini" || ! -d "$HOME/.mozilla/firefox" ]] || root="$HOME/.mozilla/firefox"

if grep -qxF "Name=$name" "$root/profiles.ini" 2>/dev/null; then
    info "profil Firefox « $name » déjà présent"
else
    dir="$root/$(od -An -N4 -tx4 /dev/urandom | tr -d ' \n').$slug"
    firefox -CreateProfile "$name $dir" >/dev/null 2>&1
    grep -qxF "Name=$name" "$root/profiles.ini" || { error "création du profil « $name » échouée"; exit 1; }
    success "profil Firefox « $name » créé ($dir)"
fi

apps="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
mkdir -p "$apps"
cat > "$apps/firefox-$slug.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Firefox ($name)
GenericName=Navigateur web
Comment=Firefox avec le profil « $name »
Exec=firefox -P "$name" --no-remote --name firefox-$slug %u
Icon=firefox-profile-extra
StartupWMClass=firefox-$slug
StartupNotify=true
Terminal=false
Categories=Network;WebBrowser;
MimeType=text/html;x-scheme-handler/http;x-scheme-handler/https;
EOF
update-desktop-database "$apps" 2>/dev/null || true
gtk-update-icon-cache -q "${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor" 2>/dev/null || true
success "lanceur « Firefox ($name) » installé"
