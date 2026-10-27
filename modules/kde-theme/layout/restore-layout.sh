#!/usr/bin/env bash
# OPTIONNEL — restaure la disposition du panneau (barre des tâches en bas, applets,
# zone de notification) depuis la copie nettoyée de ce dossier.
# Écrase ~/.config/plasma-org.kde.plasma.desktop-appletsrc (sauvegarde .bak-DATE).
# Les positions des icônes du bureau, les correspondances d'écrans et le fond
# d'écran ne sont PAS dans la copie (le fond est réglé par apply.sh du module).
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
cfg="${XDG_CONFIG_HOME:-$HOME/.config}"
rc="$cfg/plasma-org.kde.plasma.desktop-appletsrc"

read -r -p "Remplacer la disposition Plasma actuelle ? [o/N] " r
[[ $r == [oOyY]* ]] || exit 0

systemctl --user stop plasma-plasmashell.service || true
[[ -f $rc ]] && cp -a "$rc" "$rc.bak-$(date +%Y%m%d-%H%M%S)"
cp "$here/plasma-org.kde.plasma.desktop-appletsrc" "$rc"

# Réglages du panneau (identifiant 73 dans la copie)
kwriteconfig6 --file plasmashellrc --group PlasmaViews --group "Panel 73" --key floating 0
kwriteconfig6 --file plasmashellrc --group PlasmaViews --group "Panel 73" --key panelOpacity 2
kwriteconfig6 --file plasmashellrc --group PlasmaViews --group "Panel 73" --group Defaults --key thickness 46

systemctl --user start plasma-plasmashell.service
echo "Disposition restaurée. Relancer « dotctl apply kde-theme » pour remettre le fond d'écran."
