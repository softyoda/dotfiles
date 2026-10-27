#!/usr/bin/env bash
[[ $(kreadconfig6 --file kwinrc --group Plugins --key round-safe-areaEnabled) == true ]] &&
cmp -s "$MODULE_DIR/kwin-script/round-safe-area/contents/code/main.js" ~/.local/share/kwin/scripts/round-safe-area/contents/code/main.js &&
diff -qr "$MODULE_DIR/org.softyoda.arcpanel" ~/.local/share/plasma/plasmoids/org.softyoda.arcpanel >/dev/null
