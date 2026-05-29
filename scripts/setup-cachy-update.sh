#!/usr/bin/env bash
set -e

DOTFILES="$(cd "$(dirname "$0")/.." && pwd)"
OVERRIDE="$HOME/.local/share/arch-update/lib"
ARCH_UPDATE_CONF="$HOME/.config/arch-update/arch-update.conf"

echo "▶ Création du répertoire override…"
mkdir -p "$OVERRIDE"

echo "▶ Liens symboliques vers les libs système…"
for f in /usr/share/arch-update/lib/*; do
    ln -sf "$f" "$OVERRIDE/$(basename "$f")"
done

echo "▶ Copie des libs patchées…"
cp -f "$DOTFILES/cachy-update/lib/"*.sh "$OVERRIDE/"

echo "▶ Config arch-update (NewsNum=0)…"
if [ ! -f "$ARCH_UPDATE_CONF" ]; then
    arch-update --gen-config 2>/dev/null || true
fi
cp -f "$DOTFILES/cachy-update/arch-update.conf" "$ARCH_UPDATE_CONF"

echo "▶ paru.conf : ajout de SkipReview…"
if ! grep -q "^SkipReview" /etc/paru.conf 2>/dev/null; then
    pkexec bash -c "sed -i '/^\[options\]/a SkipReview' /etc/paru.conf"
fi

echo "✓ Mises à jour automatiques activées !"
echo "  → Au prochain update : Y=interactif  /  a=tout automatique sans pause"
