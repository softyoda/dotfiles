from pathlib import Path
import json,os,shutil,hashlib,re,datetime,collections,copy,xml.etree.ElementTree as E
HERE=Path.cwd();H=Path.home();BASE=Path(os.environ['ROMS_NAS_DIR']).parent;DEST=BASE/'retro-roms-best-set';RA=H/'.config/retroarch';ES=H/'ES-DE'
plan=json.loads((HERE/'incoming-plan.json').read_text());rows=plan['keep'];reject=plan['reject'];replacement=plan['replacements'];stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S');Q=BASE/('tri-sauvegarde-'+stamp);backup=H/'.local/share/emulation-backups'/('import-'+stamp)
for p in Path('/proc').glob('[0-9]*/comm'):
 try:assert p.read_text().strip() not in ['retroarch','es-de','ES-DE'],'Frontend is running; cannot safely replace its lists'
 except FileNotFoundError:pass
Q.mkdir();backup.mkdir(parents=True);shutil.copytree(ES/'gamelists',backup/'gamelists');shutil.copytree(RA/'playlists',backup/'playlists');shutil.copytree(ES/'collections',backup/'collections');shutil.copy2(ES/'custom_systems/es_systems.xml',backup/'es_systems.xml');shutil.copy2(HERE/'incoming-plan.json',Q/'plan.json')
state={'quarantine':str(Q),'backup':str(backup),'phase':'moving','moved':0,'copied':0};(HERE/'incoming-apply-state.json').write_text(json.dumps(state))
journal=(Q/'operations.jsonl').open('a')
def log(**kw):journal.write(json.dumps(kw,ensure_ascii=False)+'\n');journal.flush()
def move(src,dst):
 src=Path(src);dst=Path(dst);assert src.is_file() or src.is_dir(),src;assert not dst.exists(),dst;dst.parent.mkdir(parents=True,exist_ok=True);os.rename(src,dst);log(action='rename',src=str(src),dst=str(dst));state['moved']+=1
# Remove only losing existing ROMs, keeping them recoverable on the same NAS.
for r in reject:
 if r.get('existing'):
  p=Path(r['source']);move(p,Q/'previous-library'/p.relative_to(DEST))
for n,r in enumerate(rows):
 p=Path(r['target'])
 if r.get('existing'):assert p.exists();continue
 p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists(),p
 if r['stage']:
  src=Path(r['stage']);tmp=p.with_name(p.name+'.importing');shutil.copyfile(src,tmp)
  with tmp.open('rb') as f:got='sha256:'+hashlib.file_digest(f,'sha256').hexdigest()
  assert got==r['identity'],p;os.rename(tmp,p);log(action='verified_extract',src=r['source'],member=r['member'],dst=str(p),hash=got);state['copied']+=1
 else:move(r['source'],p)
 if n%250==0:print('Installed',n,'/',len(rows),flush=True)
# Store source media independently from the rollback/quarantine folder.
media_roots={}
for group in (BASE/'tmp_dl').iterdir():
 if not group.is_dir():continue
 for child in list(group.iterdir()):
  if child.is_dir() and child.name.lower() in ['images','videos','media','manuals','bezels','marquees']:
   target=DEST/'.media-imports'/group.name/child.name;move(child,target);media_roots[str(child)]=str(target)
def media_path(s,root):
 p=Path(root)/s.removeprefix('./')
 for old,new in media_roots.items():
  if p.is_relative_to(old):return Path(new)/p.relative_to(old)
 return p
# Preserve old M3U files when all discs survive, otherwise rebuild only from chosen discs.
launch=[];rowbytarget={r['target']:r for r in rows};represented=set();m3ureplacement={}
folders={r['folder'] for r in rows}
for folder in folders:
 for p in (DEST/folder).rglob('*.m3u'):
  refs=[str((p.parent/l.strip()).resolve()) for l in p.read_text(encoding='utf-8-sig').splitlines() if l.strip() and not l.startswith('#')]
  if refs and all(x in rowbytarget for x in refs):
   r=copy.deepcopy(rowbytarget[refs[0]]);r['target']=str(p);r['name']=p.name;r['discs']=refs;launch.append(r);represented.update(refs)
  elif any(not Path(x).exists() for x in refs):
   candidate=next((replacement[x] for x in refs if x in replacement),None)
   if candidate:m3ureplacement[str(p)]=candidate
   move(p,Q/'previous-library'/p.relative_to(DEST))
bykey=collections.defaultdict(list)
for r in rows:
 if r['target'] not in represented:bykey[r['key']].append(r)
