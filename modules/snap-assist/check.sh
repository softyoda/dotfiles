#!/usr/bin/env bash
[[ -d "${XDG_DATA_HOME:-$HOME/.local/share}/kwin/scripts/org.kde.snapassist" ]] &&
[[ $(kreadconfig6 --file kwinrc --group Plugins --key org.kde.snapassistEnabled) == true ]] &&
cmp -s "$MODULE_DIR/org.kde.snapassist/contents/ui/main.qml" \
       "${XDG_DATA_HOME:-$HOME/.local/share}/kwin/scripts/org.kde.snapassist/contents/ui/main.qml"
