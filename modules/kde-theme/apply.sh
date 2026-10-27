#!/usr/bin/env bash
# Thème KDE Plasma 6 : We10XOS-dark + icônes We10X-black-dark + curseurs Win10OS,
# accent gris, effets KWin (verre, flou, fenêtres molles…), splash Watch_Dogs,
# fond d'écran flouté en diaporama.
set -euo pipefail
source "$DOTFILES_LIB"
need_vars WALLPAPER_DIR XWAYLAND_SCALE

F="$MODULE_DIR/files"
DATA="${XDG_DATA_HOME:-$HOME/.local/share}"
CFG="${XDG_CONFIG_HOME:-$HOME/.config}"
CACHE="${XDG_CACHE_HOME:-$HOME/.cache}/dotfiles/kde-theme"
mkdir -p "$CACHE"

# Sources épinglées (téléchargées : trop lourdes pour le repo)
WE10XOS_KDE_URL=https://github.com/yeyushengfan258/We10XOS-kde
WE10XOS_KDE_REV=270f0d7d3c1f0d5540109e6116d2fa891664f24b
WE10X_ICONS_URL=https://github.com/yeyushengfan258/We10X-icon-theme
WE10X_ICONS_REV=0f52ff2dce554146f8f76ab2c7a5968fd773400d
WIN10OS_CURSORS_URL=https://github.com/yeyushengfan258/Win10OS-cursors
WIN10OS_CURSORS_REV=79d13bb90eb9346a40a2da5a1f5cb24cb919f256

# fetch <url> <rev> <dossier>  — clone/positionne un dépôt git sur une révision
fetch() {
    local url=$1 rev=$2 dir=$3
    if [[ ! -d $dir/.git ]]; then
        rm -rf "$dir"; git clone -q --filter=blob:none "$url" "$dir"
    fi
    git -C "$dir" fetch -q origin "$rev" 2>/dev/null || git -C "$dir" fetch -q origin
    git -C "$dir" -c advice.detachedHead=false checkout -q "$rev"
}

# sync_dir <src> <dst> — copie un dossier (remplacement complet) s'il diffère
sync_dir() {
    local src=$1 dst=$2
    if ! diff -rq "$src" "$dst" &>/dev/null; then
        rm -rf "$dst"; mkdir -p "$(dirname "$dst")"; cp -r "$src" "$dst"
        info "  → $dst"
    fi
}

has_icon_theme() { [[ -d $DATA/icons/$1 || -d /usr/share/icons/$1 || -d $HOME/.icons/$1 ]]; }

# ── Thème global, Plasma, décorations (We10XOS) ─────────────────────────────
info "Thème We10XOS-dark (global, Plasma, Aurorae)"
fetch "$WE10XOS_KDE_URL" "$WE10XOS_KDE_REV" "$CACHE/We10XOS-kde"
sync_dir "$CACHE/We10XOS-kde/plasma/look-and-feel/6.0/com.github.yeyushengfan258.We10XOS-dark" \
         "$DATA/plasma/look-and-feel/com.github.yeyushengfan258.We10XOS-dark"
sync_dir "$CACHE/We10XOS-kde/plasma/desktoptheme/We10XOS-dark" "$DATA/plasma/desktoptheme/We10XOS-dark"
sync_dir "$CACHE/We10XOS-kde/aurorae/We10XOS-dark" "$DATA/aurorae/themes/We10XOS-dark"
# Modèle de couleurs : version locale (légèrement retouchée par rapport à l'amont)
install -Dm644 "$F/color-schemes/We10XOSDark.colors" "$DATA/color-schemes/We10XOSDark.colors"

# ── Icônes et curseurs ──────────────────────────────────────────────────────
if ! has_icon_theme We10X-black-dark; then
    info "Icônes We10X (variante black)"
    fetch "$WE10X_ICONS_URL" "$WE10X_ICONS_REV" "$CACHE/We10X-icon-theme"
    (cd "$CACHE/We10X-icon-theme" && ./install.sh -d "$DATA/icons" -t black)
fi
if ! has_icon_theme Papirus && ! has_pkg papirus-icon-theme; then
    info "Icônes Papirus (dépôt officiel)"
    as_root pacman -S --needed --noconfirm papirus-icon-theme
fi
if ! has_icon_theme Win10OS-cursors; then
    info "Curseurs Win10OS"
    fetch "$WIN10OS_CURSORS_URL" "$WIN10OS_CURSORS_REV" "$CACHE/Win10OS-cursors"
    mkdir -p "$HOME/.icons"; rm -rf "$HOME/.icons/Win10OS-cursors"
    cp -r "$CACHE/Win10OS-cursors/dist" "$HOME/.icons/Win10OS-cursors"
fi

# ── Petits paquets locaux versionnés dans le module ─────────────────────────
info "Splash Watch_Dogs, effet geometry_change, applets"
sync_dir "$F/look-and-feel/Watch_Dogs_Theme" "$DATA/plasma/look-and-feel/Watch_Dogs_Theme"
sync_dir "$F/kwin-effects/kwin4_effect_geometry_change" "$DATA/kwin/effects/kwin4_effect_geometry_change"
sync_dir "$F/plasmoids/org.kde.plasma.simplekickoff" "$DATA/plasma/plasmoids/org.kde.plasma.simplekickoff"
sync_dir "$F/wallpapers/org.kde.plasma.citygrow" "$DATA/plasma/wallpapers/org.kde.plasma.citygrow"

