import collections,datetime,json,xml.etree.ElementTree as E
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent;ES=Path.home()/'ES-DE'
plans=[]
for f in ['bulk-media-plan-first.json','bulk-media-plan.json']:plans+=json.load(open(ROOT/f))
paths={p['dest']:p for p in plans if not(p['label']=='invaders' and p['id']=='40058')}
counts=collections.Counter();size=0;invalid=[];unavailable=[]
for dest,entry in paths.items():
 p=Path(dest)
 if not p.exists():unavailable.append(dest);continue
 try:
  with Image.open(p) as im:im.verify()
 except Exception as e:invalid.append(dict(path=dest,error=str(e)));continue
 counts[entry['kind']]+=1;size+=p.stat().st_size
fields=collections.Counter();broken=[];metadata={}
backup=Path(json.load(open(ROOT/'bulk-metadata-report.json'))['backup'])
for p in (ES/'gamelists').glob('*/gamelist.xml'):
 t=E.parse(p);metadata[p.parent.name]={g.findtext('path'):g for g in t.getroot().findall('game')}
 for g in t.getroot().findall('game'):
  if g.findtext('hidden')=='true':continue
  fields['games']+=1
  for k in ['desc','developer','publisher','genre','players','releasedate','rating']:fields[k]+=bool(g.findtext(k))
 for g in E.parse(backup/'gamelists'/p.parent.name/'gamelist.xml').getroot().findall('game'):
  for child in g:
   assert not child.text or metadata[p.parent.name][g.findtext('path')].findtext(child.tag)==child.text
for p in (ES/'downloaded_media').rglob('*'):
 if p.is_symlink() and not p.exists():broken.append(str(p))
report=dict(finished=datetime.datetime.now().isoformat(),metadata=dict(fields),new_media=sum(counts.values()),media_types=dict(counts),media_bytes=size,invalid_images=invalid,unavailable_source_images=len(unavailable),broken_links=broken,existing_metadata_preserved=True,rom_bytes_copied=0,video_and_manual_scraping_complete=False,description_language='Existing descriptions preserved; new bulk descriptions generally English',source='https://gamesdb.launchbox-app.com/Metadata.zip',backup=str(backup))
(ROOT/'external-scrape-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
