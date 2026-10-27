"""Cœur de dotctl : chargement des modules, statut, application, capture.

Un module = un dossier modules/<id>/ contenant :
  module.toml   description, paquets, fichiers à déployer, variables attendues
  apply.sh      (optionnel) étapes post-déploiement (services, dconf, …)
  check.sh      (optionnel) test supplémentaire « appliqué ? » (exit 0 = oui)
  files/        fichiers déployés par la section [[files]]
  README.md     (optionnel) notes / aide-mémoire

Les applis « simples » (juste un paquet) sont dans catalog/apps.toml et
deviennent des pseudo-modules `app-<id>`.
"""
from __future__ import annotations

import hashlib
import json
import re
import os
import shlex
import shutil
import socket
import sqlite3
import subprocess
import time
import tomllib
from dataclasses import dataclass, field, asdict
from pathlib import Path
from string import Template

from . import options

DOTFILES = Path(__file__).resolve().parent.parent
MODULES_DIR = DOTFILES / "modules"
CATALOG = DOTFILES / "catalog" / "apps.toml"
STATE_FILE = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state")) / "dotfiles" / "applied.json"
SECRETS_FILE = Path.home() / ".config" / "dotfiles" / "secrets.env"

CATEGORIES = {
    "base": "Système de base",
    "kde": "KDE Plasma",
    "hardware": "Matériel",
    "apps": "Applications",
    "ai": "IA & agents",
    "creative": "Création",
    "retro": "Rétro & salon",
    "homelab": "NAS & homelab",
}

# Statuts
ABSENT, OK, UPDATE, DRIFT = "absent", "ok", "update", "drift"
STATUS_LABEL = {ABSENT: "non installé", OK: "à jour", UPDATE: "mise à jour dispo", DRIFT: "modifié localement"}


PRIVATE_PATH_FILE = Path.home() / ".config" / "dotfiles" / "private-path"


def private_dir() -> Path | None:
    """Dossier privé (bibliothèque Seafile chiffrée « dotfiles-private »).

    Ordre : $DOTFILES_PRIVATE, chemin noté dans ~/.config/dotfiles/private-path,
    puis recherche des emplacements Seafile habituels.
    """
    cands = [os.environ.get("DOTFILES_PRIVATE")]
    if PRIVATE_PATH_FILE.is_file():
        cands.append(os.path.expanduser(PRIVATE_PATH_FILE.read_text().strip()))
    home = Path.home()
    cands += [home / "Seafile" / "dotfiles-private", *home.glob("seafile*/Seafile/dotfiles-private"),
              home / ".config" / "dotfiles-private", DOTFILES.parent / "dotfiles-private"]
    for p in cands:
        if p and Path(p).is_dir():
            return Path(p)
    return None



def private_sync_label() -> str:
    private = private_dir()
    if private is None:
        return "Données privées : dossier introuvable."
    if is_git_root(private):
        return "Données privées : dépôt Git (synchronisé par le bouton Synchroniser)."
    home = Path.home()
    for ini in (home / ".ccnet/seafile.ini",
                home / ".var/app/com.seafile.Client/.ccnet/seafile.ini"):
        try:
            db = Path(ini.read_text().strip()) / "repo.db"
            with sqlite3.connect(db.as_uri() + "?mode=ro", uri=True) as conn:
                trees = conn.execute("SELECT value FROM RepoProperty WHERE key = 'worktree'").fetchall()
            if any(private.resolve().is_relative_to(Path(value).resolve()) for (value,) in trees):
                return "Données privées : dossier suivi par Seafile ; vérifier le transfert dans le client Seafile."
        except (OSError, ValueError, sqlite3.Error):
            continue
    return "Données privées : dossier local — synchronisation distante à configurer dans Seafile."


def read_env_file(path: Path) -> dict[str, str]:
    env = {}
    if path.is_file():
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            v = v.split(" #", 1)[0]  # commentaire en fin de ligne (ex. « # expire: 2027-01-31 »)
            env[k.strip().removeprefix("export ").strip()] = v.strip().strip('"').strip("'")
    return env


def secret_files() -> list[Path]:
    """secrets.env du dossier privé (partagé entre machines) puis surcharge locale."""
    priv = private_dir()
    return ([priv / "secrets.env"] if priv else []) + [SECRETS_FILE]


