import os
from pathlib import Path
import json,re,collections,unicodedata,xml.etree.ElementTree as E
BASE=Path(os.environ['ROMS_NAS_DIR']).parent;DEST=BASE/'retro-roms-best-set';incoming=json.load(open('incoming-staged.json'));rows=json.load(open('incoming-existing.json'))+incoming['games']
for r in rows:
 if Path(r['name']).suffix.lower()=='.gbc':r['sid']='gbc';r['folder']='Nintendo - Game Boy Color'
meta={};id_by_key={}
def norm(t):
 t=unicodedata.normalize('NFKD',t).encode('ascii','ignore').decode().lower();t=re.sub(r'\([^)]*\)|\[[^]]*\]','',t);t=re.sub(r'\b(?:disc|disk|cd)\s*\d+(?:\s*of\s*\d+)?','',t);t=t.replace('&','and');t=re.sub(r'\bthe\b','',t)
 for roman,num in [('viii','8'),('vii','7'),('vi','6'),('iv','4'),('iii','3'),('ii','2')]:t=re.sub(r'\b'+roman+r'\b',num,t)
 return re.sub('[^a-z0-9]','',t)
for root in (BASE/'tmp_dl').iterdir():
 p=root/'gamelist.xml'
 if not p.exists():continue
 for g in E.parse(p).getroot().findall('game'):
  src=str(root/g.findtext('path','').removeprefix('./'));fields={c.tag:c.text or '' for c in g};fields['_id']=g.get('id','');fields['_root']=str(root);meta[src]=fields
for r in rows:
 r['metadata']=meta.get(r['source'],{})
 key=norm(Path(r['name']).stem);r['title_key']=key
 # Group all language/region variants; hacks with explicit identifiers remain distinct works.
 hacks=re.findall(r'\[(H\.[^]]+)\]',r['name'],re.I)
 # One edition per base game, including patch variants.
 r['base_key']=key
 if r['metadata'].get('_id'):id_by_key[(r['sid'],key)]=r['metadata']['_id']
for r in rows:
 r['key']=r['sid']+':'+('ss-'+id_by_key[(r['sid'],r['base_key'])] if (r['sid'],r['base_key']) in id_by_key else r['base_key'])
 name=r['name'].lower();lang=r['metadata'].get('lang','').lower();r['language_rank']=0
 if re.search(r'\bfr\b|french|france|t[+._ -](?:fre|fra)',name+' '+lang):r['language_rank']=3
 elif re.search(r'\ben\b|english|\busa\b|\bworld\b|\beurope\b|t[+._ -]eng',name+' '+lang):r['language_rank']=2
 if r.get('pbp_info',{}).get('DISC_ID','').startswith(('SLUS','SCUS')):r['language_rank']=max(r['language_rank'],2)
 # Prefer verified regular releases to hacks/bad dumps at equal language priority.
 bad=bool(re.search(r'\[(?:b|o|a|h|p|f)\d*\]|prototype|beta|demo|sample|t-',name))
 r['rank']=(r['language_rank'],not bool(hacks if False else re.search(r'\[H\.',r['name'],re.I)),not bad,not r.get('hackpack',False),r.get('existing',False),r['name'].lower().endswith('.chd'),bool(r['metadata']))
groups=collections.defaultdict(list)
for r in rows:groups[r['key']].append(r)
keep=[];reject=[];replacement={}
def discnumber(name):
 m=re.search(r'(?:disc|disk|cd)[ _-]*(\d+)',name,re.I);return int(m[1]) if m else None
def release(name):return re.sub(r'(?:disc|disk|cd)[ _-]*\d+(?:\s*of\s*\d+)?','DISC',Path(name).stem,flags=re.I)
for k,rs in groups.items():
 best=max(rs,key=lambda r:(r['rank'],-len(r['name'])))
 # Keep all discs of the winning edition, not discs from another locale/revision.
 selected=[best]
 if discnumber(best['name']) is not None:
  bydisc={}
  for r in rs:
   if release(r['name'])==release(best['name']):
    d=discnumber(r['name'])
    if d not in bydisc or r['rank']>bydisc[d]['rank']:bydisc[d]=r
  selected=list(bydisc.values())
 for r in selected:
  r['target']=r['source'] if r.get('existing') else str(DEST/r['folder']/('Hacks' if '-hack-' in r['base_key'] else '')/r['name'])
  keep.append(r)
 for r in rs:
  if any(r is a for a in selected):continue
  r['reason']='identical_content' if any(r['identity']==a['identity'] for a in selected) else 'other_language_or_edition'
  r['selected']=selected[0]['target'];reject.append(r)
  if r.get('existing'):replacement[r['source']]=selected[0]['target']
# Deduplicate byte-identical games across alternate names, within the same platform.
byidentity={};final=[]
for r in sorted(keep,key=lambda r:r['rank'],reverse=True):
 key=(r['sid'],r['identity'])
 if key in byidentity:
  r['reason']='identical_content_alternate_name';r['selected']=byidentity[key]['target'];reject.append(r)
  if r.get('existing'):replacement[r['source']]=r['selected']
 else:byidentity[key]=r;final.append(r)
# Resolve replacement chains.
for old in list(replacement):
 seen=set();new=replacement[old]
 while new in replacement and new not in seen:seen.add(new);new=replacement[new]
 replacement[old]=new
# Unique destination names are required before any mutation.
targets=[r['target'] for r in final];assert len(targets)==len(set(targets)),'Destination collision'
plan={'keep':final,'reject':reject,'replacements':replacement,'policy':'one release per title, FR then EN; explicit named hacks distinct; originals quarantined not deleted'}
Path('incoming-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2))
print('KEEP',len(final),'NEW',sum(not r.get('existing') for r in final),'REJECT',len(reject),'EXISTING REPLACED',len(replacement));print('SYSTEMS',dict(collections.Counter(r['sid'] for r in final)));print('REASONS',dict(collections.Counter(r['reason'] for r in reject)));print('FR',sum(r['language_rank']==3 for r in final));print('Existing replacements sample',list(replacement.items())[:15])
