#!/usr/bin/env python3
"""Install NAS references and tiny metadata only; never copy game data."""
from pathlib import Path
import argparse
import datetime
import importlib.util
import json
import os
import re
import shutil

BASE = Path(os.environ['ROMS_NAS_DIR'])
RA = Path.home() / '.config/retroarch'
ROWS = [
 ('Atari - 2600','Atari - 2600','stella','Atari 2600'),
 ('Nintendo - NES','Nintendo - NES','mesen','NES'),
 ('Sega - Master System','Sega - Master System','genesis_plus_gx','Master System'),
 ('NEC - TurboGrafx-16','NEC - PC Engine','mednafen_pce_fast','PC Engine'),
 ('NEC - TurboGrafx CD','NEC - PC Engine CD','mednafen_pce_fast','PC Engine'),
 ('Nintendo - SNES','Nintendo - Super Nintendo','snes9x','SNES'),
 ('Sega - Genesis','Sega - Mega Drive','genesis_plus_gx','Mega Drive'),
 ('Sega - Sega CD','Sega - Mega-CD','genesis_plus_gx','Mega-CD'),
 ('Nintendo - Game Boy','Nintendo - Game Boy','gambatte','Game Boy'),
 ('Sega - Game Gear','Sega - Game Gear','genesis_plus_gx','Game Gear'),
 ('Nintendo - Game Boy Color','Nintendo - Game Boy Color','gambatte','Game Boy Color'),
 ('Nintendo - N64','Nintendo - Nintendo 64','mupen64plus_next','N64'),
 ('Sony - PS1','Sony - PlayStation','swanstation','PlayStation'),
 ('Sega - Saturn','Sega - Saturn','kronos','Saturn'),
 ('Nintendo - Game Boy Advance','Nintendo - Game Boy Advance','mgba','Game Boy Advance'),
 ('Nintendo - GameCube','Nintendo - GameCube','dolphin','GameCube'),
 ('Sega - Dreamcast','Sega - Dreamcast','flycast','Dreamcast'),
 ('Nintendo - DS','Nintendo - Nintendo DS','melondsds','Nintendo DS'),
 ('Sony - PSP','Sony - PSP','ppsspp','PSP'),
 ('Arcade - Mame 2003 Plus','MAME 2003-Plus','mame2003_plus',None),
 ('SNK - NEO GEO','SNK - Neo Geo',None,None),
]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--apply',action='store_true')
    args=parser.parse_args()
    spec=importlib.util.spec_from_file_location('inventory',Path(__file__).with_name('nas-roms-inventory.py'))
    inventory=importlib.util.module_from_spec(spec);spec.loader.exec_module(inventory)
    summary=json.loads((BASE/'INVENTAIRE-ROMs.json').read_text())
    assert summary['playlists']==len(ROWS)
    stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    backup=RA/('backup-nas-'+stamp)
    changes=[];presets=[]
    for system,title,core,oldfolder in ROWS:
        gen,db,exts,_=inventory.SYSTEMS[system]
        incoming=json.loads((BASE/'Playlists-RetroArch'/(db+'.lpl')).read_text())
        dest=RA/'playlists'/(title+'.lpl')
        before=dest.read_bytes() if dest.exists() else None
        existing=json.loads(before) if before else {}
        preferred=Path(existing.get('default_core_path','DETECT')).expanduser()
        if not preferred.is_file():
            preferred=RA/'cores'/f'{core}_libretro.so' if core else Path('DETECT')
        corepath='DETECT';corename='DETECT';runtime=None
        if preferred.is_file():
            corepath=str(preferred)
            info=(RA/'info'/(preferred.stem+'.info')).read_text()
            corename=re.search(r'^display_name = "(.*)"',info,re.M)[1]
            runtime=re.search(r'^corename = "(.*)"',info,re.M)[1]
            supported=set(re.search(r'^supported_extensions = "(.*)"',info,re.M)[1].split('|'))
        for item in incoming['items']:
            p=Path(item['path'])
            assert p.is_file() and p.is_relative_to(BASE),str(p)
            if corepath!='DETECT':
                assert p.suffix[1:] in supported,(corepath,p)
            item['core_path']=corepath;item['core_name']=corename
        # Keep unrelated existing entries; equivalent titles now point to the NAS.
        labels={item['label'] for item in incoming['items']}
        preserved=[item for item in existing.get('items',[]) if item.get('label') not in labels and not str(item.get('path','')).startswith(str(BASE)+'/')]
        data={**existing,**incoming}
        data.update(default_core_path=corepath,default_core_name=corename,sort_mode=1,scan_content_dir=str(BASE/system),scan_file_exts=exts,scan_search_recursively=True,scan_search_archives=False,scan_overwrite_playlist=False,items=sorted(incoming['items']+preserved,key=lambda i:i['label'].casefold()))
        changes.append((dest,before,json.dumps(data,ensure_ascii=False,indent=2)+'\n',dict(system=system,playlist=str(dest),nas_entries=len(incoming['items']),preserved_entries=len(preserved),core=corename)))
        if runtime and oldfolder:
            for suffix in ('.slangp','.cfg'):
                old=RA/'config'/runtime/(oldfolder+suffix)
                new=RA/'config'/runtime/(system+suffix)
                if old.is_file() and not new.exists() and new!=old:
                    presets.append((old,new))
    link=Path.home()/'Jeux/ROMs/NAS'
    if link.exists() or link.is_symlink():
        assert link.is_symlink() and link.resolve()==BASE.resolve(),'NAS shortcut already exists with another destination'
    if args.apply:
        backup.mkdir()
        for dest,before,after,details in changes:
            assert (dest.read_bytes() if dest.exists() else None)==before,'Playlist changed concurrently: '+str(dest)
            if before is not None:
                (backup/dest.name).write_bytes(before)
            dest.parent.mkdir(parents=True,exist_ok=True)
            tmp=dest.with_name(dest.name+'.nas-tmp')
            tmp.write_text(after)
            os.replace(tmp,dest)
        for old,new in presets:
            shutil.copy2(old,new)
        if not link.is_symlink():
            link.parent.mkdir(parents=True,exist_ok=True)
            link.symlink_to(BASE,target_is_directory=True)
    report=dict(applied=args.apply,backup=str(backup) if args.apply else None,link=str(link),rom_bytes_copied=0,playlists=[row[3] for row in changes],added_presets=[str(new) for old,new in presets])
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if args.apply:
        Path(__file__).with_name('nas-retroarch-integration.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':
    main()