def expiring_secrets(days: int = 21) -> list[tuple[str, str, int]]:
    """Secrets annotés « # expire: AAAA-MM-JJ » qui expirent dans moins de `days` jours."""
    import datetime as dt
    out = []
    today = dt.date.today()
    for f in secret_files():
        if not f.is_file():
            continue
        for line in f.read_text().splitlines():
            m = re.search(r"^\s*(?:export\s+)?(\w+)=.*#\s*expire:\s*(\d{4}-\d{2}-\d{2})", line)
            if m:
                left = (dt.date.fromisoformat(m.group(2)) - today).days
                if left <= days:
                    out.append((m.group(1), m.group(2), left))
    return out


# ─── Profils ────────────────────────────────────────────────────────────────

def profile_candidates() -> list[Path]:
    out = []
    priv = private_dir()
    if priv:
        out += sorted((priv / "hosts").glob("*.toml"))
    out += sorted((DOTFILES / "profiles").glob("*.toml"))
    return out


def load_profile(name: str | None = None) -> dict:
    """Profil `name`, sinon celui du hostname, sinon `default`."""
    wanted = [name] if name else [socket.gethostname(), "default"]
    for w in wanted:
        for p in profile_candidates():
            if p.stem == w:
                data = tomllib.loads(p.read_text())
                data.setdefault("modules", [])
                data.setdefault("vars", {})
                data["_path"] = str(p)
                data["_name"] = p.stem
                return data
    return {"modules": [], "vars": {}, "_name": None, "_path": None}


def context_env(profile: dict | None = None) -> dict[str, str]:
    """Variables visibles par les modules : profil (non secret) + secrets locaux."""
    profile = profile or load_profile()
    # « ~/… » développé : les scripts et fichiers générés reçoivent des chemins absolus
    env = {k: (os.path.expanduser(str(v)) if str(v).startswith("~/") else str(v))
           for k, v in profile.get("vars", {}).items()}
    for f in secret_files():
        env.update(read_env_file(f))
    env.update(options.environment())
    env.setdefault("USER", os.environ.get("USER", ""))
    env.setdefault("HOME", str(Path.home()))
    env.setdefault("UID", str(os.getuid()))
    return env


# ─── Modules ────────────────────────────────────────────────────────────────

@dataclass
class FileSpec:
    src: str
    dst: str
    root: bool = False
    mode: str | None = None
    template: bool = False

    def dst_path(self, env: dict) -> Path:
        return Path(os.path.expanduser(Template(self.dst).safe_substitute(env)))


@dataclass
class Module:
    id: str
    name: str
    category: str
    description: str = ""
    path: Path | None = None
    pacman: list[str] = field(default_factory=list)
    aur: list[str] = field(default_factory=list)
    flatpak: list[str] = field(default_factory=list)
    files: list[FileSpec] = field(default_factory=list)
    requires: list[str] = field(default_factory=list)
    vars: list[str] = field(default_factory=list)
    secrets: list[str] = field(default_factory=list)
    notes: str = ""
    manual: bool = False  # étapes manuelles restantes (affichées, pas automatisables)

    parent: str | None = None
    default: bool = True
    parts: list[Module] = field(default_factory=list)
    inputs: list[options.Input] = field(default_factory=list)
    apply_script: str | None = None
    check_script: str | None = None

    @property
    def packages(self) -> list[str]:
        return self.pacman + self.aur + self.flatpak

    def script(self, name: str) -> Path | None:
        override = self.apply_script if name == "apply.sh" else self.check_script
        if self.parent and override is None:
            return None
        relative = override or name
        if self.path and (self.path / relative).is_file():
            return self.path / relative
        return None

    def readme(self) -> str:
        if self.path and (self.path / "README.md").is_file():
            return (self.path / "README.md").read_text()
        return self.notes

    def content_hash(self) -> str:
        h = hashlib.sha256()
        if self.path and (self.parent or self.parts):
            spec = {key: getattr(self, key) for key in
                    ("id", "name", "description", "requires", "vars", "secrets", "pacman", "aur", "flatpak",
                     "apply_script", "check_script")}
            spec["inputs"] = [f.schema() for f in self.inputs]
            spec["files"] = [asdict(f) for f in self.files]
            h.update(json.dumps(spec, sort_keys=True).encode())
            paths = [self.path / f.src for f in self.files]
            paths += [p for name in ("apply.sh", "check.sh") if (p := self.script(name))]
            for f in sorted(set(paths)):
                h.update(str(f.relative_to(self.path)).encode())
                h.update(f.read_bytes())
        elif self.path:
            for f in sorted(self.path.rglob("*")):
                if f.is_file():
                    h.update(str(f.relative_to(self.path)).encode())
                    h.update(f.read_bytes())
        else:
            h.update(json.dumps([self.pacman, self.aur, self.flatpak]).encode())
        return h.hexdigest()[:16]


