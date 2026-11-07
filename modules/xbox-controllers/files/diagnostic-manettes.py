#!/usr/bin/python3
"""Local controller diagnostics; never records button/keyboard input."""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import selectors
import subprocess
import tarfile
import tempfile
import time

HOME = Path.home()
STATE = HOME / '.local/state/diagnostic-manettes'
REPORTS = HOME / 'Documents/Diagnostic-manettes'
MATCH = re.compile(r'xone|xpad|\bgip\d*\b|\busb\b|xhci|bluetooth|Microsoft Xbox|gamepad|controller', re.I)
SERVICE = 'diagnostic-manettes.service'

def stamp():
    return dt.datetime.now().astimezone().isoformat(timespec='seconds')

def read(path):
    try:
        return Path(path).read_text(errors='replace').strip()
    except OSError:
        return None

def run(args):
    try:
        p = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
        return p.stdout
    except (OSError, subprocess.TimeoutExpired) as e:
        return str(e)

def prune():
    files = sorted(STATE.glob('events-*.jsonl'), key=lambda p: p.stat().st_mtime)
    total = sum(p.stat().st_size for p in files)
    for p in files:
        s = p.stat()
        if s.st_mtime < time.time() - 30*86400 or total > 256*1024*1024:
            p.unlink()
            total -= s.st_size

def record(kind, data):
    STATE.mkdir(parents=True, exist_ok=True, mode=0o700)
    prefix = 'events-' + dt.date.today().isoformat()
    existing = sorted(STATE.glob(prefix + '-*.jsonl'))
    path = existing[-1] if existing else STATE / (prefix + '-0000.jsonl')
    if path.exists() and path.stat().st_size >= 8*1024*1024:
        number = int(path.stem.rsplit('-', 1)[1]) + 1
        path = STATE / (prefix + f'-{number:04d}.jsonl')
    with path.open('a') as f:
        f.write(json.dumps({'time': stamp(), 'kind': kind, 'data': data}, ensure_ascii=False) + '\n')

def snapshot():
    inputs = read('/proc/bus/input/devices') or ''
    inputs = [b for b in inputs.split('\n\n') if re.search('xbox|gamepad|joystick|x-box', b, re.I)]
    usb = {}
    for p in Path('/sys/bus/usb/devices').glob('*'):
        if read(p/'idVendor') == '045e':
            usb[p.name] = {k: read(p/k) for k in ('idProduct', 'product', 'power/control', 'power/autosuspend', 'power/runtime_status')}
    clients = {str(p): read(p) for p in Path('/sys/bus/usb/drivers/xone-dongle').glob('*/active_clients')}
    batteries = {}
    for p in Path('/sys/class/power_supply').glob('*'):
        if re.search('xone|gip|xbox', str(p.resolve()), re.I):
            batteries[p.name] = {k: read(p/k) for k in ('capacity', 'capacity_level', 'status')}
    pairing = {str(p): read(p) for p in Path('/sys/bus/usb/drivers/xone-dongle').glob('*/pairing')}
    driver = {key: read(Path('/sys/module/xone_dongle')/key) for key in ('version', 'srcversion')}
    gip = sorted(p.name for p in Path('/sys/bus/xone-gip/devices').glob('*'))
    return {'controllers': inputs, 'usb': usb, 'active_clients': clients, 'pairing': pairing, 'batteries': batteries, 'driver': driver, 'gip_devices': gip}

