#!/bin/bash

BLUE='\033[0;34m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'; BOLD='\033[1m'

info()    { echo -e "${BLUE}  →${NC} $1"; }
success() { echo -e "${GREEN}  ✓${NC} $1"; }
warn()    { echo -e "${YELLOW}  ⚠${NC} $1"; }
error()   { echo -e "${RED}  ✗${NC} $1"; }
header()  { echo -e "\n${BOLD}${BLUE}━━ $1 ━━${NC}"; }

is_installed_pacman() { pacman -Qq "$1" &>/dev/null; }
is_installed_flatpak() { flatpak list --app --columns=application 2>/dev/null | grep -q "^$1$"; }
is_installed_cmd()    { command -v "$1" &>/dev/null; }
