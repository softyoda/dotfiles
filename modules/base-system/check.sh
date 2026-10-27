#!/usr/bin/env bash
# Exit 0 si les réglages de base sont en place.
command -v paru >/dev/null &&
flatpak remotes --system --columns=name 2>/dev/null | grep -qx flathub &&
grep -Eq '^[[:space:]]*Color[[:space:]]*$' /etc/pacman.conf &&
grep -Eq '^[[:space:]]*ILoveCandy[[:space:]]*$' /etc/pacman.conf &&
grep -Eq '^[[:space:]]*DisableDownloadTimeout[[:space:]]*$' /etc/pacman.conf &&
grep -Eq '^[[:space:]]*ParallelDownloads[[:space:]]*=[[:space:]]*10[[:space:]]*$' /etc/pacman.conf &&
grep -Eq '^[[:space:]]*SkipReview[[:space:]]*$' /etc/paru.conf &&
grep -qx 'SUDO_ASKPASS=/usr/bin/ksshaskpass' /etc/environment &&
id -nG "$USER" | tr ' ' '\n' | grep -qx wheel
