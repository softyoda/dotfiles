import json
from pathlib import Path
import shutil
import subprocess
import time
import yaml

c=json.loads((Path.home()/'.config/immich-update/config.json').read_text())
stack=Path(c['local_stack']);p=stack/'docker-compose.yml'
before=p.read_text();d=yaml.safe_load(before);s=d['services']['immich-microservices']
command=['exec node /opt/immich-ocr/worker-guard.cjs']
if s.get('command') not in (None,command):raise SystemExit('Commande worker personnalisée inconnue')
hook=str(Path.home()/'.local/share/immich-ocr/worker-guard.cjs')+':/opt/immich-ocr/worker-guard.cjs:ro'
if s.get('command')!=command:
    after=before.replace('  immich-microservices:\n','  immich-microservices:\n    command: '+json.dumps(command)+'\n',1)
    start=after.index('  immich-microservices:')
    section=after[start:]
    section=section.replace('    volumes:\n','    volumes:\n      - '+hook+'\n',1)
    section=section.replace('    environment:\n','    environment:\n      - IMMICH_WORKER_EXPECTED_VERSION=${IMMICH_VERSION}\n      - IMMICH_SERVER_URL='+c['server_url']+'\n',1)
    after=after[:start]+section
    test=yaml.safe_load(after);ts=test['services']['immich-microservices']
    ts.pop('command');ts['volumes'].remove(hook)
    ts['environment']=[e for e in ts['environment'] if not e.startswith(('IMMICH_SERVER_URL=','IMMICH_WORKER_EXPECTED_VERSION='))]
    if test!=d:raise SystemExit('Modification worker inattendue')
    check=stack/'compose.ocr-check.yml';check.write_text(after)
    try:
        subprocess.run(['docker','compose','--project-directory',str(stack),'-f',str(check),'config','--quiet'],check=True)
        shutil.copy2(p,str(p)+'.pre-ocr-'+time.strftime('%Y%m%d-%H%M%S'))
        p.write_text(after)
    finally:check.unlink(missing_ok=True)
subprocess.run(['docker','compose','--project-directory',str(stack),'up','-d','--no-deps','immich-microservices'],check=True)
