"""dotctl — gestion des modules dotfiles.

  dotctl list [catégorie|--md|--json]   catalogue des modules (--md : tableau pour le README)
  dotctl status [--all]          état des modules (du profil, ou tous)
  dotctl info <id> [--json]      module ou module/sous-partie : schéma, fichiers, README
  dotctl plan <id>… [--json]     aperçu sans modification
  dotctl configure <id>          --parts a,b --set CLE=valeur --values-file fichier.json
  dotctl apply <module>…         installe / met à jour des modules
  dotctl apply --profile [nom]   applique tout le profil (machine courante par défaut)
  dotctl diff <module>           différences repo ↔ machine
  dotctl capture <module>        recopie dans le repo les fichiers modifiés localement
  dotctl sync                    git pull des dépôts Git (privé Seafile exclu)
  dotctl firefox                 sauvegarde/restauration sélectives de Firefox
  dotctl gui | tray              interface graphique / icône de notification
"""
from __future__ import annotations

import argparse
import difflib
import json
from pathlib import Path
import sys

from . import core, options

C = {"ok": "\033[32m", "update": "\033[33m", "drift": "\033[35m", "absent": "\033[90m", "end": "\033[0m"}


def _color(s: str, st: str) -> str:
    return f"{C.get(st, '')}{s}{C['end']}" if sys.stdout.isatty() else s


def cmd_list(args):
    mods = core.load_modules()
    if "--json" in args:
        print(json.dumps([core.describe(m) for m in mods.values()], ensure_ascii=False, indent=2))
        return
    if "--md" in args:
        for cat, label in core.CATEGORIES.items():
            items = sorted((m for m in mods.values() if m.category == cat and m.path and not m.parent), key=lambda m: m.id)
            if items:
                print(f"\n### {label}\n\n| Module | Ce que ça fait |\n|---|---|")
                for m in items:
                    flag = " ✋" if m.manual else ""
                    print(f"| [`{m.id}`](modules/{m.id}/) | {m.description}{flag} |")
        apps = sorted((m for m in mods.values() if not m.path), key=lambda m: (getattr(m, "group", ""), m.name.lower()))
        print(f"\n### Applications simples ({len(apps)}, `catalog/apps.toml`)\n")
        groups = {}
        for m in apps:
            groups.setdefault(getattr(m, "group", ""), []).append(m.name)
        for g, names in groups.items():
            print(f"- **{g}** : {', '.join(names)}")
        return
    cats = [args[0]] if args else list(core.CATEGORIES)
    for cat in cats:
        items = [m for m in mods.values() if m.category == cat and not m.parent]
        if not items:
            continue
        print(f"\n\033[1m{core.CATEGORIES.get(cat, cat)}\033[0m")
        for m in sorted(items, key=lambda m: m.id):
            print(f"  {m.id:28} {m.description}")


def cmd_status(args):
    mods = core.load_modules()
    prof = core.load_profile()
    env = core.context_env(prof)
    state = core.load_state()
    explicit = [arg for arg in args if not arg.startswith("--")]
    ids = explicit or ([mid for mid, m in mods.items() if not m.parent]
                       if "--all" in args or not prof["modules"] else prof["modules"])
    print(f"Profil : {prof['_name'] or '(aucun)'}  {prof['_path'] or ''}")
    for mid in ids:
        if mid not in mods:
            print(f"  {mid:28} ? module inconnu")
            continue
        st = core.status(mods[mid], env, state)
        if st == core.ABSENT and "--all" in args and mid.startswith("app-"):
            continue
        print(f"  {mid:28} {_color(core.STATUS_LABEL[st], st)}")


def cmd_info(args):
    m = core.load_modules()[args[0]]
    if "--json" in args:
        print(json.dumps(core.describe(m), ensure_ascii=False, indent=2))
        return
    print(f"\033[1m{m.name}\033[0m  [{m.id}, {core.CATEGORIES.get(m.category, m.category)}]")
    print(m.description)
    for label, pk in (("pacman", m.pacman), ("AUR", m.aur), ("flatpak", m.flatpak)):
        if pk:
            print(f"  {label:8}: {' '.join(pk)}")
    for f in m.files:
        print(f"  fichier : {f.dst}{'  (root)' if f.root else ''}{'  (template)' if f.template else ''}")
    if m.requires:
        print(f"  dépend de : {', '.join(m.requires)}")
    if m.vars or m.secrets:
        print(f"  variables : {', '.join(m.vars)}  secrets : {', '.join(m.secrets)}")
    for part in m.parts:
        print(f"  sous-partie : {part.id} — {part.name}")
    for item in options.fields(m):
        print(f"  champ : {item.key} ({item.type}) — {item.label or item.key}")
    if m.readme():
        print("\n" + m.readme())



