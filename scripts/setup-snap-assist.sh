#!/usr/bin/env bash
set -euo pipefail

DOTFILES="$(cd "$(dirname "$0")/.." && pwd)"
plugin=org.kde.snapassist
package="$DOTFILES/kde/kwin-scripts/$plugin"
data_home="${XDG_DATA_HOME:-$HOME/.local/share}"

for cmd in kpackagetool6 kwriteconfig6; do
    command -v "$cmd" >/dev/null || { echo "Commande KDE Plasma 6 manquante : $cmd" >&2; exit 1; }
done

if [[ -d "$data_home/kwin/scripts/$plugin" ]]; then
    kpackagetool6 --type KWin/Script --upgrade "$package"
else
    kpackagetool6 --type KWin/Script --install "$package"
fi
kwriteconfig6 --file kwinrc --group Plugins --key "${plugin}Enabled" true

if command -v qdbus6 >/dev/null && qdbus6 org.kde.KWin /Scripting >/dev/null 2>&1; then
    if [[ $(qdbus6 org.kde.KWin /Scripting org.kde.kwin.Scripting.isScriptLoaded "$plugin") == true ]]; then
        qdbus6 org.kde.KWin /Scripting org.kde.kwin.Scripting.unloadScript "$plugin" >/dev/null
    fi
    qdbus6 org.kde.KWin /Scripting org.kde.kwin.Scripting.loadDeclarativeScript \
        "$data_home/kwin/scripts/$plugin/contents/ui/main.qml" "$plugin" >/dev/null
    qdbus6 org.kde.KWin /Scripting org.kde.kwin.Scripting.start
    [[ $(qdbus6 org.kde.KWin /Scripting org.kde.kwin.Scripting.isScriptLoaded "$plugin") == true ]]
    echo 'Snap Assist installé et chargé dans la session KDE.'
else
    echo 'Snap Assist installé ; activation à la prochaine ouverture de session KDE.'
fi
