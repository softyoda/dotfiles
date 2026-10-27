#!/usr/bin/env bash
# Thème en place : clés principales + paquets de thème présents (et à jour pour ceux du module).
DATA="${XDG_DATA_HOME:-$HOME/.local/share}"
F="$MODULE_DIR/files"
rd() { kreadconfig6 "$@"; }
has_icon_theme() { [[ -d $DATA/icons/$1 || -d /usr/share/icons/$1 || -d $HOME/.icons/$1 ]]; }

[[ $(rd --file kdeglobals --group General --key ColorScheme) == We10XOSDark ]] &&
[[ $(rd --file kdeglobals --group General --key AccentColor) == 104,107,111 ]] &&
[[ $(rd --file kdeglobals --group Icons --key Theme) == We10X-black-dark ]] &&
[[ $(rd --file kdeglobals --group KDE --key LookAndFeelPackage) == com.github.yeyushengfan258.We10XOS-dark ]] &&
[[ $(rd --file plasmarc --group Theme --key name) == We10XOS-dark ]] &&
[[ $(rd --file ksplashrc --group KSplash --key Theme) == Watch_Dogs_Theme ]] &&
[[ $(rd --file kwinrc --group org.kde.kdecoration2 --key theme) == __aurorae__svg__We10XOS-dark ]] &&
[[ $(rd --file kwinrc --group Plugins --key glassEnabled) == true ]] &&
[[ $(rd --file kwinrc --group Plugins --key wobblywindowsEnabled) == true ]] &&
[[ $(rd --file kwinrc --group Effect-blur --key BlurStrength) == 11 ]] &&
[[ -d $DATA/plasma/look-and-feel/com.github.yeyushengfan258.We10XOS-dark ]] &&
[[ -d $DATA/plasma/desktoptheme/We10XOS-dark ]] &&
[[ -d $DATA/aurorae/themes/We10XOS-dark ]] &&
has_icon_theme We10X-black-dark && has_icon_theme Win10OS-cursors &&
cmp -s "$F/color-schemes/We10XOSDark.colors" "$DATA/color-schemes/We10XOSDark.colors" &&
diff -rq "$F/look-and-feel/Watch_Dogs_Theme" "$DATA/plasma/look-and-feel/Watch_Dogs_Theme" >/dev/null &&
diff -rq "$F/kwin-effects/kwin4_effect_geometry_change" "$DATA/kwin/effects/kwin4_effect_geometry_change" >/dev/null &&
grep -q '^wallpaperplugin=a2n.blur' "${XDG_CONFIG_HOME:-$HOME/.config}/plasma-org.kde.plasma.desktop-appletsrc"
