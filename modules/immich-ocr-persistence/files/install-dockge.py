import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import yaml

p=json.load(sys.stdin);stack=Path(p['stack'])
compose=stack/'docker-compose.yml'
before=compose.read_text();data=yaml.safe_load(before)
service=data['services']['dockge']
old_command=['sh','-c','node /app/data/immich-maintenance/patch-dockge.cjs && exec tsx ./backend/index.ts']
command=['sh','-c','node /app/data/immich-maintenance/patch-dockge.cjs || echo "Immich: integration Dockge incompatible, voir les logs"; exec tsx ./backend/index.ts']
if service.get('command') not in (None,old_command,command):
    raise SystemExit('Dockge : commande personnalisée inconnue')
dest=stack/'data/immich-maintenance';dest.mkdir(exist_ok=True)
(dest/'patch-dockge.cjs').write_text(p['patch'])
if service.get('command')!=command:
    if service.get('command') == old_command:
        after=before.replace('    command: '+json.dumps(old_command), '    command: '+json.dumps(command), 1)
    else:
        after=before.replace('  dockge:\n','  dockge:\n    command: '+json.dumps(command)+'\n',1)
    test=yaml.safe_load(after)
    if 'command' in service: test['services']['dockge']['command']=service['command']
    else: test['services']['dockge'].pop('command')
    if test!=data:raise SystemExit('Modification Dockge inattendue')
    candidate=stack/'compose.ocr-check.yml';candidate.write_text(after)
    try:
        subprocess.run(['sudo','-n','docker','compose','--project-directory',str(stack),
                        '-f',str(candidate),'config','--quiet'],check=True)
        shutil.copy2(compose,str(compose)+'.pre-immich-'+time.strftime('%Y%m%d-%H%M%S'))
        compose.write_text(after)
    finally:candidate.unlink(missing_ok=True)
subprocess.run(['sudo','-n','docker','compose','--project-directory',str(stack),'up','-d','--no-deps','dockge'],check=True)
print('Bouton Mettre à jour de Dockge relié à la procédure Immich côté NAS.')