# ── Réglages, clé par clé ───────────────────────────────────────────────────
kw() { kwriteconfig6 "$@"; }
info "Réglages d'apparence (kdeglobals, plasmarc, ksplashrc, kcminputrc)"
kw --file kdeglobals --group General --key ColorScheme We10XOSDark
kw --file kdeglobals --group General --key AccentColor 104,107,111
kw --file kdeglobals --group General --key LastUsedCustomAccentColor 104,107,111
kw --file kdeglobals --group General --key font "Noto Sans,10,-1,5,400,0,0,0,0,0,0,0,0,0,0,1,,0,0"
kw --file kdeglobals --group General --key XftAntialias true
kw --file kdeglobals --group General --key XftHintStyle hintslight
kw --file kdeglobals --group General --key XftSubPixel none
kw --file kdeglobals --group Icons --key Theme We10X-black-dark
kw --file kdeglobals --group KDE --key LookAndFeelPackage com.github.yeyushengfan258.We10XOS-dark
kw --file kdeglobals --group KDE --key widgetStyle Breeze
kw --file kdeglobals --group KDE --key AnimationDurationFactor 0.25
kw --file plasmarc --group Theme --key name We10XOS-dark
kw --file ksplashrc --group KSplash --key Engine KSplashQML
kw --file ksplashrc --group KSplash --key Theme Watch_Dogs_Theme
kw --file kcminputrc --group Mouse --key cursorTheme Win10OS-cursors
kw --file kcminputrc --group Mouse --key cursorSize 36
# Pas de verrouillage automatique (l'économiseur rétro prend le relais)
kw --file kscreenlockerrc --group Daemon --key Autolock false
kw --file kscreenlockerrc --group Daemon --key LockOnResume false
kw --file kscreenlockerrc --group Daemon --key Timeout 0
kw --file plasma-localerc --group Formats --key LANG fr_FR.UTF-8

info "Décoration et effets KWin"
kw --file kwinrc --group org.kde.kdecoration2 --key library org.kde.kwin.aurorae.v2
kw --file kwinrc --group org.kde.kdecoration2 --key theme __aurorae__svg__We10XOS-dark
kw --file kwinrc --group Effect-blur --key BlurStrength 11
kw --file kwinrc --group Effect-blur --key NoiseStrength 4
kw --file kwinrc --group Effect-blur --key Saturation 169
kw --file kwinrc --group Effect-shakecursor --key Magnification 4
kw --file kwinrc --group Effect-wobblywindows --key AdvancedMode true
kw --file kwinrc --group Effect-wobblywindows --key MoveFactor 14
kw --file kwinrc --group Effect-wobblywindows --key Stiffness 5
for p in diminactive glass translucency wobblywindows kwin4_effect_geometry_change; do
    kw --file kwinrc --group Plugins --key "${p}Enabled" true
done
for p in overview kinetic_maximize; do
    kw --file kwinrc --group Plugins --key "${p}Enabled" false
done
kw --file kwinrc --group Windows --key ElectricBorderCornerRatio 0.3
kw --file kwinrc --group Xwayland --key Scale "$XWAYLAND_SCALE"

# Tuilage : marge de 4 px et disposition 25/50/25 sur chaque écran déjà connu
# (les groupes [Tiling][<bureau>][<écran>] sont créés par KWin à la connexion).
tiles='{"layoutDirection":"horizontal","tiles":[{"width":0.25},{"width":0.5},{"width":0.25}]}'
grep -o '^\[Tiling\]\[[^]]*\]\[[^]]*\]' "$CFG/kwinrc" 2>/dev/null | sort -u | while read -r g; do
    desk=$(sed -E 's/^\[Tiling\]\[([^]]*)\]\[([^]]*)\]$/\1/' <<<"$g")
    scr=$(sed -E 's/^\[Tiling\]\[([^]]*)\]\[([^]]*)\]$/\2/' <<<"$g")
    [[ -n $desk && -n $scr ]] || continue   # groupe incomplet (ex. [Tiling][][…]) : ignoré
    kw --file kwinrc --group Tiling --group "$desk" --group "$scr" --key padding 4
    kw --file kwinrc --group Tiling --group "$desk" --group "$scr" --key tiles "$tiles"
done

# ── Application en direct + fond d'écran (session Plasma uniquement) ────────
wall="${WALLPAPER_DIR/#\~/$HOME}"; wall="${wall%/}/"
[[ -d $wall ]] || warn "dossier de fonds d'écran introuvable : $wall"
if in_session && has qdbus6 && qdbus6 org.kde.plasmashell /PlasmaShell &>/dev/null; then
    plasma-apply-colorscheme --accent-color "#686b6f" We10XOSDark >/dev/null 2>&1 || true
    plasma-apply-desktoptheme We10XOS-dark >/dev/null 2>&1 || true
    plasma-apply-cursortheme --size 36 Win10OS-cursors >/dev/null 2>&1 || true
    /usr/lib/plasma-changeicons We10X-black-dark >/dev/null 2>&1 || true
    qdbus6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
        desktops().forEach(function (d) {
            d.wallpaperPlugin = 'a2n.blur';
            d.currentConfigGroup = ['Wallpaper', 'a2n.blur', 'General'];
            d.writeConfig('IsSlideshow', true);
            d.writeConfig('SlidePaths', '$wall');
            d.writeConfig('SlideInterval', 120);
            d.writeConfig('SlideshowMode', 4);
            d.writeConfig('BlurRadius', 50);
            d.writeConfig('ActiveColor', true);
            d.writeConfig('ActiveColorColor', '#000000');
            d.reloadConfig();
        });" >/dev/null
    qdbus6 org.kde.KWin /KWin reconfigure &>/dev/null || true
    success "thème appliqué (décoration et effets complets après reconnexion)"
else
    warn "hors session Plasma : fond d'écran non réglé, relancer ce module depuis la session"
    success "réglages écrits (effectifs à la prochaine ouverture de session)"
fi