def _module_from_toml(mid: str, data: dict, path: Path | None) -> Module:
    pk = data.get("packages", {})
    return Module(
        id=mid,
        name=data.get("name", mid),
        category=data.get("category", "apps"),
        description=data.get("description", ""),
        path=path,
        pacman=pk.get("pacman", []),
        aur=pk.get("aur", []),
        flatpak=pk.get("flatpak", []),
        files=[FileSpec(**f) for f in data.get("files", [])],
        requires=data.get("requires", []),
        vars=data.get("vars", []),
        secrets=data.get("secrets", []),
        notes=data.get("notes", ""),
        manual=data.get("manual", False),
        parent=data.get("parent"),
        default=data.get("default", True),
        inputs=[options.Input(**item) for item in data.get("inputs", [])],
        apply_script=data.get("apply"),
        check_script=data.get("check"),
    )


def load_modules() -> dict[str, Module]:
    mods: dict[str, Module] = {}
    for toml in sorted(MODULES_DIR.glob("*/module.toml")):
        mid = toml.parent.name
        data = tomllib.loads(toml.read_text())
        mods[mid] = _module_from_toml(mid, data, toml.parent)
        for part in data.get("parts", []):
            pid = part["id"]
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", pid):
                raise ValueError(f"Identifiant de sous-partie invalide : {mid}/{pid}")
            full_id = f"{mid}/{pid}"
            if full_id in mods:
                raise ValueError(f"Sous-partie dupliquée : {full_id}")
            child = _module_from_toml(full_id, {**part, "parent": mid,
                          "category": data.get("category", "apps")}, toml.parent)
            for field in child.files:
                if Path(field.src).is_absolute() or ".." in Path(field.src).parts:
                    raise ValueError(f"Source invalide : {full_id}")
            for script in (child.apply_script, child.check_script):
                if script and (Path(script).is_absolute() or ".." in Path(script).parts
                               or not (toml.parent / script).is_file()):
                    raise ValueError(f"Script invalide : {full_id}")
            mods[mid].parts.append(child)
            mods[full_id] = child
    if CATALOG.is_file():
        cat = tomllib.loads(CATALOG.read_text())
        for group, apps in cat.items():
            for a in apps:
                mid = f"app-{a['id']}"
                method = a["method"]
                mods[mid] = Module(
                    id=mid, name=a["label"], category="apps", description=a.get("desc", ""),
                    pacman=[a["pkg"]] if method == "pacman" else [],
                    aur=[a["pkg"]] if method == "aur" else [],
                    flatpak=[a["pkg"]] if method == "flatpak" else [],
                    notes=f"Groupe : {group}",
                )
                mods[mid].group = group  # type: ignore[attr-defined]
    return mods


def resolve(ids: list[str], mods: dict[str, Module], selections: dict | None = None) -> list[Module]:
    """Une sous-partie ajoute le socle parent, jamais ses parties sœurs."""
    out, seen, visiting, expanded = [], set(), set(), set()

    def visit(mid: str, expand=True):
        if mid not in mods:
            raise KeyError(mid)
        if mid in visiting:
            raise ValueError(f"Dépendance circulaire : {mid}")
        m = mods[mid]
        if mid not in seen:
            visiting.add(mid)
            if m.parent:
                visit(m.parent, expand=False)
            for dependency in m.requires:
                visit(dependency)
            visiting.remove(mid)
            seen.add(mid)
            out.append(m)
        if expand and m.parts and mid not in expanded:
            expanded.add(mid)
            chosen = selections[mid] if selections is not None and mid in selections else options.selected(m)
            available = {p.id for p in m.parts}
            if set(chosen) - available:
                raise ValueError(f"Sous-partie inconnue pour {mid}")
            for child in chosen:
                visit(child)

    for mid in ids:
        visit(mid)
    return out


def module_env(m: Module, env: dict) -> dict:
    result = dict(env)
    sources = [m]
    if m.parent:
        sources.insert(0, load_modules()[m.parent])
    for source in sources:
        for item in options.fields(source):
            if item.key not in env and item.default is not None:
                result[item.key] = options.env_value(item.default)
    return result


