#!/usr/bin/env python3
"""Tests hors ligne : aucun gestionnaire de paquets réel n'est exécuté."""
import os
from pathlib import Path
import subprocess
import tempfile

lib = Path(__file__).resolve().parent / "lib"
for script in lib.glob("*.sh"):
    subprocess.run(["bash", "-n", str(script)], check=True)

with tempfile.TemporaryDirectory() as directory:
    env = dict(os.environ, LIB=str(lib), TESTDIR=directory, LC_ALL="C")
    common = r'''
eval_gettext() { printf '%s' "$1"; }
info_msg() { :; }; main_msg() { :; }; warning_msg() { :; }
error_msg() { :; }; quit_msg() { :; }
icon_updates-available() { :; }; icon_up-to-date() { :; }
'''
    for answer in ("A", "a", "Y", "n"):
        result = subprocess.run(["bash", "-c", common + r'''
ask_msg() { answer="$TESTANSWER"; }
timeout() { shift; "$@"; }
checkupdates() { echo 'example 1 -> 2'; }
checkupdates_db_tmpdir_prefix="$TESTDIR/check-"
statedir="$TESTDIR"
update_check_timeout=2
no_color=true
source "$LIB/list_packages.sh"
printf '\nRESULT:%s:%s\n' "$proceed_with_update" "$noconfirm_mode"
'''], env=dict(env, TESTANSWER=answer), capture_output=True, text=True)
        if answer == "n":
            assert result.returncode == 4, result
        else:
            assert result.returncode == 0, result.stderr
            expected = "RESULT:true:true" if answer in ("A", "a") else "RESULT:true:"
            assert expected in result.stdout, result.stdout

    for mode in ("true", ""):
        result = subprocess.run(["bash", "-c", common + r'''
ask_msg() { echo UNEXPECTED_PROMPT; return 1; }
pacman() { :; }
mock_sudo() { printf 'CMD'; printf ' <%s>' "$@"; echo; }
paru() { printf 'AUR'; printf ' <%s>' "$@"; echo; }
flatpak() { printf 'FLATPAK'; printf ' <%s>' "$@"; echo; }
libdir="$LIB"
statedir="$TESTDIR"
su_cmd=mock_sudo
aur_helper=paru
pacman_color_opt=never
packages=example
aur_packages=example-aur
flatpak_packages=example-flatpak
source "$LIB/update.sh"
'''], env=dict(env, noconfirm_mode=mode), capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        assert "UNEXPECTED_PROMPT" not in result.stdout, result.stdout
        if mode:
            assert '<--noconfirm> <-Syu>' in result.stdout, result.stdout
            assert '<--noconfirm> <--skipreview> <-Syu>' in result.stdout, result.stdout
            assert 'FLATPAK <update> <-y>' in result.stdout, result.stdout
        else:
            assert '--noconfirm' not in result.stdout, result.stdout
            assert '--skipreview' not in result.stdout, result.stdout
            assert 'FLATPAK <update>\n' in result.stdout, result.stdout
print('OK : A/a automatiques, Y interactif, n annule ; commandes pacman/paru/Flatpak simulées.')
