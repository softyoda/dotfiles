"""Sauvegardes sélectives Firefox : données privées, navigateur fermé."""
from __future__ import annotations

import configparser
import fcntl
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
import time
import uuid
import zipfile

from . import core

EXTENSIONS = {
    "ublock": "uBlock0@raymondhill.net",
    "userscripts": "{aecec67f-0d10-4fa7-b7c7-609a2db280cf}",
}
LABELS = {"prefs": "Préférences about:config", "ublock": "uBlock Origin (filtres et réglages)",
          "userscripts": "Violentmonkey (userscripts et réglages)"}
# Préférences utilisateur transportables ; pas les identifiants, sessions ou chemins.
PREF_PREFIXES = ("browser.tabs.", "browser.urlbar.", "browser.search.", "browser.toolbars.",
                 "browser.compactmode.", "browser.uidensity", "toolkit.tabbox.",
                 "toolkit.legacyUserProfileCustomizations.", "mousewheel.", "general.smoothScroll",
                 "general.autoScroll", "accessibility.", "ui.key.", "layout.spellcheckDefault",
                 "media.autoplay.", "privacy.trackingprotection.", "privacy.donottrackheader.",
                 "browser.download.useDownloadDir", "browser.download.alwaysOpenPanel",
                 "browser.fullscreen.", "browser.ctrlTab.", "browser.backspace_action")
PREF_RE = re.compile(r'^\s*(?:user_)?pref\(("(?:[^"\\]|\\.)*"),\s*(.*?)\);\s*$', re.M)


def preferences(path: Path) -> dict:
    result = {}
    if path.exists():
        for m in PREF_RE.finditer(path.read_text()):
            try:
                result[json.loads(m[1])] = json.loads(m[2])
            except ValueError:
                continue
    return result


def candidates(profile: Path) -> dict:
    return {k: v for k, v in preferences(profile / "prefs.js").items()
            if k.startswith(PREF_PREFIXES)}


def profiles() -> dict[str, Path]:
    result = {}
    for base in (Path.home() / ".config/mozilla/firefox", Path.home() / ".mozilla/firefox"):
        ini = configparser.ConfigParser(interpolation=None)
        ini.read(base / "profiles.ini")
        for section in ini.sections():
            if not section.startswith("Profile"):
                continue
            name = ini.get(section, "Name", fallback=section)
            path = Path(ini.get(section, "Path"))
            if ini.getboolean(section, "IsRelative", fallback=True):
                path = base / path
            if path.is_dir():
                label = name if name not in result else f"{name} ({base})"
                result[label] = path
    return result


