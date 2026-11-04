#!/usr/bin/env bash
set -euo pipefail
source "$DOTFILES_LIB"
need_vars CATALOG_URL CATALOG_AGENT_ID CATALOG_LOCAL_SOURCES CATALOG_LAUNCH_KEY_SOURCE
for file in client.json local-paths.json sources.json agent.json; do python3 -m json.tool "$HOME/.config/file-catalog/$file" >/dev/null; done
install -m 600 "$CATALOG_LAUNCH_KEY_SOURCE" "$HOME/.config/file-catalog/local-launcher.key"
if [[ -n ${CATALOG_AGENT_KEY_SOURCE:-} && -f "$CATALOG_AGENT_KEY_SOURCE" ]]; then
    install -m 600 "$CATALOG_AGENT_KEY_SOURCE" "$HOME/.config/file-catalog/agent.key"
    enable_user file-catalog-agent.timer
fi
