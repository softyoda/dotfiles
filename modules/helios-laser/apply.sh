#!/usr/bin/env bash
# SDK Helios (Grix/helios_dac, commit épinglé) compilé en libHeliosDacAPI.so,
# règle udev rechargée, pont UDP→USB activé.
set -euo pipefail
source "$DOTFILES_LIB"

COMMIT=5881d9f8dd092f18be726cdfd687b9908108d62a
LIB=/usr/local/lib/libHeliosDacAPI.so
STAMP=/usr/local/lib/.libHeliosDacAPI.commit

if [[ -f "$LIB" && $(cat "$STAMP" 2>/dev/null) == "$COMMIT" ]] || [[ -f "$LIB" && ! -f "$STAMP" ]]; then
    info "libHeliosDacAPI.so déjà installée"
else
    work=$(mktemp -d)
    trap 'rm -rf -- "$work"' EXIT
    info "téléchargement du SDK Helios ($COMMIT)"
    curl -fsSL "https://github.com/Grix/helios_dac/archive/$COMMIT.tar.gz" | tar -xz -C "$work"
    sdk="$work/helios_dac-$COMMIT/sdk/cpp"
    g++ -std=c++17 -O2 -fPIC -shared -w -I"$sdk" -I"$sdk/shared_library" \
        "$sdk/shared_library/HeliosDacAPI.cpp" "$sdk/HeliosDac.cpp" \
        "$sdk/idn/idn.cpp" "$sdk/idn/idnServerList.cpp" "$sdk/idn/plt-posix.cpp" \
        -lusb-1.0 -lpthread -o "$work/libHeliosDacAPI.so"
    as_root install -D -m 755 "$work/libHeliosDacAPI.so" "$LIB"
    echo "$COMMIT" | as_root tee "$STAMP" >/dev/null
    success "libHeliosDacAPI.so installée dans /usr/local/lib"
fi

as_root udevadm control --reload-rules
as_root udevadm trigger --subsystem-match=usb --attr-match=idVendor=1209 --attr-match=idProduct=e500 || true
enable_user helios-bridge.service
success "pont Helios actif (UDP 127.0.0.1:45457)"
