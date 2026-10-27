import json,time,urllib.request
from pathlib import Path
base='http://elasticsearch:9200'
def request(path, body=None, method=None):
 data=None if body is None else json.dumps(body).encode()
 req=urllib.request.Request(base+path,data=data,method=method,headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=90) as r:return json.load(r)
status=Path('/config/scan-logs/all.status.log')
for attempt in range(180):
 lines=status.read_text().splitlines()
 if any('END diskover-tout exit=' in line for line in lines):
  end=[line for line in lines if 'END diskover-tout exit=' in line][-1]
  if not end.endswith(('exit=0','exit=64')):raise RuntimeError(end)
  break
 if attempt%5==0:
  lines=Path('/config/scan-logs/tout.log').read_text().splitlines()
  print(lines[-1] if lines else 'Scan en cours',flush=True)
 time.sleep(10)
else:raise TimeoutError('Le scan dépasse 30 minutes. Anciens index conservés.')
request('/diskover-tout/_refresh',method='POST')
checks={}
for name in ['linux','intel','truenas','truenas-qbittorrent','truenas-immich-uploads','truenas-immich-thumbs']:
 query={'query':{'bool':{'filter':[{'term':{'type':'file'}},{'bool':{'should':[{'term':{'parent_path':'/scan/'+name}},{'prefix':{'parent_path':'/scan/'+name+'/'}}],'minimum_should_match':1}}]}}}
 old=request('/diskover-'+name+'/_count',query)['count']
 new=request('/diskover-tout/_count',query)['count']
 checks[name]={'previous_files':old,'unified_files':new}
 if new < old*0.95:raise RuntimeError(f'Couverture insuffisante: {name}: {old} -> {new}. Anciens index conservés.')
Path('/config/scan-logs/unified-validation.json').write_text(json.dumps(checks,indent=2))
print(json.dumps(checks),flush=True)
for name in checks:
 request('/diskover-'+name,method='DELETE')
print('VALIDÉ : seul diskover-tout conservé.',flush=True)
