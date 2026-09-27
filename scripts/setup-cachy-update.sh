#!/usr/bin/env bash
set -euo pipefail

DOTFILES="$(cd "$(dirname "$0")/.." && pwd)"
OVERRIDE="$HOME/.local/share/arch-update/lib"
ARCH_UPDATE_CONF="$HOME/.config/arch-update/arch-update.conf"

echo "▶ Préparation des bibliothèques utilisateur…"
mkdir -p "$(dirname "$OVERRIDE")" "$(dirname "$ARCH_UPDATE_CONF")"
staging=$(mktemp -d "$(dirname "$OVERRIDE")/.lib-install.XXXXXX")
trap 'rm -rf -- "$staging"' EXIT

echo "▶ Liens symboliques vers les libs système…"
for f in /usr/share/arch-update/lib/*; do
    ln -s "$f" "$staging/$(basename "$f")"
done

echo "▶ Copie des libs patchées…"
# Remplacer les liens dans le répertoire de préparation, jamais leur cible système.
cp --remove-destination "$DOTFILES/cachy-update/lib/"*.sh "$staging/"
for f in "$staging/"*.sh; do
    bash -n "$f"
done
stamp=$(date +%Y%m%d-%H%M%S)
if [ -e "$OVERRIDE" ] || [ -L "$OVERRIDE" ]; then
    mv "$OVERRIDE" "${OVERRIDE}.backup-${stamp}-$$"
fi
mv "$staging" "$OVERRIDE"
trap - EXIT

echo "▶ Config arch-update (NewsNum=0)…"
if [ -e "$ARCH_UPDATE_CONF" ]; then
    cp -a "$ARCH_UPDATE_CONF" "${ARCH_UPDATE_CONF}.backup-${stamp}-$$"
fi
cp --remove-destination "$DOTFILES/cachy-update/arch-update.conf" "$ARCH_UPDATE_CONF"

echo "✓ Mises à jour automatiques activées !"
echo "  → Au prochain update : Y=interactif / A=confirmations des paquets automatiques"
echo "  → Le mode A active aussi les nettoyages et redémarrages de services prévus."
echo "  → L'authentification, les fichiers .pacnew et le redémarrage du PC peuvent demander une intervention."
