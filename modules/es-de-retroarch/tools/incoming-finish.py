import os
from pathlib import Path
import json,shutil,re,struct,collections,xml.etree.ElementTree as E
H=Path.home();RA=H/'.config/retroarch';ES=H/'ES-DE';state=json.load(open('incoming-apply-state.json'));assert state['phase']=='complete';rows=json.load(open('incoming-launch.json'));plan=json.load(open('incoming-plan.json'));counts=collections.Counter()
def link(src,dst):
 if not src.is_file():return
 dst.parent.mkdir(parents=True,exist_ok=True)
 if not dst.exists() and not dst.is_symlink():dst.symlink_to(src);counts['links']+=1
# PBP packages contain their own original menu illustration. Use it as an icon, not a fabricated cover.
for r in rows:
 p=Path(r['target'])
 if p.suffix.lower()!='.pbp':continue
 with p.open('rb') as f:
  offsets=struct.unpack('<10I',f.read(40));f.seek(offsets[3]);png=f.read(offsets[4]-offsets[3])
 if png.startswith(b'\x89PNG'):
  dst=ES/'downloaded_media/psx/titlescreens'/(p.stem+'.png');dst.parent.mkdir(parents=True,exist_ok=True)
  if not dst.exists():dst.write_bytes(png);counts['pbp_icons']+=1
  link(dst,ES/'downloaded_media/psx/miximages'/(p.stem+'.png'))
  clean=re.sub(r'[&*/:`<>?\\|]','_',p.stem);link(dst,RA/'thumbnails/Sony - PlayStation/Named_Snaps'/(clean+'.png'))
# Existing supplied Coleco BIOS, no downloads.
src=RA/'system/Machines/COL - ColecoVision/coleco.rom';dst=RA/'system/colecovision.rom'
if src.is_file() and not dst.exists():shutil.copy2(src,dst);counts['coleco_bios_installed']=1
# Transfer RetroArch artwork aliases for regional substitutions.
for old,new in plan['replacements'].items():
 a=re.sub(r'[&*/:`<>?\\|]','_',Path(old).stem);z=re.sub(r'[&*/:`<>?\\|]','_',Path(new).stem)
 for system in (RA/'thumbnails').iterdir():
  if not system.is_dir():continue
  for kind in ['Named_Boxarts','Named_Snaps','Named_Titles']:
   for ext in ['.png','.jpg']:
    src=system/kind/(a+ext)
    if src.is_file():link(src,system/kind/(z+ext))
# Verify all playlist paths, multi-disc references and imported metadata paths.
systems={s.findtext('name'):Path(s.findtext('path')) for s in E.parse(ES/'custom_systems/es_systems.xml').findall('system')};errors=[];checked=0
for r in rows:
 p=Path(r['target']);checked+=1
 if not p.is_file():errors.append(str(p))
 if p.suffix.lower()=='.m3u':
  for line in p.read_text().splitlines():
   if line.strip() and not line.startswith('#') and not (p.parent/line).is_file():errors.append(str(p)+' -> '+line)
for sid in state['counts']:
 for g in E.parse(ES/'gamelists'/sid/'gamelist.xml').findall('game'):
  if not (systems[sid]/g.findtext('path','').removeprefix('./')).is_file():errors.append(sid+':'+g.findtext('path',''))
for p in (ES/'collections').glob('*.cfg'):
 for line in p.read_text().splitlines():
  if line and not Path(line).is_file():errors.append(str(p)+':'+line)
# Broken media links can arise when old paths move: report those specifically.
broken=[]
for sid in state['counts']:
 for p in (ES/'downloaded_media'/sid).rglob('*'):
  if p.is_symlink() and not p.exists():broken.append(str(p))
result={'postprocessing':dict(counts),'launch_paths_checked':checked,'errors':errors,'broken_media_links':broken};Path('incoming-validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));assert not errors
