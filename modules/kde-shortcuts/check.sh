#!/usr/bin/env bash
r() { kreadconfig6 --file kglobalshortcutsrc --group "$1" --key "$2"; }
[[ $(r kwin Cube) == Meta+C,* ]] &&
[[ $(r plasmashell "next activity") == Meta+A,* ]] &&
[[ $(r plasmashell "previous activity") == Meta+Shift+A,* ]] &&
[[ $(kreadconfig6 --file kglobalshortcutsrc --group services --group org.kde.konsole.desktop --key _launch) == none ]]
