import json,subprocess,sys,shutil,time
from pathlib import Path
import yaml

stack=Path(json.load(sys.stdin)['stack'])
p=stack/'docker-compose.yml';before=p.read_text();data=yaml.safe_load(before)
server=data['services']['immich-server'];db=data['services']['immich-db']
networks=sorted(set(server['networks'])&set(db['networks']))
if len(networks)!=1:raise SystemExit('Réseau privé Immich ambigu')
service={
 'image':'ghcr.io/immich-app/immich-machine-learning:${IMMICH_VERSION:-release}',
 'container_name':'immich-machine-learning','restart':'unless-stopped',
 'cpus':2,'mem_limit':'1536m',
 'environment':{'MACHINE_LEARNING_MODEL_INTRA_OP_THREADS':'1',
                'MACHINE_LEARNING_MODEL_INTER_OP_THREADS':'1',
                'MACHINE_LEARNING_MODEL_TTL':'300'},
 'volumes':[str(stack/'ml-query-cache')+':/cache'],
 'networks':networks}
existing=data['services'].get('immich-machine-learning')
if existing is not None and existing!=service:
 raise SystemExit('Service ML NAS déjà personnalisé : aucune modification automatique')
def dc(*args):
 subprocess.run(['sudo','-n','docker','compose','--project-directory',str(stack),*args],check=True)
if existing is None:
 block=yaml.safe_dump({'immich-machine-learning':service},sort_keys=False)
 block=''.join('  '+line+'\n' for line in block.splitlines())
 after=before.replace('services:\n','services:\n'+block,1)
 expected=yaml.safe_load(after);expected['services'].pop('immich-machine-learning')
 if expected!=data:raise SystemExit('Diff Compose inattendu')
 candidate=stack/'compose.local-search-check.yml';candidate.write_text(after)
 try:
  dc('-f',str(candidate),'config','--quiet')
  dc('-f',str(candidate),'pull','immich-machine-learning')
  shutil.copy2(p,str(p)+'.pre-local-search-'+time.strftime('%Y%m%d-%H%M%S'))
  p.write_text(after)
 finally:candidate.unlink(missing_ok=True)
dc('up','-d','--no-deps','immich-machine-learning')
for _ in range(60):
 s=subprocess.check_output(['sudo','-n','docker','inspect','immich-machine-learning','--format','{{.State.Health.Status}}'],text=True).strip()
 if s=='healthy':break
 time.sleep(2)
else:raise SystemExit('Moteur ML du NAS non sain')
print('Moteur de recherche CPU du NAS sain, réseau Docker privé uniquement.')
