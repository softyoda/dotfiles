#!/usr/bin/env bash
# Surcharges DLL du préfixe par défaut (~/.wine) : ddraw/dinput/dinput8 en
# « native,builtin » (wrappers type dgVoodoo / dinput8 des vieux jeux).
set -euo pipefail
source "$DOTFILES_LIB"

update-desktop-database "${XDG_DATA_HOME:-$HOME/.local/share}/applications" 2>/dev/null || true
prefix="${WINEPREFIX:-$HOME/.wine}"
if [[ ! -d "$prefix" ]]; then
    info "pas de préfixe $prefix : surcharges DLL ignorées (relancer après le premier lancement de Wine)"
    exit 0
fi
for dll in ddraw dinput dinput8; do
    current=$(WINEPREFIX="$prefix" wine reg query 'HKCU\Software\Wine\DllOverrides' /v "$dll" 2>/dev/null | awk -v d="$dll" '$1==d {print $3}' | tr -d '\r')
    if [[ "$current" != "native,builtin" ]]; then
        WINEPREFIX="$prefix" wine reg add 'HKCU\Software\Wine\DllOverrides' /v "$dll" /t REG_SZ /d native,builtin /f >/dev/null 2>&1
        info "surcharge $dll = native,builtin"
    fi
done
success "surcharges DLL du préfixe $prefix à jour"
