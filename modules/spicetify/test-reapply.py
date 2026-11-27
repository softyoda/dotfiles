#!/usr/bin/env python3
"""Teste les sauvegardes et le blocage du client non patché, sans lancer Spotify."""

import os
from pathlib import Path
import subprocess
import tarfile
import tempfile

files = Path(__file__).resolve().parent / "files"


def executable(path, script):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("#!/usr/bin/env bash\nset -eu\n" + script)
    path.chmod(0o700)


with tempfile.TemporaryDirectory() as root:
    base = Path(root)
    env = dict(os.environ, **{
        "HOME": root,
        "XDG_CONFIG_HOME": str(base / "config"),
        "XDG_CACHE_HOME": str(base / "cache"),
        "XDG_DATA_HOME": str(base / "data"),
        "XDG_STATE_HOME": str(base / "state"),
        "PATH": f"{base / 'bin'}:{os.environ['PATH']}",
    })
    fixture = base / "cache/spotify/Browser/Local Storage/leveldb/000001.log"
    fixture.parent.mkdir(parents=True)
    fixture.write_bytes(b"marketplace:installed:test")
    executable(base / "bin/pgrep", 'exit "${MOCK_RUNNING:-1}"\n')
    executable(base / "bin/kdialog", 'exit 0\n')
    executable(base / "bin/spotify-launcher", r'''
if [[ "$1" == --skip-update ]]; then
    touch "$HOME/started"
    exit 0
fi
compgen -G "$XDG_STATE_HOME/spicetify-profile-backups/*.tar.gz" >/dev/null
data="$XDG_DATA_HOME/spotify-launcher"
mkdir -p "$data/install/usr/share/spotify/Apps"
printf '%s\n' '{"version":"1:1.3.9.7.gabc"}' > "$data/state.json"
touch "$data/install/usr/share/spotify/Apps/xpui.spa"
''')
    executable(base / ".spicetify/spicetify", r'''
[[ "$*" == '--no-restart backup apply' ]]
data="$XDG_DATA_HOME/spotify-launcher"
grep -Fxq 'app.last-launched-version="1.3.9.7.gabc"' "$data/spicetify-version.prefs"
if [[ "${MOCK_PATCH_FAILURE:-0}" == 1 ]]; then exit 1; fi
apps="$data/install/usr/share/spotify/Apps"
rm -- "$apps/xpui.spa"
mkdir -p "$apps/xpui/helper"
printf '%s\n' '<script src="helper/spicetifyWrapper.js"></script>' > "$apps/xpui/index.html"
for file in helper/spicetifyWrapper.js spicetify-routes-marketplace.{js,json}; do
    echo fixture > "$apps/xpui/$file"
done
''')
    helper = base / ".local/bin/spicetify-reapply"
    helper.parent.mkdir(parents=True)
    helper.symlink_to(files / "spicetify-reapply")

    launcher = ["bash", str(files / "spotify-with-spicetify")]
    result = subprocess.run(launcher, env=dict(env, MOCK_PATCH_FAILURE="1"), capture_output=True)
    assert result.returncode != 0
    assert not (base / "started").exists()

    subprocess.run(launcher, env=env, check=True)
    assert (base / "started").exists()
    snapshots = list((base / "state/spicetify-profile-backups").glob("*.tar.gz"))
    assert len(snapshots) == 1
    assert snapshots[0].stat().st_mode & 0o777 == 0o600
    with tarfile.open(snapshots[0]) as archive:
        entry = archive.extractfile("spotify/Browser/Local Storage/leveldb/000001.log")
        assert entry and entry.read() == fixture.read_bytes()

    fixture.write_bytes(b"marketplace:installed:updated")
    subprocess.run([str(helper), "--check-update"], env=dict(env, MOCK_RUNNING="0"), check=True)
    assert len(list(snapshots[0].parent.glob("*.tar.gz"))) == 1

print("OK : sauvegarde privée avant la mise à jour, patch obligatoire et report si Spotify est ouvert.")