def configuration_hash(m: Module, env: dict) -> str:
    env = module_env(m, env)
    data = {f.key: env.get(f.key, "") for f in options.fields(m)}
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:16]


def describe(m: Module) -> dict:
    return {"id": m.id, "parent": m.parent, "name": m.name, "description": m.description,
            "category": m.category, "manual": m.manual,
            "requires": ([m.parent] if m.parent else []) + m.requires,
            "parts": [{"id": p.id, "name": p.name, "default": p.default} for p in m.parts],
            "inputs": [f.schema() for f in options.fields(m)],
            "packages": {"pacman": m.pacman, "aur": m.aur, "flatpak": m.flatpak},
            "files": [asdict(f) for f in m.files],
            "scripts": {name: str(p.relative_to(DOTFILES)) for name in ("apply.sh", "check.sh")
                        if (p := m.script(name))},
            "readme": str(m.path.relative_to(DOTFILES) / "README.md") if m.path else None}


def application_plan(ids: list[str], selections=None, values=None) -> dict:
    env = context_env()
    env.update({key: options.env_value(value) for key, value in (values or {}).items()})
    modules = resolve(ids, load_modules(), selections)
    return {"requested": ids, "modules": [dict(describe(m), missing_inputs=missing_vars(m, module_env(m, env)))
                                         for m in modules]}


# ─── État installé ──────────────────────────────────────────────────────────

_installed_cache: dict[str, set[str]] = {}


def _installed(kind: str) -> set[str]:
    if kind not in _installed_cache:
        try:
            if kind == "pacman":
                out = subprocess.run(["pacman", "-Qq"], capture_output=True, text=True).stdout
            else:
                out = subprocess.run(["flatpak", "list", "--columns=application"],
                                     capture_output=True, text=True).stdout if shutil.which("flatpak") else ""
        except FileNotFoundError:
            out = ""
        _installed_cache[kind] = set(out.split())
    return _installed_cache[kind]


def invalidate_cache():
    _installed_cache.clear()


def missing_packages(m: Module) -> list[str]:
    pac = _installed("pacman")
    fp = _installed("flatpak")
    miss = [p for p in m.pacman + m.aur if p not in pac]
    if miss:  # paquet fourni par une variante (ex. vesktop-bin fournit vesktop)
        r = subprocess.run(["pacman", "-T", *miss], capture_output=True, text=True)
        miss = r.stdout.split()
    miss += [p for p in m.flatpak if p not in fp]
    return miss


def render(m: Module, f: FileSpec, env: dict) -> bytes:
    env = module_env(m, env)
    data = (m.path / f.src).read_bytes()
    if f.template:
        data = Template(data.decode()).safe_substitute(env).encode()
    return data


def drifted_files(m: Module, env: dict) -> list[FileSpec]:
    out = []
    for f in m.files:
        dst = f.dst_path(env)
        try:
            if not dst.exists() or dst.read_bytes() != render(m, f, env):
                out.append(f)
        except PermissionError:
            pass  # fichier root illisible : on ne peut pas juger
    return out


def load_state() -> dict:
    try:
        return json.loads(STATE_FILE.read_text())
    except Exception:
        return {}


def save_state(state: dict):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, sort_keys=True))


def status(m: Module, env: dict, state: dict | None = None, _aggregate=True) -> str:
    env = module_env(m, env)
    state = load_state() if state is None else state
    applied = state.get(m.id)
    if missing_packages(m) or missing_vars(m, env):
        return ABSENT
    if m.parent and _aggregate:
        parent_status = status(load_modules()[m.parent], env, state, _aggregate=False)
        if parent_status != OK:
            return parent_status
    chk = m.script("check.sh")
    if chk and subprocess.run(["bash", str(chk)], env={**os.environ, **env, **_script_env(m)},
                              capture_output=True).returncode != 0:
        return ABSENT
    drift = drifted_files(m, env)
    if drift and not applied:
        return ABSENT if all(not f.dst_path(env).exists() for f in drift) else DRIFT
    if applied and applied.get("hash") != m.content_hash():
        return UPDATE
    if drift:
        return DRIFT
    if applied and "config_hash" in applied and applied["config_hash"] != configuration_hash(m, env):
        return UPDATE
    if m.parts and _aggregate:
        selected = set(options.selected(m))
        statuses = [status(part, env, state) for part in m.parts if part.id in selected]
        for candidate in (DRIFT, ABSENT, UPDATE):
            if candidate in statuses:
                return candidate
    if m.requires and _aggregate:
        mods = load_modules()
        # La résolution vérifie les cycles avant l'inspection des dépendances.
        for dependency in resolve(m.requires, mods):
            result = status(dependency, env, state, _aggregate=False)
            if result != OK:
                return result
    return OK


