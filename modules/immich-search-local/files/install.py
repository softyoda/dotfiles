#!/usr/bin/env python3
import json,subprocess,shlex,shutil,time,os
from pathlib import Path
import yaml

config=Path.home()/'.config/immich-update/config.json'
if not config.exists():raise SystemExit('Installer et configurer immich-ocr-persistence au préalable')
c=json.loads(config.read_text())
assets=Path.home()/'.local/share/immich-search-local'
ssh=['ssh','-F',str(Path.home()/'.ssh/config'),'-o','BatchMode=yes',c['nas_ssh']]
subprocess.run(ssh+['python3 -c '+shlex.quote((assets/'install-nas.py').read_text())],
               input=json.dumps({'stack':c['nas_stack']}),text=True,check=True)
# Routing uses the same Docker service name on each host's separate network.
marker=config.parent/'local-search-enabled'
marker.write_text('NAS CPU / worker CUDA\n')
subprocess.run(['python3',str(Path.home()/'.local/share/immich-ocr/configure-ml.py')],check=True)
stack=Path(c['local_stack']);p=stack/'docker-compose.yml'
before=p.read_text();data=yaml.safe_load(before)
s=data['services']['immich-machine-learning']
if not s['image'].startswith('ghcr.io/immich-app/immich-machine-learning:'):
 raise SystemExit('Image ML locale personnalisée')
s['image']='ghcr.io/immich-app/immich-machine-learning:${IMMICH_VERSION:-release}-cuda'
s.setdefault('deploy',{}).setdefault('resources',{}).setdefault('reservations',{})['devices']=[
 {'driver':'nvidia','count':1,'capabilities':['gpu']}]
start=before.index('  immich-machine-learning:\n')
tail=before[start+len('  immich-machine-learning:\n'):]
import re
end_match=re.search(r'(?m)^  [\w-]+:',tail)
end=start+len('  immich-machine-learning:\n')+end_match.start() if end_match else len(before)
block=''.join('  '+line+'\n' for line in yaml.safe_dump({'immich-machine-learning':s},sort_keys=False).splitlines())
after=before[:start]+block+before[end:]
if yaml.safe_load(after)!=data:raise SystemExit('Diff worker inattendu')
dc=['docker','compose','--project-directory',str(stack)]
if after!=before:
 candidate=stack/'compose.cuda-check.yml';candidate.write_text(after)
 try:
  subprocess.run(dc+['-f',str(candidate),'config','--quiet'],check=True)
  subprocess.run(dc+['-f',str(candidate),'pull','immich-machine-learning'],check=True)
  shutil.copy2(p,str(p)+'.pre-cuda-'+time.strftime('%Y%m%d-%H%M%S'))
  p.write_text(after)
 finally:candidate.unlink(missing_ok=True)
subprocess.run(dc+['up','-d','--no-deps','immich-machine-learning'],check=True)
for _ in range(60):
 s=subprocess.check_output(['docker','inspect','immich-machine-learning','--format','{{.State.Health.Status}}'],text=True).strip()
 if s=='healthy':break
 time.sleep(2)
else:raise SystemExit('Moteur CUDA non sain')
print('Recherches sur le NAS, ingestion IA sur CUDA : routage installé.')
