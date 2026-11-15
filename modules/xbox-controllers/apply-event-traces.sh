#!/usr/bin/env bash
set -euo pipefail
source "$DOTFILES_LIB"
as_root python3 /usr/local/libexec/xone-event-traces.py enable
success "Traces Xbox actives, sans reset ni rechargement de pilote."