# ─── Application ────────────────────────────────────────────────────────────

def _script_env(m: Module) -> dict:
    return {"DOTFILES": str(DOTFILES), "MODULE_DIR": str(m.path or ""),
            "DOTFILES_LIB": str(DOTFILES / "lib" / "lib.sh")}


def sudo_cmd() -> list[str]:
    if os.geteuid() == 0:
        return []
    if not os.isatty(0) and os.environ.get("SUDO_ASKPASS"):
        return ["sudo", "-A"]
    return ["sudo"]


def missing_vars(m: Module, env: dict) -> list[str]:
    env = module_env(m, env)
    missing = []
    for item in options.fields(m):
        try:
            item.normalize(env.get(item.key, ""))
        except ValueError:
            missing.append(item.key)
    return missing


def plan_commands(mods: list[Module], env: dict) -> list[tuple[str, list[str] | str]]:
    """Liste (titre, commande) ; une commande str est exécutée via bash."""
    steps: list[tuple[str, list[str] | str]] = []
    pac = sorted({p for m in mods for p in m.pacman if p not in _installed("pacman")})
    aur = sorted({p for m in mods for p in m.aur if p not in _installed("pacman")})
    fp = sorted({p for m in mods for p in m.flatpak if p not in _installed("flatpak")})
    if pac:
        steps.append((f"pacman : {' '.join(pac)}", sudo_cmd() + ["pacman", "-S", "--needed", "--noconfirm", *pac]))
    if aur:
        if not shutil.which("paru"):  # machine neuve : paru est dans les dépôts CachyOS, sinon compilé depuis l'AUR
            steps.append(("installation de paru", " ".join(sudo_cmd()) + " pacman -S --needed --noconfirm paru || "
                          "(rm -rf /tmp/paru-bin && git clone https://aur.archlinux.org/paru-bin.git /tmp/paru-bin && "
                          "cd /tmp/paru-bin && makepkg -si --noconfirm)"))
        steps.append((f"AUR : {' '.join(aur)}", ["paru", "-S", "--needed", "--noconfirm", "--skipreview", *aur]))
    if fp:
        steps.append((f"Flatpak : {' '.join(fp)}",
                      sudo_cmd() + ["flatpak", "install", "--system", "-y", "--noninteractive", "flathub", *fp]))
    return steps


def deploy_files(m: Module, env: dict, log) -> bool:
    ok = True
    for f in m.files:
        dst = f.dst_path(env)
        data = render(m, f, env)
        try:
            if dst.exists() and dst.read_bytes() == data:
                continue
        except PermissionError:
            pass
        mode = f.mode or ("644" if f.root else None)
        if f.root:
            r = subprocess.run(sudo_cmd() + ["install", "-D", "-m", mode, "/dev/stdin", str(dst)],
                               input=data, capture_output=True)
            if r.returncode:
                log(f"  ✗ {dst} : {r.stderr.decode().strip()}")
                ok = False
                continue
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            if dst.is_symlink():
                dst.unlink()
            elif dst.exists():
                shutil.copy2(dst, dst.with_name(dst.name + f".bak-{time.strftime('%Y%m%d')}"))
            dst.write_bytes(data)
            if mode:
                dst.chmod(int(mode, 8))
        log(f"  → {dst}")
    return ok


def run_stream(cmd, log, env=None) -> int:
    if isinstance(cmd, str):
        cmd = ["bash", "-c", cmd]
    if not shutil.which(cmd[0]):
        log(f"✗ commande introuvable : {cmd[0]}")
        return 127
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                            env={**os.environ, **(env or {})})
    try:
        for line in proc.stdout:
            log(line.rstrip())
        return proc.wait()
    finally:
        proc.stdout.close()


