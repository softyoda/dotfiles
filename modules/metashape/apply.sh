#!/usr/bin/env bash
# Installe Metashape Pro dans /opt/metashape-pro s'il manque. La licence
# n'est jamais gérée ici : voir README.md.
set -euo pipefail
source "$DOTFILES_LIB"

VERSION=2_1_3
URL="https://download.agisoft.com/metashape-pro_${VERSION}_amd64.tar.gz"

if [[ -x /opt/metashape-pro/metashape ]]; then
    info "Metashape déjà installé dans /opt/metashape-pro"
else
    work=$(mktemp -d)
    trap 'rm -rf -- "$work"' EXIT
    info "téléchargement de Metashape Pro ${VERSION//_/.} (≈ 150 Mo)"
    curl -fL --progress-bar -o "$work/metashape.tar.gz" "$URL"
    tar -xzf "$work/metashape.tar.gz" -C "$work"
    as_root rm -rf /opt/metashape-pro
    as_root mv "$work/metashape-pro" /opt/metashape-pro
    as_root chown -R root:root /opt/metashape-pro
    as_root chmod -R a+rX /opt/metashape-pro
    success "Metashape installé"
fi
warn "licence à activer à la main au premier lancement (voir README du module)"
