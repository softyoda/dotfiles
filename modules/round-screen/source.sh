#!/usr/bin/env bash
# Chemin dérivé à l'exécution ; aucune valeur machine dans le dépôt.
source "$MODULE_DIR/upstream.env"
LINUX_ROND_SOURCE="${XDG_DATA_HOME:-$HOME/.local/share}/linux-rond/source"
ensure_linux_rond_source() {
    mkdir -p "$(dirname "$LINUX_ROND_SOURCE")"
    if [[ ! -d $LINUX_ROND_SOURCE ]]; then
        git init -q "$LINUX_ROND_SOURCE"
        git -C "$LINUX_ROND_SOURCE" remote add origin "$LINUX_ROND_URL"
    fi
    [[ $(git -C "$LINUX_ROND_SOURCE" remote get-url origin) == "$LINUX_ROND_URL" ]] || {
        printf '%s\n' 'Linux Rond : origine inattendue, dépôt conservé.' >&2; return 1;
    }
    [[ -z $(git -C "$LINUX_ROND_SOURCE" status --porcelain) ]] || {
        printf '%s\n' 'Linux Rond : modifications locales présentes, dépôt conservé.' >&2; return 1;
    }
    if [[ $(git -C "$LINUX_ROND_SOURCE" rev-parse HEAD 2>/dev/null || true) != "$LINUX_ROND_REVISION" ]]; then
        git -C "$LINUX_ROND_SOURCE" fetch --depth 1 origin "$LINUX_ROND_REVISION"
        git -C "$LINUX_ROND_SOURCE" checkout --detach "$LINUX_ROND_REVISION"
    fi
}