def apply(ids: list[str], log=print, profile: dict | None = None) -> int:
    """Applique les modules (avec dépendances). Retourne le nombre d'échecs."""
    mods_all = load_modules()
    mods = resolve(ids, mods_all)
    env = context_env(profile)
    failures = 0

    blocked = {m.id: missing_vars(m, env) for m in mods if missing_vars(m, env)}
    for mid, vs in blocked.items():
        log(f"⚠ {mid} ignoré : variables manquantes {', '.join(vs)} "
            f"(profil privé ou {SECRETS_FILE})")
    # Propager les échecs de configuration avant toute installation.
    for m in mods:
        if m.id not in blocked and any(dep in blocked for dep in ([m.parent] if m.parent else []) + m.requires):
            blocked[m.id] = ["dépendance non configurée"]
            log(f"⚠ {m.id} ignoré : dépendance non configurée")
    mods = [m for m in mods if m.id not in blocked]
    failures += len(blocked)

    for title, cmd in plan_commands(mods, env):
        log(f"\n▶ {title}")
        if run_stream(cmd, log):
            log("✗ échec de l'installation des paquets")
            failures += 1
    invalidate_cache()

    state = load_state()
    failed = set(blocked)
    for m in mods:
        log(f"\n━━ {m.name} ({m.id}) ━━")
        if missing_packages(m):
            log(f"✗ paquets manquants : {' '.join(missing_packages(m))}")
            failures += 1
            failed.add(m.id)
            continue
        current_env = module_env(m, env)
        if any(dependency in failed for dependency in ([m.parent] if m.parent else []) + m.requires):
            log("✗ dépendance non appliquée")
            failures += 1
            failed.add(m.id)
            continue
        ok = deploy_files(m, current_env, log)
        script = m.script("apply.sh")
        if ok and script:
            ok = run_stream(["bash", str(script)], log, env={**current_env, **_script_env(m)}) == 0
        if ok:
            state[m.id] = {"hash": m.content_hash(), "config_hash": configuration_hash(m, current_env),
                           "requested": m.id in ids or state.get(m.id, {}).get("requested", m.id in state and not m.parent),
                           "date": time.strftime("%Y-%m-%d %H:%M")}
            save_state(state)
            log("✓ appliqué")
            if m.manual:
                log("ℹ étapes manuelles : voir `dotctl info " + m.id + "`")
        else:
            log("✗ échec")
            failures += 1
            failed.add(m.id)
    return failures


def capture(mid: str, log=print) -> int:
    """Recopie dans le repo les fichiers modifiés sur la machine (hors templates)."""
    m = load_modules()[mid]
    env = context_env()
    n = 0
    for f in drifted_files(m, env):
        if f.template:
            log(f"  ⚠ {f.dst} est un template : à reporter à la main")
            continue
        dst = f.dst_path(env)
        if dst.exists():
            shutil.copy2(dst, m.path / f.src)
            log(f"  ← {dst}")
            n += 1
    return n


# ─── Git ────────────────────────────────────────────────────────────────────

def git(repo: Path, *args) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


def is_git_root(path: Path) -> bool:
    # Ne pas traiter un simple dossier (même dans un dépôt parent) comme un dépôt.
    result = git(path, "rev-parse", "--show-toplevel")
    return result.returncode == 0 and Path(result.stdout.strip()).resolve() == path.resolve()


def repos() -> list[Path]:
    private = private_dir()
    return [DOTFILES] + ([private] if private and private.resolve() != DOTFILES.resolve()
                        and is_git_root(private) else [])


def behind_count(repo: Path, fetch: bool = True) -> int:
    if fetch:
        git(repo, "fetch", "--quiet")
    r = git(repo, "rev-list", "--count", "HEAD..@{u}")
    return int(r.stdout.strip() or 0) if r.returncode == 0 else 0


def sync(log=print) -> bool:
    ok = True
    for repo in repos():
        r = git(repo, "pull", "--ff-only")
        log(f"{repo.name} : {(r.stdout or r.stderr).strip()}")
        ok &= r.returncode == 0
    private = private_dir()
    if private and not is_git_root(private):
        log(private_sync_label())
        log(f"{private.name} : dossier privé non Git ({private}). "
            "Pas de git pull ; sa synchronisation doit être assurée par Seafile "
            "ou votre outil de sauvegarde. dotctl ne vérifie pas son transfert distant.")
    elif private is None:
        log("Dossier privé introuvable : seules les configurations publiques ont été synchronisées.")
    return ok


def shell_quote_env(env: dict) -> str:
    return " ".join(f"{k}={shlex.quote(v)}" for k, v in env.items())
