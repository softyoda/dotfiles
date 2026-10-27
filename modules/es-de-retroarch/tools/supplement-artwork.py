import importlib.util,json,collections,concurrent.futures as cf,urllib.parse
from pathlib import Path
spec=importlib.util.spec_from_file_location('art',Path(__file__).with_name('game-artwork.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
items=json.loads((m.ROOT/'artwork-plan.json').read_text())
aliases=json.loads((m.ROOT/'artwork-aliases.json').read_text())
extra=['FBNeo - Arcade Games','Nintendo - Family Computer Disk System']
with cf.ThreadPoolExecutor(max_workers=2) as pool:
    list(pool.map(lambda k:m.catalog(*k),[(s,t) for s in extra for t in m.TYPES]))
# The official GitHub repository can be newer than the thumbnail mirror.
tree_file=m.CACHE/'psp-github-tree.json'
if not tree_file.exists():
    tree_file.write_bytes(m.get('https://api.github.com/repos/libretro-thumbnails/Sony_-_PlayStation_Portable/git/trees/master?recursive=1'))
tree=json.loads(tree_file.read_text());assert not tree.get('truncated'), 'Incomplete GitHub index'
indexes={}
for f in m.CACHE.glob('*--Named_*.json'):
    system,kind=f.stem.split('--');names=json.loads(f.read_text());idx=collections.defaultdict(list)
    for n in names:idx[m.base(Path(n).stem)].append(n)
    indexes[system,kind]=(set(names),idx)
for kind in m.TYPES:
    names=[Path(e['path']).name for e in tree['tree'] if e['path'].startswith(kind+'/') and e['path'].endswith('.png')]
    idx=collections.defaultdict(list)
    for n in names:idx[m.base(Path(n).stem)].append(n)
    indexes['PSP-GitHub',kind]=(set(names),idx)
added=[]
for item in items:
    queries=[item['search']]
    for system,prefix,title in aliases:
        if item['system']==system and item['label'].startswith(prefix):queries.insert(0,title)
    sources=[item['source']]
    if item['system'] in ['SNK - NEO GEO','Arcade - Mame 2003 Plus']:sources+=['MAME','FBNeo - Arcade Games']
    if Path(item['path']).suffix=='.fds':sources.insert(0,'Nintendo - Family Computer Disk System')
    if item['system']=='Sony - PSP':sources.insert(0,'PSP-GitHub')
    for kind in m.TYPES:
        if kind in item['art']:continue
        found=None
        for source in sources:
            for query in queries:
                names,idx=indexes[source,kind]
                found,mode=m.choose(query,names,idx)
                if found:break
            if found:break
        if not found:continue
        prefix='https://raw.githubusercontent.com/libretro-thumbnails/Sony_-_PlayStation_Portable/master/' if source=='PSP-GitHub' else m.HOST+urllib.parse.quote(source,safe='')+'/'
        a=dict(url=prefix+kind+'/'+urllib.parse.quote(found,safe=''),matched=found,mode='reviewed_alias' if query!=item['search'] else mode,dest=str(m.RA/'thumbnails'/item['db']/kind/(m.sanitize(item['label'])+'.png')))
        item['art'][kind]=a;added.append(a)
(m.ROOT/'artwork-plan.json').write_text(json.dumps(items,ensure_ascii=False,indent=2))
print('Added',len(added),'images',flush=True)
errors=[]
with cf.ThreadPoolExecutor(max_workers=2) as pool:
    futures={pool.submit(m.download_one,a):a for a in added}
    for f in cf.as_completed(futures):
        try:f.result()
        except Exception as e:errors.append(dict(url=futures[f]['url'],error=str(e)))
missing=[dict(system=i['system'],label=i['label'],search=i['search']) for i in items if not i['art']]
(m.ROOT/'artwork-supplement-report.json').write_text(json.dumps(dict(added=len(added),errors=errors,without_art=missing),ensure_ascii=False,indent=2))
print(json.dumps(dict(added=len(added),errors=errors,without_art=missing),ensure_ascii=False),flush=True)