def cmd_plan(args):
    ids = [arg for arg in args if arg != "--json"]
    if not ids:
        raise ValueError("dotctl plan <module ou module/sous-partie>… [--json]")
    plan = core.application_plan(ids)
    if "--json" in args:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return
    for m in plan["modules"]:
        print(f"{m['id']} : {m['name']}")
        for kind, names in m['packages'].items():
            if names:
                print(f"  {kind} : {', '.join(names)}")
        for f in m['files']:
            print(f"  fichier : {f['dst']}{' (système)' if f['root'] else ''}")
        for name, path in m['scripts'].items():
            if name == 'apply.sh':
                print(f"  script : {path}")
        if m['missing_inputs']:
            print("  champs à renseigner : " + ", ".join(m['missing_inputs']))


def cmd_configure(args):
    parser = argparse.ArgumentParser(prog='dotctl configure')
    parser.add_argument('id')
    parser.add_argument('--parts', help='Identifiants séparés par des virgules ; none = socle seul')
    parser.add_argument('--set', action='append', default=[], metavar='CLE=VALEUR')
    parser.add_argument('--values-file', help='JSON privé ; - pour stdin (recommandé pour les secrets)')
    parsed = parser.parse_args(args)
    module = core.load_modules()[parsed.id]
    parts = None
    if parsed.parts is not None:
        parts = [] if parsed.parts in ('', 'none') else [
            p if '/' in p else f'{module.id}/{p}' for p in parsed.parts.split(',')]
    schema = {f.key: f for m in [module, *module.parts] for f in options.fields(m)}
    values = {}
    if parsed.values_file:
        values = json.load(sys.stdin) if parsed.values_file == '-' else json.loads(Path(parsed.values_file).read_text())
        if not isinstance(values, dict):
            raise ValueError('Le fichier de valeurs doit contenir un objet JSON.')
    for setting in parsed.set:
        if '=' not in setting:
            raise ValueError('--set attend CLE=valeur')
        key, value = setting.split('=', 1)
        if key in schema and schema[key].type == 'secret':
            raise ValueError('Utilisez --values-file ou stdin pour les secrets, pas les arguments de commande.')
        values[key] = value
    if parts is None and module.parts:
        parts = options.selected(module)
    options.save(module, values, parts)
    print(f'{module.id} : choix enregistrés dans le dossier privé. Rien appliqué ; utilisez dotctl plan puis dotctl apply.')


def cmd_apply(args):
    if args and args[0] == "--profile":
        prof = core.load_profile(args[1] if len(args) > 1 else None)
        if not prof["modules"]:
            sys.exit("Aucun profil trouvé (repo privé hosts/<hostname>.toml ou profiles/).")
        print(f"Profil {prof['_name']} : {len(prof['modules'])} modules")
        sys.exit(1 if core.apply(prof["modules"], profile=prof) else 0)
    if not args:
        sys.exit("dotctl apply <module>… | --profile [nom]")
    sys.exit(1 if core.apply(args) else 0)


def cmd_diff(args):
    m = core.load_modules()[args[0]]
    env = core.context_env()
    for f in core.drifted_files(m, env):
        dst = f.dst_path(env)
        new = dst.read_text(errors="replace").splitlines() if dst.exists() else []
        old = core.render(m, f, env).decode(errors="replace").splitlines()
        sys.stdout.writelines(l + "\n" for l in difflib.unified_diff(old, new, f"repo/{f.src}", str(dst), lineterm=""))


def cmd_capture(args):
    for mid in args:
        print(f"{mid} : {core.capture(mid)} fichier(s) recopié(s)")


def cmd_firefox(args):
    from .firefox_gui import main
    main()


def cmd_sync(args):
    sys.exit(0 if core.sync() else 1)


def cmd_gui(args):
    from . import gui
    gui.main(tray=False)


def cmd_tray(args):
    from . import gui
    gui.main(tray=True)


COMMANDS = {"plan": cmd_plan, "configure": cmd_configure, "list": cmd_list, "status": cmd_status, "info": cmd_info, "apply": cmd_apply,
            "diff": cmd_diff, "capture": cmd_capture, "sync": cmd_sync, "firefox": cmd_firefox, "gui": cmd_gui, "tray": cmd_tray}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] in ("-h", "--help", "help") or argv[0] not in COMMANDS:
        print(__doc__)
        return
    try:
        COMMANDS[argv[0]](argv[1:])
    except KeyError as e:
        sys.exit(f"Module inconnu : {e}")
    except (ValueError, OSError) as e:
        sys.exit(str(e))
