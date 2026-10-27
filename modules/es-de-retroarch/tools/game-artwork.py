#!/usr/bin/env python3
"""Fetch real Libretro artwork for the installed playlists; no ROM transfers."""
import os
import concurrent.futures as cf
import collections
import html
import json
from pathlib import Path
import re
import threading
import time
import unicodedata
import urllib.parse
import xml.etree.ElementTree as ET
import requests
from PIL import Image

ROOT=Path(__file__).resolve().parent
CACHE=ROOT/'artwork-cache'; CACHE.mkdir(exist_ok=True)
RA=Path.home()/'.config/retroarch'
NAS=Path(os.environ['ROMS_NAS_DIR'])
HOST='https://thumbnails.libretro.com/'
TYPES={'Named_Boxarts':'covers','Named_Snaps':'screenshots','Named_Titles':'titlescreens','Named_Logos':'marquees'}
SIDS=dict(zip(['Atari - 2600','Nintendo - NES','Sega - Master System','NEC - TurboGrafx-16','NEC - TurboGrafx CD','Nintendo - SNES','Sega - Genesis','Sega - Sega CD','Nintendo - Game Boy','Sega - Game Gear','Nintendo - Game Boy Color','Nintendo - N64','Sony - PS1','Sega - Saturn','Nintendo - Game Boy Advance','Nintendo - GameCube','Sega - Dreamcast','Nintendo - DS','Sony - PSP','Arcade - Mame 2003 Plus','SNK - NEO GEO'],['atari2600','nes','mastersystem','pcengine','pcenginecd','snes','megadrive','segacd','gb','gamegear','gbc','n64','psx','saturn','gba','gc','dreamcast','nds','psp','arcade','neogeo']))
LOCAL=threading.local()
def session():
    if not hasattr(LOCAL,'session'):
        LOCAL.session=requests.Session()
        LOCAL.session.headers['User-Agent']='RetroArch-library-artwork/1.0 (personal library)'
    return LOCAL.session

def get(url):
    for attempt in range(3):
        try:
            r=session().get(url,timeout=(15,75))
            if r.status_code==404:return None
            r.raise_for_status()
            return r.content
        except requests.RequestException:
            if attempt==2:raise
            time.sleep(2*(attempt+1))

def sanitize(s):return re.sub(r'[&*/:`<>?\\|\"]','_',s)
def base(s):
    s=re.sub(r'\([^)]*\)','',s.split('[')[0])
    s=s.strip()
    s=re.sub(r'^(the|a|an)\s+','',s,flags=re.I)
    s=re.sub(r',\s*(the|a|an)$','',s,flags=re.I)
    return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower())

def catalog(system,kind):
    file=CACHE/(system+'--'+kind+'.json')
    if file.exists():return json.loads(file.read_text())
    data=get(HOST+urllib.parse.quote(system,safe='')+'/'+kind+'/')
    names=sorted({urllib.parse.unquote(html.unescape(x)) for x in re.findall(r'href="([^"]+)"',data.decode(errors='replace') if data else '') if x.lower().endswith('.png')})
    file.write_text(json.dumps(names,ensure_ascii=False))
    return names

def choose(label,names,index):
    wanted=sanitize(label)
    if wanted+'.png' in names:return wanted+'.png','exact'
    candidates=index.get(base(wanted),[])
    if not candidates:return None,None
    regions=set(re.findall(r'USA|Europe|Japan|World|France',label))
    def score(name):
        overlap=len(regions & set(re.findall(r'USA|Europe|Japan|World|France',name)))
        return (-overlap,0 if 'USA' in name else 1,len(name),name)
    return sorted(candidates,key=score)[0],'same_title'

def plan():
    arcade={g.get('name'):g.findtext('description') for g in ET.parse(CACHE/'mame.xml').getroot().findall('game')}
    items=[]
    for pl in sorted((RA/'playlists').glob('*.lpl')):
        data=json.loads(pl.read_text())
        for item in data.get('items',[]):
            p=Path(item['path'])
            if not p.is_relative_to(NAS):continue
            system=p.relative_to(NAS).parts[0]
            db=Path(item.get('db_name') or pl.name).stem
            source='MAME' if system=='Arcade - Mame 2003 Plus' else db
            search=arcade.get(p.stem,item['label']) if system in ['Arcade - Mame 2003 Plus','SNK - NEO GEO'] else item['label']
            items.append(dict(system=system,sid=SIDS[system],playlist=str(pl),db=db,source=source,path=str(p),label=item['label'],search=search,core_path=item['core_path'],core_name=item['core_name']))
    keys=sorted({(i['source'],kind) for i in items for kind in TYPES})
    cats={};indexes={}
    with cf.ThreadPoolExecutor(max_workers=6) as pool:
        jobs={pool.submit(catalog,*key):key for key in keys}
        for future in cf.as_completed(jobs):
            key=jobs[future];names=future.result();cats[key]=set(names)
            index=collections.defaultdict(list)
            for n in names:index[base(Path(n).stem)].append(n)
            indexes[key]=index
            print('CATALOG',key,len(names),flush=True)
    for item in items:
        item['art']={}
        for kind in TYPES:
            key=item['source'],kind
            found,mode=choose(item['search'],cats[key],indexes[key])
            if found:
                item['art'][kind]=dict(url=HOST+urllib.parse.quote(item['source'],safe='')+'/'+kind+'/'+urllib.parse.quote(found,safe=''),matched=found,mode=mode,dest=str(RA/'thumbnails'/item['db']/kind/(sanitize(item['label'])+'.png')))
    (ROOT/'artwork-plan.json').write_text(json.dumps(items,ensure_ascii=False,indent=2))
    print(json.dumps(dict(games=len(items),images=sum(len(i['art']) for i in items),without_art=[dict(system=i['system'],label=i['label'],search=i['search']) for i in items if not i['art']]),ensure_ascii=False),flush=True)

def valid(p):
    try:
        with Image.open(p) as im:im.verify()
        return True
    except (OSError,ValueError,SyntaxError):return False

def download_one(a):
    p=Path(a['dest'])
    if p.exists() and valid(p):return 'existing',str(p),p.stat().st_size
    data=get(a['url'])
    if not data:return 'missing',str(p),0
    p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_suffix('.png.downloading');tmp.write_bytes(data)
    if not valid(tmp):
        tmp.unlink();raise ValueError('Invalid image: '+a['url'])
    tmp.replace(p)
    return 'downloaded',str(p),len(data)

def download():
    items=json.loads((ROOT/'artwork-plan.json').read_text())
    arts={a['dest']:a for i in items for a in i['art'].values()}
    counts=collections.Counter();errors=[];size=0
    with cf.ThreadPoolExecutor(max_workers=6) as pool:
        jobs={pool.submit(download_one,a):a for a in arts.values()}
        for j,future in enumerate(cf.as_completed(jobs),1):
            try:
                status,path,n=future.result();counts[status]+=1;size+=n
            except Exception as e:errors.append(dict(url=jobs[future]['url'],error=str(e)))
            if j%100==0:print(json.dumps(dict(done=j,total=len(arts),counts=counts,bytes=size,errors=len(errors))),flush=True)
    report=dict(games=len(items),planned_images=len(arts),counts=counts,bytes=size,errors=errors)
    (ROOT/'artwork-download-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps(report,ensure_ascii=False),flush=True)

if __name__=='__main__':
    import sys
    {'plan':plan,'download':download}[sys.argv[1]]()
