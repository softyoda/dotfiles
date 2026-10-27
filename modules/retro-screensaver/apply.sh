#!/usr/bin/env bash
set -euo pipefail
source "$DOTFILES_LIB"

# Plugin d'actions de conteneur Plasma (menu clic droit), compilé depuis plugin/
PLUGDIR="$HOME/.local/lib/qt6/plugins/plasma/containmentactions"
build=$(mktemp -d); trap 'rm -rf "$build"' EXIT
info "compilation du plugin de menu…"
bash "$MODULE_DIR/plugin/build.sh" "$build"
install -Dm755 "$build/local.retro.contextmenu.so" "$PLUGDIR/local.retro.contextmenu.so"

# Script KWin de détection du plein écran + inhibitions KeepAwake bloquées
kwriteconfig6 --file kwinrc --group Plugins --key local-retro-guardEnabled true
kwriteconfig6 --file powerdevilrc --group Inhibitions --key BlockedInhibitions \
    "io.github.segevfiner.keepawake-rs:User requested,keepawake-rs:User requested"

# Services : l'autostart .desktop est volontairement désactivé (Hidden=true), c'est le service qui lance xscreensaver
enable_user retro-screensaver.service retro-saver-guard.service
in_session && qdbus6 org.kde.KWin /KWin reconfigure >/dev/null 2>&1 || true
success "économiseur rétro en place (menu clic droit : redémarrer plasma-plasmashell.service)"
