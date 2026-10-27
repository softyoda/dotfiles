#!/usr/bin/env bash
set -euo pipefail
source "$DOTFILES_LIB"
need_vars ROMS_DIR NAS_ROMS_DIR SCREENSCRAPER_USER SCREENSCRAPER_PASSWORD

ES="$HOME/ES-DE"
RA="$HOME/.config/retroarch"
CACHE="${XDG_CACHE_HOME:-$HOME/.cache}/dotfiles/es-de-retroarch"
mkdir -p "$CACHE" "$HOME/Applications" "$ES/themes" "$RA" "$ROMS_DIR"

# 1. AppImage ES-DE (version épinglée, ~125 Mo : non stockée dans le repo)
ESDE_VERSION=3.5.0
if ! compgen -G "$HOME/Applications/ES-DE_x64*.AppImage" >/dev/null; then
    info "téléchargement d'ES-DE $ESDE_VERSION…"
    curl -fL --retry 3 -o "$HOME/Applications/ES-DE_x64.AppImage.part" \
        "https://gitlab.com/api/v4/projects/18817634/packages/generic/ES-DE_Stable/$ESDE_VERSION/ES-DE_x64.AppImage"
    mv "$HOME/Applications/ES-DE_x64.AppImage.part" "$HOME/Applications/ES-DE_x64.AppImage"
    chmod +x "$HOME/Applications/ES-DE_x64.AppImage"
fi

# 2. Profils de manettes : dépôt libretro officiel (révision épinglée), sans le bouton de menu
#    (le menu RetroArch s'ouvre par le combo défini dans retroarch-session.cfg). Le profil Xbox local est conservé.
JAC_REV=7f94f847057c0829d4e18df27e50930728507f83
JAC="$CACHE/retroarch-joypad-autoconfig"
if [[ ! -d $JAC/.git ]]; then git clone -q --filter=blob:none https://github.com/libretro/retroarch-joypad-autoconfig.git "$JAC"; fi
git -C "$JAC" fetch -q origin "$JAC_REV" 2>/dev/null || git -C "$JAC" fetch -q origin
git -C "$JAC" -c advice.detachedHead=false checkout -q "$JAC_REV"
AC="$ES/settings/retroarch-autoconfig"
for d in android dinput hid linuxraw mfi parport qnx sdl2 sdl3 udev winraw x xinput; do
    mkdir -p "$AC/$d"; cp -rn "$JAC/$d/." "$AC/$d/"
done
find "$AC" -name '*.cfg' -exec sed -i '/^input_menu_toggle_btn/d' {} +

# 3. Thème Aura (révision épinglée + retouches locales) et collection « multijoueur »
AURA="$ES/themes/aura-es-de"
AURA_REV=46865ef1ac630b2573cb79fc1626216031bcb00c
if [[ ! -d $AURA/.git ]]; then git clone -q --filter=blob:none https://github.com/Siddy212/aura-es-de.git "$AURA"; fi
if git -C "$AURA" apply --check -R "$MODULE_DIR/files/patches/aura-es-de.patch" 2>/dev/null; then
    info "retouches Aura déjà appliquées"
else
    git -C "$AURA" fetch -q origin "$AURA_REV" 2>/dev/null || true
    git -C "$AURA" -c advice.detachedHead=false checkout -q "$AURA_REV" 2>/dev/null || warn "révision Aura non positionnée (modifications locales ?)"
    git -C "$AURA" apply "$MODULE_DIR/files/patches/aura-es-de.patch"
fi
cp -n "$MODULE_DIR"/files/aura-extra/multijoueur-* "$AURA/custom-collections/"
# Thème Adroit original (facultatif, alternative à Aura)
[[ -d $ES/themes/adroit-es-de ]] || git clone -q --depth 1 https://github.com/RickAndTired/adroit-es-de.git "$ES/themes/adroit-es-de"

# 4. retroarch.cfg : clés une par une (jamais le fichier entier)
set_ra() {  # set_ra <clé> <valeur>
    local f="$RA/retroarch.cfg"; touch "$f"
    if grep -q "^$1 = " "$f"; then sed -i "s|^$1 = .*|$1 = \"$2\"|" "$f"; else echo "$1 = \"$2\"" >>"$f"; fi
}
pgrep -x retroarch >/dev/null && warn "RetroArch tourne : il réécrira retroarch.cfg à sa fermeture"
while read -r k v; do set_ra "$k" "$v"; done <<'KEYS'
video_driver glcore
video_shader_enable true
input_joypad_driver udev
input_overlay_enable false
audio_driver pulse
video_windowed_fullscreen true
menu_driver xmb
xmb_theme 6
menu_dynamic_wallpaper_enable true
menu_shader_pipeline 0
menu_swap_ok_cancel_buttons true
menu_show_advanced_settings false
menu_show_core_updater false
quit_on_close_content 0
content_show_images false
content_show_music false
content_show_video false
content_show_netplay false
content_show_explore false
playlist_show_sublabels false
KEYS
success "ES-DE prêt (cœurs, BIOS et ROMs à ajouter à part ; voir README)"
