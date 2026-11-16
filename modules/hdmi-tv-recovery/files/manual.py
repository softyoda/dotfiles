#!/usr/bin/python
"""Relance manuelle HDMI par changement de mode, puis restauration du mode initial."""
import fcntl
import json
import logging
import os
from pathlib import Path
import subprocess
import time

LOG = logging.getLogger('hdmi-manual')

def alternate_mode(output):
    modes = [m for m in output.get('modes', [])
             if m['id'] != output['currentModeId']
             and m.get('refreshRate', 0) >= 23
             and m.get('size', {}).get('width', 0) <= 3840
             and m.get('size', {}).get('height', 0) <= 2160]
    # Prefer the ordinary 1080p mode tested successfully; avoid custom tall modes.
    def rank(m):
        size = m['size']
        return (size == {'width': 1920, 'height': 1080},
                -abs(m.get('refreshRate', 0) - 60), size['width'] * size['height'])
    if not modes:
        raise RuntimeError('Aucun autre mode HDMI standard disponible')
    return max(modes, key=rank)

def cycle(output, run=subprocess.run, sleep=time.sleep):
    name = output['name']
    original = output['currentModeId']
    alternate = alternate_mode(output)
    LOG.info('%s : mode %s temporaire, puis restauration de %s', name, alternate['id'], original)
    try:
        run(['kscreen-doctor', f"output.{name}.mode.{alternate['id']}"], check=True, timeout=15)
        sleep(5)
    finally:
        # Restore even when the temporary mode fails; never disable the sole output.
        run(['kscreen-doctor', f'output.{name}.mode.{original}'], check=True, timeout=15)

def main():
    logging.basicConfig(level=logging.INFO)
    state = Path(os.environ.get('XDG_STATE_HOME', str(Path.home()/'.local/state'))) / 'hdmi-recovery'
    state.mkdir(parents=True, exist_ok=True)
    with (state/'manual.lock').open('w') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return
        data = json.loads(subprocess.check_output(['kscreen-doctor', '-j'], text=True, timeout=15))
        outputs = [o for o in data['outputs'] if o.get('connected') and o.get('enabled')
                   and o.get('name', '').startswith('HDMI-')]
        if len(outputs) != 1:
            raise RuntimeError('La récupération attend une seule sortie HDMI active ; aucune sortie modifiée')
        (state/'before-manual.json').write_text(json.dumps(data, ensure_ascii=False, indent=2))
        cycle(outputs[0])
        LOG.info('Mode initial rétabli ; vérifier visuellement le signal sur la TV')

if __name__ == '__main__':
    main()
