#!/usr/bin/env python3
"""Persist the remote ML URL using Immich's supported admin API."""
import json
import os
from pathlib import Path
import urllib.request
import urllib.parse

def configure():
    c=json.loads((Path.home()/'.config/immich-update/config.json').read_text())
    env={}
    for line in (Path(c['local_stack'])/'.env').read_text().splitlines():
        if '=' in line and not line.lstrip().startswith('#'):
            k,v=line.split('=',1);env[k.strip()]=v.strip().strip('"').strip("'")
    key=env.get('IMMICH_API_KEY')
    if not key:
        raise RuntimeError('Clé API administrative absente de la configuration locale')
    remote=c['worker_ping'].removesuffix('/ping').rstrip('/')
    parts=urllib.parse.urlsplit(remote)
    if parts.scheme not in ('http','https') or not parts.hostname or parts.username or parts.password:
        raise RuntimeError('URL ML invalide')
    def api(method,data=None):
        req=urllib.request.Request(c['server_url']+'/api/system-config',
            data=json.dumps(data).encode() if data is not None else None,method=method,
            headers={'User-Agent':'immich-maintenance','x-api-key':key,'Content-Type':'application/json'})
        with urllib.request.urlopen(req,timeout=20) as r:return json.load(r)
    config=api('GET')
    current=config['machineLearning']['urls']
    # No ML container exists on the NAS. Preserve any other custom fallback URLs.
    desired=[remote]+[u for u in current if u not in (remote,'http://immich-machine-learning:3003')]
    if current!=desired:
        state=Path.home()/'.local/state/immich';state.mkdir(parents=True,exist_ok=True)
        backup=state/'ml-urls-before.json'
        if not backup.exists():
            with os.fdopen(os.open(backup,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as f:json.dump(current,f)
        config['machineLearning']['urls']=desired
        api('PUT',config)
        if api('GET')['machineLearning']['urls']!=desired:
            raise RuntimeError('Vérification de la configuration ML échouée')
        print('URL du moteur IA distant corrigée et enregistrée dans Immich.')
    else:print('URL du moteur IA distant déjà configurée.')
if __name__=='__main__':
    try:configure()
    except Exception as e:
        # Do not print request headers, configuration or API response bodies.
        raise SystemExit('Configuration ML impossible : '+str(e))