class ProfileLock:
    """Même verrou fcntl que Firefox ; ne ferme jamais le navigateur."""
    def __init__(self, profile: Path):
        self.profile = profile
        self.fd = None

    def __enter__(self):
        self.fd = os.open(self.profile / ".parentlock", os.O_CREAT | os.O_RDWR, 0o600)
        try:
            fcntl.lockf(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            os.close(self.fd)
            self.fd = None
            raise RuntimeError("Fermez Firefox pour ce profil, puis réessayez.")
        return self

    def __exit__(self, *args):
        os.close(self.fd)


def archive_root() -> Path:
    private = core.private_dir()
    if private is None:
        raise RuntimeError("Configurez d’abord le dossier privé dans ~/.config/dotfiles/private-path.")
    root = private / "firefox"
    # Ces données peuvent contenir des URL privées et les valeurs des userscripts.
    if root.resolve().is_relative_to(core.DOTFILES.resolve()):
        raise RuntimeError("Les sauvegardes Firefox doivent être hors du dépôt public.")
    return root


def snapshots() -> list[Path]:
    try:
        return sorted(archive_root().glob('*/manifest.json'), reverse=True)
    except RuntimeError:
        return []


def _copy_tree(src: Path, dst: Path):
    if any(p.is_symlink() for p in src.rglob('*')):
        raise RuntimeError("Lien symbolique inattendu dans les données d’extension.")
    shutil.copytree(src, dst)


def capture(profile: Path, name: str, components: list[str], keys: list[str] | None = None) -> Path:
    if not components or set(components) - LABELS.keys():
        raise ValueError("Choisissez au moins un élément à sauvegarder.")
    with ProfileLock(profile):
        root = archive_root()
        root.mkdir(parents=True, exist_ok=True, mode=0o700)
        stamp = time.strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:8]
        target = root / stamp
        staging = Path(tempfile.mkdtemp(prefix='.capture-', dir=root))
        try:
            manifest = {"version": 1, "profile": name, "created": time.strftime('%Y-%m-%d %H:%M:%S'),
                        "components": {}, "firefox": _firefox_version(profile)}
            prefs = preferences(profile / 'prefs.js')
            mapping = json.loads(prefs.get('extensions.webextensions.uuids', '{}'))
            for part in components:
                if part == 'prefs':
                    allowed = {k: v for k, v in prefs.items() if k != 'extensions.webextensions.uuids'}
                    selected = {k: allowed[k] for k in (keys if keys is not None else candidates(profile)) if k in allowed}
                    if not selected:
                        raise RuntimeError("Aucune préférence sélectionnée à sauvegarder.")
                    (staging / 'prefs.json').write_text(json.dumps(selected, indent=2, ensure_ascii=False) + '\n')
                    manifest['components'][part] = {"count": len(selected)}
                    continue
                eid = EXTENSIONS[part]
                uid = mapping.get(eid)
                if not uid:
                    raise RuntimeError(f"{LABELS[part]} absent de ce profil : décochez cet élément.")
                uuid.UUID(uid)
                xpi = profile / 'extensions' / (eid + '.xpi')
                if not xpi.is_file():
                    raise RuntimeError(f"Extension {LABELS[part]} : fichier XPI introuvable.")
                folder = staging / part
                folder.mkdir()
                shutil.copy2(xpi, folder / 'extension.xpi')
                origins = []
                for origin in sorted((profile / 'storage/default').glob('moz-extension+++' + uid + '*')):
                    if origin.name not in ('moz-extension+++' + uid,
                                          'moz-extension+++' + uid + '^userContextId=4294967295'):
                        continue
                    _copy_tree(origin, folder / origin.name)
                    origins.append(origin.name)
                legacy = profile / 'browser-extension-data' / eid
                if legacy.is_dir():
                    _copy_tree(legacy, folder / 'legacy')
                if not origins and not legacy.is_dir():
                    raise RuntimeError(f"Aucune donnée trouvée pour {LABELS[part]}.")
                manifest['components'][part] = {"uuid": uid, "origins": origins,
                                                 "legacy": legacy.is_dir()}
            (staging / 'manifest.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')
            staging.rename(target)
            return target
        except Exception:
            shutil.rmtree(staging)
            raise


def _firefox_version(profile):
    ini = configparser.ConfigParser(interpolation=None)
    ini.read(profile / 'compatibility.ini')
    return ini.get('Compatibility', 'LastVersion', fallback='inconnue')


def _merge_prefs(path: Path, updates: dict):
    original = path.read_text() if path.exists() else ''
    def keep(match):
        return '' if json.loads(match[1]) in updates else match[0]
    text = PREF_RE.sub(keep, original).rstrip() + '\n'
    text += ''.join(f'user_pref({json.dumps(k)}, {json.dumps(v, ensure_ascii=True)});\n'
                    for k, v in updates.items())
    path.write_text(text)