for key,rs in bykey.items():
 if len(rs)>1 and all(re.search(r'(?:disc|disk|cd)[ _-]*\d+',r['name'],re.I) for r in rs):
  rs.sort(key=lambda r:int(re.search(r'(?:disc|disk|cd)[ _-]*(\d+)',r['name'],re.I)[1]));base=re.sub(r'\s*\((?:Disc|Disk|CD)\s*\d+\)','',Path(rs[0]['name']).stem,flags=re.I);base=re.sub(r'\s*(?:Disc|Disk|CD)[ _-]*\d+(?:\s*of\s*\d+)?','',base,flags=re.I)
  p=Path(rs[0]['target']).with_name(base+'.m3u');text=''.join(os.path.relpath(r['target'],p.parent)+'\n' for r in rs)
  if p.exists():assert p.read_text()==text
  else:p.write_text(text);log(action='create_m3u',dst=str(p))
  r=copy.deepcopy(rs[0]);r['target']=str(p);r['name']=p.name;r['discs']=[q['target'] for q in rs];launch.append(r)
 else:launch.extend(rs)
replacement.update(m3ureplacement)
for r in launch:
 for d in r.get('discs',[]):
  for old,new in list(replacement.items()):
   if new==d:replacement[old]=r['target']
# Complete each system's native metadata and RetroArch playlist.
configs={
'nes':('Nintendo - NES','Nintendo - Nintendo Entertainment System','mesen','Mesen'),
'snes':('Nintendo - Super Nintendo','Nintendo - Super Nintendo Entertainment System','snes9x','Snes9x'),
'gb':('Nintendo - Game Boy','Nintendo - Game Boy','gambatte','Gambatte'),
'gbc':('Nintendo - Game Boy Color','Nintendo - Game Boy Color','gambatte','Gambatte'),
'mastersystem':('Sega - Master System','Sega - Master System - Mark III','genesis_plus_gx','Genesis Plus GX'),
'gamegear':('Sega - Game Gear','Sega - Game Gear','genesis_plus_gx','Genesis Plus GX'),
'saturn':('Sega - Saturn','Sega - Saturn','kronos','Kronos'),
'psx':('Sony - PlayStation','Sony - PlayStation','swanstation','SwanStation'),
'atari5200':('Atari - 5200','Atari - 5200','a5200','a5200'),
'colecovision':('Coleco - ColecoVision','Coleco - ColecoVision','gearcoleco','Gearcoleco'),
'gamate':('Bit Corporation - Gamate','Bit Corporation - Gamate','mame','MAME'),
'pv1000':('Casio - PV-1000','Casio - PV-1000','mame','MAME'),
'universal':('Arcade - Universal','MAME','mame','MAME')}
systems=E.parse(ES/'custom_systems/es_systems.xml');groups=collections.defaultdict(list)
for r in launch:groups[r['sid']].append(r)
def put(g,k,v):
 n=g.find(k)
 if n is None:n=E.SubElement(g,k)
 n.text=v

def xmlwrite(tree,p):
 p.parent.mkdir(parents=True,exist_ok=True);E.indent(tree);tmp=p.with_suffix('.import-tmp');tree.write(tmp,encoding='utf-8',xml_declaration=True);tmp.replace(p)
def link(src,dst):
 if not src.is_file():return False
 dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists() or dst.is_symlink():return True
 dst.symlink_to(src);return True