def collect():
    record('start', {'boot_id': read('/proc/sys/kernel/random/boot_id'), 'kernel': run(['uname', '-r']).strip()})
    # --since replays a short window on service restart, without losing intervening events.
    proc = subprocess.Popen(['journalctl', '_TRANSPORT=kernel', '--since', '-5min', '-f', '-o', 'short-iso-precise', '--no-pager'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    os.set_blocking(proc.stdout.fileno(), False)
    selector = selectors.DefaultSelector()
    selector.register(proc.stdout, selectors.EVENT_READ)
    pending = b''
    previous = None
    next_snapshot = next_prune = next_heartbeat = 0
    try:
        while True:
            for key, _ in selector.select(timeout=1):
                chunk = os.read(key.fd, 65536)
                if not chunk:
                    raise RuntimeError('Journal inaccessible ou interrompu : le service doit redémarrer.')
                pending += chunk
                while b'\n' in pending:
                    line, pending = pending.split(b'\n', 1)
                    line = line.decode(errors='replace')
                    if MATCH.search(line) or 'permission' in line.lower():
                        record('kernel', line)
            now = time.monotonic()
            if now >= next_snapshot:
                current = snapshot()
                if current != previous:
                    record('devices', current)
                    previous = current
                next_snapshot = now + 2
            if now >= next_heartbeat:
                record('heartbeat', 'Collecte active')
                next_heartbeat = now + 300
            if now >= next_prune:
                prune()
                next_prune = now + 60
    finally:
        proc.terminate()
        proc.wait(timeout=5)

def report():
    REPORTS.mkdir(parents=True, exist_ok=True, mode=0o700)
    with tempfile.TemporaryDirectory(prefix='manettes-') as tmp:
        root = Path(tmp)
        (root/'etat.json').write_text(json.dumps(snapshot(), ensure_ascii=False, indent=2))
        commands = {
            'systeme.txt': ['uname', '-a'],
            'dkms.txt': ['dkms', 'status', '-m', 'xone'],
            'pilote-module.txt': ['modinfo', 'xone_dongle'],
            'pilotes.txt': ['pacman', '-Q', 'xone-dkms', 'xone-dongle-firmware', 'linux-cachyos', 'linux-cachyos-lts'],
            'service.txt': ['systemctl', '--user', 'status', SERVICE, '--no-pager'],
            'service-journal.txt': ['journalctl', '--user', '-u', SERVICE, '-n', '100', '--no-pager'],
            'journald-config.txt': ['systemd-analyze', 'cat-config', 'systemd/journald.conf'],
        }
        for name, command in commands.items():
            (root/name).write_text(run(command))
        # Bounded query; dedicated archives remain the primary history.
        kernel = run(['journalctl', '_TRANSPORT=kernel', '--since', '-7days', '-n', '50000', '--no-pager', '-o', 'short-iso-precise'])
        (root/'noyau-recent.txt').write_text('\n'.join(l for l in kernel.splitlines() if MATCH.search(l)))
        sources = {
            'steam-controller.txt': HOME/'.local/share/Steam/logs/controller.txt',
            'esde.txt': HOME/'ES-DE/logs/es_log.txt',
            'esde-precedent.txt': HOME/'ES-DE/logs/es_log.txt.bak',
        }
        for name, source in sources.items():
            if source.exists():
                with source.open('rb') as f:
                    f.seek(max(0, source.stat().st_size - 8*1024*1024))
                    (root/name).write_bytes(f.read())
        cfg = read(HOME/'.config/retroarch/retroarch.cfg') or ''
        (root/'retroarch-manettes.txt').write_text('\n'.join(l for l in cfg.splitlines() if re.match(r'input_(joypad_driver|max_users|player[1-4]_(joypad_index|reserved_device|device_reservation_type))\s*=', l)))
        (root/'LIRE-MOI.txt').write_text('Rapport local, sans envoi automatique. Les événements devices sont des états de connexion, pas des pressions de touches. Archives : 30 jours au maximum, plafond total 256 Mio. Des doublons noyau sont possibles après redémarrage. Les absences de collecte sont visibles via start/heartbeat. Les journaux applicatifs peuvent contenir noms de jeux et chemins locaux.\n')
        target = REPORTS / ('manettes-' + dt.datetime.now().strftime('%Y%m%d-%H%M%S-%f') + '.tar.gz')
        with tarfile.open(target, 'w:gz') as tar:
            tar.add(root, arcname='rapport')
            if STATE.exists():
                for p in sorted(STATE.glob('events-*.jsonl')):
                    tar.add(p, arcname='rapport/evenements/'+p.name)
    return target

def gui():
    while True:
        p = subprocess.run(['zenity', '--list', '--title=Diagnostic manettes Xbox', '--text=Les connexions sont enregistrées automatiquement pendant ta session.\nAprès une coupure, marque son heure avant de débrancher le récepteur.', '--column=Action', 'Marquer une coupure', 'Créer un rapport', 'Afficher l’état', 'Ouvrir les rapports', '--width=620', '--height=340'], text=True, stdout=subprocess.PIPE)
        if p.returncode:
            return
        choice = p.stdout.strip()
        if choice == 'Marquer une coupure':
            note = subprocess.run(['zenity', '--entry', '--title=Coupure manettes', '--text=Précisions facultatives : jeu, nombre de manettes, voyants…'], text=True, stdout=subprocess.PIPE)
            if note.returncode == 0:
                record('incident', note.stdout.strip())
                subprocess.run(['zenity', '--info', '--text=Heure de la coupure enregistrée.'])
        elif choice == 'Créer un rapport':
            path = report()
            subprocess.run(['zenity', '--info', '--no-markup', '--text=Rapport enregistré :\n'+str(path), '--width=600'])
        elif choice == 'Afficher l’état':
            status = run(['systemctl', '--user', 'is-active', SERVICE]).strip()
            text = 'Collecte : '+status+'\nConservation : jusqu’à 30 jours, plafond 256 Mio.\nDossier : '+str(STATE)
            subprocess.run(['zenity', '--info', '--no-markup', '--text='+text, '--width=600'])
        else:
            REPORTS.mkdir(parents=True, exist_ok=True)
            subprocess.run(['xdg-open', str(REPORTS)])

def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser()
    parser.add_argument('action', nargs='?', choices=['gui', 'collect', 'report', 'mark', 'snapshot'], default='gui')
    parser.add_argument('note', nargs='?', default='Coupure signalée')
    args = parser.parse_args()
    if args.action == 'collect': collect()
    elif args.action == 'report': print(report())
    elif args.action == 'mark': record('incident', args.note)
    elif args.action == 'snapshot': print(json.dumps(snapshot(), indent=2))
    else: gui()

if __name__ == '__main__':
    main()
