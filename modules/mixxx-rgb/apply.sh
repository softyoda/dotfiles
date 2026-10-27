#!/usr/bin/env bash
# Compile Mixxx 2.5.6 + patch « rgb » dans ~/.local/opt/mixxx-rgb (une seule fois
# par version/patch, grâce à un fichier témoin) puis le plugin Qt « space alias ».
set -euo pipefail
source "$DOTFILES_LIB"

VERSION=2.5.6
TARBALL_URL="https://github.com/mixxxdj/mixxx/archive/refs/tags/$VERSION.tar.gz"
TARBALL_SHA256=9cfc9025d50d2511767ee52a07b8854f75c581f0585197d043bc219fcf9f9050
PREFIX="$HOME/.local/opt/mixxx-rgb"
PATCH="$MODULE_DIR/files/mixxx-rgb.patch"
STAMP="$PREFIX/.stamp-$VERSION-$(sha256sum "$PATCH" | cut -c1-12)"

# 1. Mixxx
if [[ -x "$PREFIX/bin/mixxx" && -f "$STAMP" ]]; then
    info "Mixxx rgb $VERSION déjà compilé (rien à faire)"
else
    has_pkg cmake && has_pkg ninja && has_pkg microsoft-gsl || {
        info "installation des outils de compilation (cmake, ninja, microsoft-gsl)"
        as_root pacman -S --needed --noconfirm cmake ninja microsoft-gsl base-devel git qt6-tools qt6-svg qt6-5compat
    }
    work=$(mktemp -d)
    trap 'rm -rf -- "$work"' EXIT
    info "téléchargement de Mixxx $VERSION"
    curl -fsSL -o "$work/mixxx.tar.gz" "$TARBALL_URL"
    echo "$TARBALL_SHA256  $work/mixxx.tar.gz" | sha256sum -c --quiet - || { error "somme de contrôle de l'archive incorrecte"; exit 1; }
    mkdir "$work/src"
    tar -xzf "$work/mixxx.tar.gz" -C "$work/src"
    src="$work/src/mixxx-$VERSION"
    patch -d "$src" -p1 -s < "$PATCH"
    info "compilation (plusieurs dizaines de minutes)"
    cmake -S "$src" -B "$work/build" -G Ninja \
        -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="$PREFIX" \
        -DQT6=ON -DQML=OFF -DOPTIMIZE=portable -DBUILD_TESTING=OFF \
        -DFFMPEG=OFF -DENGINEPRIME=OFF -DINSTALL_USER_UDEV_RULES=ON \
        -DBATTERY=ON -DBROADCAST=ON -DBULK=ON -DFAAD=ON -DHID=ON -DKEYFINDER=ON \
        -DLILV=ON -DLOCALECOMPARE=ON -DMAD=ON -DMODPLUG=ON -DOPUS=ON \
        -DQTKEYCHAIN=ON -DRUBBERBAND=ON -DVINYLCONTROL=ON -DWAVPACK=ON
    cmake --build "$work/build"
    cmake --install "$work/build"
    find "$PREFIX" -maxdepth 1 -name '.stamp-*' -delete
    touch "$STAMP"
    success "Mixxx rgb $VERSION installé dans $PREFIX"
fi

# 2. Plugin Qt « space alias » (Espace envoyé comme touche D = lecture alternative)
plug="$HOME/.local/lib/mixxx-space-alias"
if [[ ! -f "$plug/generic/libmixxxspacealias.so" || "$plug/spacealias.cpp" -nt "$plug/generic/libmixxxspacealias.so" ]]; then
    info "compilation du plugin space-alias"
    tmp=$(mktemp -d)
    qtinc=$(pkg-config --cflags Qt6Widgets Qt6Gui Qt6Core)
    moc="$(qtpaths6 --query QT_INSTALL_LIBEXECS 2>/dev/null || echo /usr/lib/qt6)/moc"
    [[ -x "$moc" ]] || moc=moc6
    "$moc" -i "$plug/spacealias.cpp" -o "$tmp/spacealias.moc"
    mkdir -p "$plug/generic"
    # shellcheck disable=SC2086
    g++ -std=c++17 -fPIC -shared -O2 $qtinc -I"$tmp" -I"$plug" "$plug/spacealias.cpp" \
        $(pkg-config --libs Qt6Widgets Qt6Gui Qt6Core) -o "$plug/generic/libmixxxspacealias.so"
    rm -rf -- "$tmp"
    success "plugin space-alias compilé"
fi
update-desktop-database "${XDG_DATA_HOME:-$HOME/.local/share}/applications" 2>/dev/null || true