coverage=collections.Counter();counts={};missing_cores=[]
for sid,rs in groups.items():
 title,db,core,corename=configs[sid];corepath=RA/'cores'/(core+'_libretro.so');root=DEST/rs[0]['folder'];node=next((s for s in systems.findall('system') if s.findtext('name')==sid),None)
 if node is None:node=E.SubElement(systems.getroot(),'system');put(node,'name',sid);put(node,'fullname',title);put(node,'platform','arcade' if sid=='universal' else sid);put(node,'theme','arcade' if sid=='universal' else sid)
 put(node,'path',str(root));extensions={Path(r['target']).suffix for r in rs}|{Path(d).suffix for r in rs for d in r.get('discs',[])};put(node,'extension',' '.join(sorted(extensions|{e.upper() for e in extensions})))
 put(node,'command',f'/usr/bin/retroarch --appendconfig "{ES}/settings/retroarch-session.cfg" -f -L {corepath} %ROM%')
 if not corepath.exists():missing_cores.append(sid)
 gp=ES/'gamelists'/sid/'gamelist.xml';old={}
 if gp.exists():
  for g in E.parse(gp).findall('game'):
   path=g.findtext('path','');old[str(root/path.removeprefix('./')) if not path.startswith('/') else path]=g
 reverse=collections.defaultdict(list)
 for a,z in replacement.items():reverse[z].append(a)
 gl=E.Element('gameList');items=[]
 for r in sorted(rs,key=lambda r:r['name'].casefold()):
  p=Path(r['target']);rel=p.relative_to(root);m=r.get('metadata',{});oldg=old.get(str(p));oldg=oldg if oldg is not None else next((old[a] for a in reverse[str(p)] if a in old),None)
  g=copy.deepcopy(oldg) if oldg is not None else E.Element('game');put(g,'path','./'+str(rel))
  label=p.stem
  if g.findtext('name') is None:put(g,'name',m.get('name') or re.sub(r'\([^)]*\)|\[[^]]*\]','',label).strip())
  for field in ['desc','developer','publisher','genre','players','releasedate','rating']:
   if m.get(field):put(g,field,m[field]);coverage['metadata_fields']+=1
  for field,kind in [('image','miximages'),('thumbnail','covers'),('marquee','marquees'),('video','videos'),('fanart','fanart')]:
   if m.get(field):
    src=media_path(m[field],m['_root']);dst=ES/'downloaded_media'/sid/kind/rel.with_suffix(src.suffix)
    if link(src,dst):coverage[kind]+=1
    if field in ['thumbnail','image']:
     clean=re.sub(r'[&*/:`<>?\\|]','_',label);link(src,RA/'thumbnails'/title/('Named_Boxarts' if field=='thumbnail' else 'Named_Snaps')/(clean+src.suffix))
  # Transfer previously downloaded media for a replacement edition without deleting originals.
  for oldpath in reverse[str(p)]:
   oldrel=Path(oldpath).relative_to(root)
   for kinddir in (ES/'downloaded_media'/sid).glob('*'):
    if kinddir.is_dir():
     for ext in ['.png','.jpg','.mp4']:
      src=kinddir/oldrel.with_suffix(ext)
      if src.is_file():link(src,kinddir/rel.with_suffix(ext))
  gl.append(g);items.append(dict(path=str(p),label=label,core_path=str(corepath),core_name=corename,crc32='DETECT',db_name=db+'.lpl'))
  for d in r.get('discs',[]):
   hidden=E.SubElement(gl,'game');put(hidden,'path','./'+str(Path(d).relative_to(root)));put(hidden,'name',Path(d).stem);put(hidden,'hidden','true')
 gp.parent.mkdir(parents=True,exist_ok=True);xmlwrite(E.ElementTree(gl),gp)
 lp=RA/'playlists'/(title+'.lpl');data=json.loads(lp.read_text()) if lp.exists() else {'version':'1.5','label_display_mode':0,'right_thumbnail_mode':0,'left_thumbnail_mode':0,'sort_mode':1}
 data.update(items=items,default_core_path=str(corepath),default_core_name=corename,scan_content_dir=str(root),scan_file_exts=' '.join(e.lstrip('.') for e in extensions));lp.write_text(json.dumps(data,ensure_ascii=False,indent=2));counts[sid]=len(items)
xmlwrite(systems,ES/'custom_systems/es_systems.xml')
# Keep favourites, play history and custom collections pointing at the chosen editions.
for p in (ES/'collections').glob('*.cfg'):
 lines=p.read_text().splitlines();new=list(dict.fromkeys(replacement.get(l,l) for l in lines));p.write_text('\n'.join(new)+'\n')
for p in (RA/'playlists/builtin').glob('*.lpl'):
 data=json.loads(p.read_text());seen=set();items=[]
 for i in data.get('items',[]):
  if i.get('path') in replacement:i['path']=replacement[i['path']];i['label']=Path(i['path']).stem
  if i.get('path') not in seen:items.append(i);seen.add(i.get('path'))
 data['items']=items;p.write_text(json.dumps(data,ensure_ascii=False,indent=2))
# Preserve per-game controller/multitap presets when selecting another edition.
for old,new in replacement.items():
 a=Path(old).stem;z=Path(new).stem
 for p in list((RA/'config').glob('**/'+a.replace('[','[[]')+'.rmp'))+list((RA/'config').glob('*/'+a.replace('[','[[]')+'.opt')):
  dest=p.with_name(z+p.suffix)
  if not dest.exists():shutil.copy2(p,dest)
# Remaining source archives/losing raw files and ancillary files are archived outside scanned roots.
for src in [BASE/'tmp_dl',next(BASE.glob('[[]PSX-PSP]*'))]:
 for child in list(src.iterdir()):move(child,Q/'sources'/src.name/child.name)
state.update(phase='complete',counts=counts,media=dict(coverage),missing_cores=missing_cores,selected_roms=len(rows),launch_entries=len(launch),rejected_variants=len(reject),invalid_files=json.loads((HERE/'incoming-staged.json').read_text())['errors']);(HERE/'incoming-apply-state.json').write_text(json.dumps(state,indent=2));(Q/'result.json').write_text(json.dumps(state,indent=2));(HERE/'incoming-launch.json').write_text(json.dumps(launch,ensure_ascii=False,indent=2));print(json.dumps(state,indent=2),flush=True)
