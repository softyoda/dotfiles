"""Schéma des champs et préférences d'installation privées par machine."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import fcntl
import json
import os
from pathlib import Path
import re
import socket
import tempfile


@dataclass
class Input:
    key: str
    label: str = ''
    type: str = 'text'  # text | path | bool | choice | integer | secret
    help: str = ''
    required: bool = False
    default: object = None
    choices: list[str] = field(default_factory=list)
    path_kind: str = 'directory'
    must_exist: bool = False
    pattern: str = ''

    def __post_init__(self):
        if not re.fullmatch(r'[A-Z][A-Z0-9_]*', self.key):
            raise ValueError(f'Clé de champ invalide : {self.key}')
        if self.type not in ('text', 'path', 'bool', 'choice', 'integer', 'secret'):
            raise ValueError(f'Type de champ invalide : {self.type}')
        if self.type == 'secret' and self.default is not None:
            raise ValueError(f'{self.key} : aucun secret par défaut dans un manifeste public')
        if self.key in ('HOME', 'PATH', 'USER', 'UID', 'DOTFILES', 'MODULE_DIR', 'DOTFILES_LIB'):
            raise ValueError(f'{self.key} : variable réservée')
        if self.type == 'choice' and not self.choices:
            raise ValueError(f'{self.key} : choix manquants')

    def normalize(self, value):
        if value is None or value == '':
            if self.required:
                raise ValueError(f'{self.label or self.key} : valeur obligatoire')
            return ''
        if self.type == 'bool':
            if isinstance(value, bool):
                return value
            if str(value).lower() not in ('true', 'false'):
                raise ValueError(f'{self.key} : attendu true ou false')
            return str(value).lower() == 'true'
        if self.type == 'integer':
            if isinstance(value, bool) or not re.fullmatch(r'-?\d+', str(value)):
                raise ValueError(f'{self.key} : entier attendu')
            return int(value)
        if not isinstance(value, str):
            raise ValueError(f'{self.key} : texte attendu')
        if '\x00' in value or '\n' in value or '\r' in value:
            raise ValueError(f'{self.key} : une seule ligne attendue')
        if self.type == 'choice' and value not in self.choices:
            raise ValueError(f'{self.key} : choisissez une valeur proposée')
        if self.pattern and not re.fullmatch(self.pattern, value):
            raise ValueError(f'{self.key} : format non valide')
        if self.type == 'path' and self.must_exist:
            p = Path(value).expanduser()
            valid = p.is_file() if self.path_kind == 'file' else p.is_dir()
            if not valid:
                raise ValueError(f'{self.key} : chemin introuvable ou de type incorrect')
        return value

    def schema(self):
        # Un secret ne doit pas avoir de valeur par défaut publiable.
        data = asdict(self)
        if self.type == 'secret':
            data['default'] = None
        return data


def path() -> Path | None:
    from . import core
    private = core.private_dir()
    if private is None:
        return None
    return private / 'settings' / f'{socket.gethostname()}.json'


def load() -> dict:
    p = path()
    if p is None or not p.exists():
        return {'version': 1, 'vars': {}, 'secrets': {}, 'parts': {}}
    data = json.loads(p.read_text())
    if data.get('version') != 1:
        raise ValueError('Format de réglages privés non pris en charge')
    for key in ('vars', 'secrets', 'parts'):
        if not isinstance(data.get(key, {}), dict):
            raise ValueError(f'Réglages privés : section {key} invalide')
        data.setdefault(key, {})
    return data


def selected(module) -> list[str]:
    saved = load()['parts'].get(module.id)
    if saved is None:
        return [p.id for p in module.parts if p.default]
    available = {p.id for p in module.parts}
    unknown = set(saved) - available
    if unknown:
        raise ValueError(f'{module.id} : sous-parties inconnues dans les réglages : {", ".join(sorted(unknown))}')
    return list(saved)


def fields(module) -> list[Input]:
    result = {item.key: item for item in module.inputs}
    for key in module.vars:
        result.setdefault(key, Input(key, required=True))
    for key in module.secrets:
        result[key] = Input(key, result[key].label if key in result else key, type='secret', required=True,
                            help=result[key].help if key in result else '')
    return list(result.values())


def env_value(value) -> str:
    if isinstance(value, bool):
        return 'true' if value else 'false'
    text = str(value)
    return os.path.expanduser(text) if text.startswith('~/') else text


def environment() -> dict[str, str]:
    data = load()
    return {key: env_value(value) for group in ('vars', 'secrets') for key, value in data[group].items()}


def save(module, values: dict, parts: list[str] | None = None):
    from . import core
    p = path()
    if p is None:
        raise ValueError('Choisissez d’abord le dossier privé synchronisé par Seafile.')
    if p.resolve().is_relative_to(core.DOTFILES.resolve()):
        raise ValueError('Les réglages doivent rester hors du dépôt public.')
    modules = [module]
    if parts is not None:
        available = {part.id: part for part in module.parts}
        if set(parts) - available.keys():
            raise ValueError('Sous-partie inconnue pour ce module')
        modules += [available[mid] for mid in parts]
    all_fields = {f.key: f for m in modules for f in fields(m)}
    if set(values) - all_fields.keys():
        raise ValueError('Champ inconnu : ' + ', '.join(sorted(set(values) - all_fields.keys())))
    normalized = {key: all_fields[key].normalize(value) for key, value in values.items()}
    p.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    lock_path = Path.home() / '.cache/dotfiles/options.lock'
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        data = load()
        if parts is not None:
            data['parts'][module.id] = list(parts)
        for key, value in normalized.items():
            section = 'secrets' if all_fields[key].type == 'secret' else 'vars'
            data[section][key] = value
        fd, temporary = tempfile.mkstemp(prefix='.settings-', dir=p.parent)
        try:
            with os.fdopen(fd, 'w') as output:
                json.dump(data, output, indent=2, ensure_ascii=False)
                output.write('\n')
                output.flush()
                os.fsync(output.fileno())
            os.replace(temporary, p)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)


def set_private_directory(value: str):
    from . import core
    directory = Path(value).expanduser().resolve()
    if not directory.is_dir():
        raise ValueError('Dossier introuvable')
    if directory.is_relative_to(core.DOTFILES.resolve()):
        raise ValueError('Le dossier privé doit être hors du dépôt public.')
    core.PRIVATE_PATH_FILE.parent.mkdir(parents=True, exist_ok=True)
    core.PRIVATE_PATH_FILE.write_text(str(directory) + '\n')
