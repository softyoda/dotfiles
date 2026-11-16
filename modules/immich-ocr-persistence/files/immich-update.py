#!/usr/bin/env python3
"""Desktop update and automatic local alignment; the NAS owns the update transaction."""
import fcntl
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import time
import urllib.request

CONFIG = json.loads((Path.home() / '.config/immich-update/config.json').read_text())
STACK = Path(CONFIG['local_stack'])
SERVICES = ['immich-machine-learning', 'immich-microservices']
def run(args, capture=False, **kwargs):
    return subprocess.run(args, check=True, text=True,
        stdout=subprocess.PIPE if capture else None, **kwargs).stdout
def dc(*args, version=None):
    return run(['docker','compose','--project-directory',str(STACK),*args],
               env={**os.environ, **({'IMMICH_VERSION':version} if version else {})})
def inspect(name):
    return json.loads(run(['docker','inspect',name,'--format','{{json .}}'],True))
def version():
    with urllib.request.urlopen(urllib.request.Request(CONFIG['server_url']+'/api/server/version', headers={'User-Agent':'immich-maintenance'}),timeout=8) as r:
        v=json.load(r)
    return 'v{major}.{minor}.{patch}'.format(**v)
def align():
    target=version()
    if not re.fullmatch(r'v\d+\.\d+\.\d+',target):
        raise RuntimeError('Version serveur invalide')
    states=[inspect(n) for n in SERVICES]
    if not any(s['State']['Running'] for s in states):
        print('Workers arrêtés volontairement : aucun démarrage automatique.',flush=True)
        return
    if all(s['Config']['Image'].split(':')[-1].removesuffix('-cuda')==target for s in states):
        print('Workers déjà alignés sur '+target,flush=True)
        return
    print('Alignement des workers sur '+target,flush=True)
    dc('pull',*SERVICES,version=target)
    # The startup guard also verifies this version before consuming jobs.
    dc('stop',*SERVICES)
    p=STACK/'.env';s=p.read_text()
    pattern=r'(?m)^[ \t]*(?:export[ \t]+)?IMMICH_VERSION[ \t]*=.*$'
    text=re.sub(pattern,'IMMICH_VERSION='+target,s) if re.search(pattern,s) else s+'\nIMMICH_VERSION='+target+'\n'
    backup=p.with_name('.env.pre-align-'+time.strftime('%Y%m%d-%H%M%S'))
    backup.write_text(s);backup.chmod(0o600)
    p.write_text(text)
    dc('up','-d','--no-deps',*SERVICES,version=target)
    for _ in range(90):
        states=[inspect(n) for n in SERVICES]
        if all(s['State'].get('Health',{}).get('Status')=='healthy' for s in states):
            print('Workers vérifiés en '+target,flush=True);return
        time.sleep(4)
    raise RuntimeError('Workers non sains : consulter les journaux')
def main():
    state=Path.home()/'.local/state/immich';state.mkdir(parents=True,exist_ok=True)
    with (state/'update.lock').open('w') as lock:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:
            print('Une opération Immich est déjà en cours.');return
        if '--align-only' not in sys.argv:
            ssh=['ssh','-F',str(Path.home()/'.ssh/config'),'-o','BatchMode=yes','-o','ConnectTimeout=10',CONFIG['nas_ssh']]
            args=['sudo','-n','docker','exec','-w',CONFIG['dockge_stack'],'dockge',
                  'flock','-n','.immich-update.lock','node','ocr-hook/update-nas.cjs']
            for option in ('--check','--resume'):
                if option in sys.argv:args.append(option)
            run(ssh+[shlex.join(args)])
        if '--check' not in sys.argv:align()
if __name__=='__main__':
    try:main()
    except Exception as e:
        print('Échec : '+str(e),file=sys.stderr,flush=True);sys.exit(1)
