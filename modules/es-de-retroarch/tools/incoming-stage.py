import os
from pathlib import Path
import json,hashlib,zipfile,subprocess,concurrent.futures,struct,collections,xml.etree.ElementTree as E
BASE=Path(os.environ['ROMS_NAS_DIR']).parent;DEST=BASE/'retro-roms-best-set';STAGE=Path('/tmp/retro-import-stage');STAGE.mkdir(exist_ok=True)
MAP={'mastersystem':('mastersystem','Sega - Master System'),'gb':('gb','Nintendo - Game Boy'),'nes':('nes','Nintendo - NES'),'snes':('snes','Nintendo - SNES'),'saturn':('saturn','Sega - Saturn'),'GG French Best Set':('gamegear','Sega - Game Gear'),'atari5200':('atari5200','Atari - 5200'),'RA - Colecovision':('colecovision','Coleco - ColecoVision'),'gamate':('gamate','Bit Corporation - Gamate'),'pv1000':('pv1000','Casio - PV-1000'),'universal':('universal','Arcade - Universal'),'Hackset-NES-YGG':('nes','Nintendo - NES')}
EXT={'.nes','.fds','.sfc','.smc','.gb','.gbc','.sms','.gg','.a52','.col','.bin','.rom','.chd','.pbp','.zip'}
rows=[];errors=[]
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def ident(p):
 if p.suffix.lower()=='.chd':
  with p.open('rb') as f:h=f.read(124)
  if h[:8]!=b'MComprHD':raise ValueError('Invalid CHD')
  ver=struct.unpack('>I',h[12:16])[0]
  # CHD v5 SHA-1 covers logical content plus metadata. Excludes compression representation.
  if ver==5:return 'chd-sha1:'+h[84:104].hex()
  return 'file:'+sha(p)
 return 'sha256:'+sha(p)
def process(pair):
 idx,item=pair;p=Path(item['path']);group=item['group'];sid,folder=MAP.get(group,('psx','Sony - PS1'));out=[]
 if p.suffix.lower() not in {'.zip','.7z','.chd','.pbp'}:return []
 if group=='Hackset-NES-YGG' and 'NES Roms' not in p.parts:return []
 def row(q,member=None):
  return dict(source=str(p),stage=str(q) if q!=p else None,member=member,name=q.name,sid=sid,folder=folder,group=group,size=q.stat().st_size,identity=ident(q),hackpack=group=='Hackset-NES-YGG')
 if p.suffix.lower()=='.zip' and sid!='universal':
  with zipfile.ZipFile(p) as z:
   for i in z.infolist():
    if i.is_dir() or Path(i.filename).suffix.lower() not in EXT- {'.zip','.chd','.pbp'}:continue
    target=STAGE/str(idx)/Path(i.filename).name;target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():raise ValueError('Repeated filename in archive')
    target.write_bytes(z.read(i));out.append(row(target,i.filename))
 elif p.suffix.lower()=='.7z':
  target=STAGE/str(idx);target.mkdir(exist_ok=True)
  r=subprocess.run(['7z','x','-y','-bd','-o'+str(target),str(p)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
  if r.returncode:raise ValueError(r.stdout.decode(errors='replace')[-600:])
  for q in target.rglob('*'):
   if q.is_file() and q.suffix.lower() in EXT- {'.zip','.chd','.pbp'}:out.append(row(q,str(q.relative_to(target))))
 elif p.suffix.lower()=='.pbp':
  with p.open('rb') as f:
   hdr=f.read(40);a=struct.unpack('<10I',hdr);assert hdr[:4]==b'\x00PBP';f.seek(a[9]);tag=f.read(12);f.seek(a[2]);sfo=f.read(a[3]-a[2])
  assert tag.startswith((b'PSISOIMG',b'PSTITLEIMG')),tag
  r=dict(source=str(p),stage=None,member=None,name=p.name,sid=sid,folder=folder,group=group,size=p.stat().st_size,identity='pbp-name-size:'+p.stem+':'+str(p.stat().st_size),hackpack=False)
  if sfo[:4]==b'\x00PSF':
   _,_,ko,do,count=struct.unpack('<5I',sfo[:20]);fields={}
   for n in range(count):
    key,fmt,length,maxlen,off=struct.unpack('<HHIII',sfo[20+n*16:36+n*16]);k=sfo[ko+key:].split(b'\0')[0].decode();v=sfo[do+off:do+off+length];fields[k]=v.rstrip(b'\0').decode(errors='replace') if fmt==0x204 else v.hex()
   r['pbp_info']=fields
  out.append(r)
 else:out.append(row(p))
 return out
items=json.load(open('incoming-inventory.json'))
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
 futures={pool.submit(process,pair):pair[1]['path'] for pair in enumerate(items) if pair[1]['ext'] in {'.zip','.7z','.chd','.pbp'}}
 for n,f in enumerate(concurrent.futures.as_completed(futures),1):
  try:rows+=f.result()
  except Exception as e:errors.append({'path':futures[f],'error':str(e)})
  if n%300==0:print('Processed',n,'archives/files;',len(rows),'ROMs;',len(errors),'errors',flush=True)
Path('incoming-staged.json').write_text(json.dumps({'games':rows,'errors':errors},indent=2));print('STAGED',len(rows),dict(collections.Counter(r['sid'] for r in rows)),'ERRORS',errors[:10],flush=True)
existing=[]
for sid,folder in set(MAP.values())|{('psx','Sony - PS1')}:
 root=DEST/folder
 if not root.exists():continue
 for p in root.rglob('*'):
  if p.is_file() and p.suffix.lower() in EXT- {'.zip','.pbp'}:
   existing.append(dict(source=str(p),stage=None,name=p.name,sid=sid,folder=folder,size=p.stat().st_size,identity=ident(p),existing=True))
Path('incoming-existing.json').write_text(json.dumps(existing,indent=2));print('EXISTING',len(existing),flush=True)