def restore(snapshot: Path, profile: Path, components: list[str], keys: list[str] | None = None) -> Path:
    if not components or set(components) - LABELS.keys():
        raise ValueError("Choisissez au moins un élément à restaurer.")
    manifest = json.loads((snapshot / 'manifest.json').read_text())
    if manifest.get('version') != 1:
        raise RuntimeError("Format de sauvegarde non pris en charge.")
    if not set(components) <= manifest['components'].keys():
        raise RuntimeError("Cette sauvegarde ne contient pas tous les éléments sélectionnés.")
    if any(p.is_symlink() for p in snapshot.rglob('*')):
        raise RuntimeError("Sauvegarde contenant des liens symboliques : restauration refusée.")
    selected = {}
    if 'prefs' in components:
        saved = json.loads((snapshot / 'prefs.json').read_text())
        selected = {k: v for k, v in saved.items() if k != 'extensions.webextensions.uuids'
                    and (keys is None or k in keys)}
    # Valider tous les chemins et toutes les extensions avant de toucher au profil.
    for part in set(components) - {'prefs'}:
        data = manifest['components'][part]
        uid = str(uuid.UUID(data['uuid']))
        for origin in data['origins']:
            if origin not in ('moz-extension+++' + uid, 'moz-extension+++' + uid + '^userContextId=4294967295'):
                raise RuntimeError("Chemin d’extension invalide dans la sauvegarde.")
            if not (snapshot / part / origin).is_dir():
                raise RuntimeError("Sauvegarde d’extension incomplète.")
        with zipfile.ZipFile(snapshot / part / 'extension.xpi') as z:
            ext = json.loads(z.read('manifest.json'))
        actual_id = (ext.get('browser_specific_settings', ext.get('applications', {}))
                    .get('gecko', {}).get('id'))
        if actual_id != EXTENSIONS[part]:
            raise RuntimeError("L’extension sauvegardée ne correspond pas à celle attendue.")
    with ProfileLock(profile):
        prefs = preferences(profile / 'prefs.js')
        mapping = json.loads(prefs.get('extensions.webextensions.uuids', '{}'))
        for part in set(components) - {'prefs'}:
            uid = manifest['components'][part]['uuid']
            if uid in (v for k, v in mapping.items() if k != EXTENSIONS[part]):
                raise RuntimeError("Conflit d’identifiant d’extension dans le profil cible.")
        backup = profile / ('dotfiles-backups/' + time.strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:8])
        backup.mkdir(parents=True, mode=0o700)
        touched: list[tuple[Path, bool]] = []
        def preserve(path):
            if any(old == path for old, _ in touched):
                return
            exists = path.exists()
            touched.append((path, exists))
            if exists:
                dst = backup / path.relative_to(profile)
                dst.parent.mkdir(parents=True, exist_ok=True)
                if path.is_dir(): shutil.copytree(path, dst)
                else: shutil.copy2(path, dst)
        try:
            for part in set(components) - {'prefs'}:
                eid = EXTENSIONS[part]
                data = manifest['components'][part]
                old_uid = mapping.get(eid)
                # Libérer les anciens emplacements de cette extension uniquement.
                if old_uid:
                    uuid.UUID(old_uid)
                    for origin in (profile / 'storage/default').glob('moz-extension+++' + old_uid + '*'):
                        preserve(origin)
                        shutil.rmtree(origin)
                for origin in data['origins']:
                    dst = profile / 'storage/default' / origin
                    preserve(dst)
                    if dst.exists(): shutil.rmtree(dst)
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copytree(snapshot / part / origin, dst)
                legacy = profile / 'browser-extension-data' / eid
                preserve(legacy)
                if legacy.exists(): shutil.rmtree(legacy)
                if data.get('legacy'):
                    legacy.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copytree(snapshot / part / 'legacy', legacy)
                dst = profile / 'extensions' / (eid + '.xpi')
                preserve(dst)
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(snapshot / part / 'extension.xpi', dst)
                mapping[eid] = data['uuid']
            updates = dict(selected)
            if set(components) - {'prefs'}:
                updates['extensions.webextensions.uuids'] = json.dumps(mapping)
            if updates:
                path = profile / 'prefs.js'
                preserve(path)
                _merge_prefs(path, updates)
                if selected:
                    path = profile / 'user.js'
                    preserve(path)
                    _merge_prefs(path, selected)
            (backup / 'restore.json').write_text(json.dumps({"files": [
                {"path": str(p.relative_to(profile)), "existed": existed} for p, existed in touched]}, indent=2))
            return backup
        except Exception:
            for path, existed in reversed(touched):
                if path.is_dir(): shutil.rmtree(path)
                elif path.exists(): path.unlink()
                if existed:
                    src = backup / path.relative_to(profile)
                    if src.is_dir(): shutil.copytree(src, path)
                    else:
                        path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src, path)
            raise
