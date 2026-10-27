"""dotctl — gestion des modules dotfiles.

  dotctl list [catégorie|--md]   catalogue des modules (--md : tableau pour le README)
  dotctl status [--all]          état des modules (du profil, ou tous)
  dotctl info <module>           description, paquets, fichiers, notes
  dotctl apply <module>…         installe / met à jour des modules
  dotctl apply --profile [nom]   applique tout le profil (machine courante par défaut)
  dotctl diff <module>           différences repo ↔ machine
  dotctl capture <module>        recopie dans le repo les fichiers modifiés localement
  dotctl sync                    git pull du repo public (+ privé)
  dotctl gui | tray              interface graphique / icône de notification
"""
from __future__ import annotations

import difflib
import sys

from . import core

C = {"ok": "\033[32m", "update": "\033[33m", "drift": "\033[35m", "absent": "\033[90m", "end": "\033[0m"}


def _color(s: str, st: str) -> str:
    return f"{C.get(st, '')}{s}{C['end']}" if sys.stdout.isatty() else s


def cmd_list(args):
    mods = core.load_modules()
    if "--md" in args:
        for cat, label in core.CATEGORIES.items():
            items = sorted((m for m in mods.values() if m.category == cat and m.path), key=lambda m: m.id)
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
        items = [m for m in mods.values() if m.category == cat]
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
    ids = list(mods) if "--all" in args or not prof["modules"] else prof["modules"]
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
    if m.readme():
        print("\n" + m.readme())


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


def cmd_sync(args):
    sys.exit(0 if core.sync() else 1)


def cmd_gui(args):
    from . import gui
    gui.main(tray=False)


def cmd_tray(args):
    from . import gui
    gui.main(tray=True)


COMMANDS = {"list": cmd_list, "status": cmd_status, "info": cmd_info, "apply": cmd_apply,
            "diff": cmd_diff, "capture": cmd_capture, "sync": cmd_sync, "gui": cmd_gui, "tray": cmd_tray}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] in ("-h", "--help", "help") or argv[0] not in COMMANDS:
        print(__doc__)
        return
    try:
        COMMANDS[argv[0]](argv[1:])
    except KeyError as e:
        sys.exit(f"Module inconnu : {e}")
