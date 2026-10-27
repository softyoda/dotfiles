#!/usr/bin/env bash
# Réglages du démon via la CLI `mullvad` (version 2026.x) + réglages de l’interface.
# Pays de sortie modifiable : MULLVAD_LOCATION=fr dotctl apply mullvad
set -euo pipefail
source "$DOTFILES_LIB"

LOCATION="${MULLVAD_LOCATION:-be}"

enable_system mullvad-daemon.service mullvad-early-boot-blocking.service

# Attendre que le démon réponde
for _ in {1..20}; do mullvad status &>/dev/null && break; sleep 0.5; done

mullvad relay set location $LOCATION
mullvad relay set multihop off
mullvad auto-connect set on
mullvad lan set allow
mullvad lockdown-mode set off
mullvad tunnel set ipv6 off
mullvad tunnel set quantum-resistant on
mullvad tunnel set daita on
mullvad tunnel set daita-direct-only off      # DAITA : multihop automatique si nécessaire
mullvad anti-censorship set mode auto
mullvad dns set default
success "réglages du démon Mullvad appliqués (sortie : $LOCATION)"

# Interface graphique : fusion clé par clé (le fichier contient aussi un état volatil)
gui="${XDG_CONFIG_HOME:-$HOME/.config}/Mullvad VPN/gui_settings.json"
mkdir -p "$(dirname "$gui")"
python3 - "$gui" <<'EOF'
import json, sys, pathlib
p = pathlib.Path(sys.argv[1])
d = json.loads(p.read_text()) if p.exists() else {}
d.update({"preferredLocale": "system", "autoConnect": True, "enableSystemNotifications": True,
          "monochromaticIcon": False, "startMinimized": True, "unpinnedWindow": True, "animateMap": True})
p.write_text(json.dumps(d, separators=(",", ":")))
EOF
success "interface Mullvad : démarrage réduit, notifications"

if ! mullvad account get &>/dev/null; then
    warn "pas encore connecté à un compte : mullvad account login (voir dotctl info mullvad)"
fi
