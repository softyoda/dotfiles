"""Executed over SSH; requires the NAS's existing Python YAML module."""
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import yaml

payload = json.load(sys.stdin)
stack = Path(payload['stack'])
compose = stack / 'docker-compose.yml'
before = compose.read_text()
data = yaml.safe_load(before)
server = data['services']['immich-server']
command = ['node /opt/immich-ocr/apply.cjs || echo "OCR: correctif incompatible, interface standard conservee"; exec start.sh']
mount = str(stack / 'ocr-hook') + ':/opt/immich-ocr:ro'
if server.get('command') not in (None, command):
    raise SystemExit('Commande de démarrage personnalisée inconnue : arrêt sans modifier la stack')
# Preserve comments, formatting and all existing configuration/credentials.
after = before
if mount not in server.get('volumes', []):
    match = re.search(r'(?m)^  immich-server:\s*$', after)
    if not match:
        raise SystemExit('Structure YAML inattendue')
    insertion = ('\n    # Préférence OCR persistante, appliquée avant le serveur web.\n'
                 '    command: ' + json.dumps(command) + '\n')
    after = after[:match.end()] + insertion + after[match.end():]
    start = after.index('  immich-server:')
    end_match = re.search(r'(?m)^  [\w-]+:', after[start+len('  immich-server:'):])
    end = start+len('  immich-server:')+end_match.start() if end_match else len(after)
    section = after[start:end]
    section, count = re.subn(r'(?m)^(    volumes:\s*)$', r'\1\n      - ' + mount, section, count=1)
    if count != 1:
        raise SystemExit('Volumes YAML inattendus')
    after = after[:start] + section + after[end:]
expected = yaml.safe_load(after)
# Verify only the three intended values differ.
restored = yaml.safe_load(after)
if server.get('command') is None:
    restored['services']['immich-server'].pop('command', None)
restored['services']['immich-server']['volumes'] = server['volumes']
if 'x-dockge' not in data:
    restored.pop('x-dockge', None)
if restored != data:
    raise SystemExit('Modification inattendue de la configuration')
hook = stack / 'ocr-hook'
hook.mkdir(exist_ok=True)
for name, content in payload['files'].items():
    if '/' in name or name.startswith('.'): raise SystemExit('Nom de fichier invalide')
    (hook / name).write_text(content)
(hook / 'config.json').write_text(json.dumps(payload['config']))
(hook / 'config.json').chmod(0o600)
if after != before:
    candidate = stack / 'docker-compose.ocr-check.yml'
    candidate.write_text(after)
    candidate.chmod(compose.stat().st_mode & 0o777)
    try:
        subprocess.run(['sudo','-n','docker','compose','--project-directory',str(stack),
                        '-f',str(candidate),'config','--quiet'],check=True)
        shutil.copy2(compose, str(compose)+'.pre-ocr-'+time.strftime('%Y%m%d-%H%M%S'))
        compose.write_text(after)
    finally:
        candidate.unlink(missing_ok=True)
subprocess.run(['sudo','-n','docker','compose','--project-directory',str(stack),
                'up','-d','--no-deps','immich-server'],check=True)
print('Hook OCR installé sur Immich.')
