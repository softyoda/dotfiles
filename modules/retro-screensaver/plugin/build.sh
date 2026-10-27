#!/usr/bin/env bash
# Compile le plugin d'actions de conteneur Plasma « local.retro.contextmenu ».
# Usage : build.sh <dossier_sortie>   → <dossier_sortie>/local.retro.contextmenu.so (+ check)
# Dépendances : gcc, qt6-base (moc), libplasma, kcoreaddons, kconfig (en-têtes inclus).
set -euo pipefail
src="$(cd "$(dirname "$0")" && pwd)"
out="${1:?dossier de sortie}"
mkdir -p "$out"
work="$(mktemp -d)"; trap 'rm -rf "$work"' EXIT
cp "$src/menu.cpp" "$src/menu.json" "$src/check.cpp" "$work/"

incs=($(pkg-config --cflags Qt6Widgets)
       -I/usr/include/Plasma -I/usr/include/KF6/KCoreAddons -I/usr/include/KF6/KConfig
       -I/usr/include/KF6/KConfigCore)
flags=(-std=c++20 -O2 -fPIC "${incs[@]}")
libs=($(pkg-config --libs Qt6Widgets) -lPlasma -lKF6CoreAddons -lKF6ConfigCore)

/usr/lib/qt6/moc "${incs[@]}" -I"$work" "$work/menu.cpp" -o "$work/menu.moc"
g++ "${flags[@]}" -I"$work" -shared "$work/menu.cpp" -o "$out/local.retro.contextmenu.so" "${libs[@]}"
g++ "${flags[@]}" "$work/check.cpp" -o "$out/check" "${libs[@]}"
# Vérifie que le plugin se charge et embarque bien le menu KDE d'origine
QT_QPA_PLATFORM=offscreen "$out/check" "$out/local.retro.contextmenu.so"
