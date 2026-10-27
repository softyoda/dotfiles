import collections,concurrent.futures as cf,datetime,json,time,threading,requests
from pathlib import Path
from PIL import Image
HERE=Path(__file__).resolve().parent;ES=Path.home()/'ES-DE/downloaded_media'
items=json.load(open(HERE/'bulk-metadata-plan.json'));catalog=json.load(open(HERE/'bulk-media-catalog.json'))
DEADLINE=datetime.datetime.fromisoformat('2026-10-11T18:40:30').timestamp()
TYPES={'3dboxes':['Box - 3D'],'backcovers':['Box - Back'],'physicalmedia':['Cart - Front','Disc'],'fanart':['Fanart - Background']}
bad_urls={e['url'] for e in json.load(open(HERE/'bulk-media-report-first.json'))['errors']}
plans=[]
for i in items:
 images=catalog.get(i['id'],[])
 for kind,types in TYPES.items():
  stem=ES/i['sid']/kind/Path(i['path']).stem
  if any(stem.with_name(stem.name+e).exists() for e in ['.png','.jpg','.webp']):continue
  candidates=[im for im in images if im['Type'] in types and 'https://images.launchbox-app.com/'+im['FileName'] not in bad_urls]
  if not candidates:continue
  desired='Europe' if 'Europe' in i['label'] else 'Japan' if 'Japan' in i['label'] else 'North America'
  candidates.sort(key=lambda v:(v.get('Region','')!=desired,v.get('Region','') not in ['North America','World',''],types.index(v['Type']),v['FileName']))
  im=candidates[0];dest=stem.with_name(stem.name+Path(im['FileName']).suffix.lower())
  plans.append(dict(kind=kind,sid=i['sid'],label=i['label'],url='https://images.launchbox-app.com/'+im['FileName'],dest=str(dest),id=i['id']))
# Spread the initial downloads across image types and systems.
plans.sort(key=lambda p:(p['label'],p['kind']))
(HERE/'bulk-media-plan.json').write_text(json.dumps(plans,ensure_ascii=False,indent=2))
local=threading.local()
def fetch(p):
 if time.time()>=DEADLINE:return ('deadline',0)
 if not hasattr(local,'session'):local.session=requests.Session()
 r=local.session.get(p['url'],timeout=(8,20));r.raise_for_status()
 dest=Path(p['dest']);dest.parent.mkdir(parents=True,exist_ok=True);tmp=dest.with_name(dest.name+'.download');tmp.write_bytes(r.content)
 try:
  with Image.open(tmp) as im:im.verify()
  tmp.replace(dest)
 except Exception:tmp.unlink(missing_ok=True);raise
 return ('downloaded',len(r.content))
counts=collections.Counter();kinds=collections.Counter();errors=[];size=0
print('Planned',len(plans),flush=True)
with cf.ThreadPoolExecutor(max_workers=16) as pool:
 futures={pool.submit(fetch,p):p for p in plans}
 for n,f in enumerate(cf.as_completed(futures),1):
  p=futures[f]
  try:
   status,b=f.result();counts[status]+=1;size+=b
   if status=='downloaded':kinds[p['kind']]+=1
  except Exception as e:errors.append(dict(url=p['url'],error=str(e)))
  if n%100==0:
   report=dict(done=n,planned=len(plans),counts=dict(counts),types=dict(kinds),bytes=size,errors=len(errors));print(json.dumps(report),flush=True);(HERE/'bulk-media-progress.json').write_text(json.dumps(report,indent=2))
report=dict(planned=len(plans),counts=dict(counts),types=dict(kinds),bytes=size,errors=errors,finished=datetime.datetime.now().isoformat())
(HERE/'bulk-media-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
