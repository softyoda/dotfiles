#!/usr/bin/env python3
"""Connect shared images and NAS game paths to both frontends, preserving metadata."""
import collections
import copy
import datetime
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import xml.etree.ElementTree as ET

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('art',HERE/'game-artwork.py');art=importlib.util.module_from_spec(spec);spec.loader.exec_module(art)
RA=art.RA;ES=Path.home()/'ES-DE';NAS=art.NAS

def write(path,text):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+'.artwork-tmp');tmp.write_text(text,encoding='utf-8');tmp.replace(path)

def xmltext(root):
    ET.indent(root)
    return ET.tostring(root,encoding='unicode',xml_declaration=True)+'\n'

def settext(node,key,value):
    child=node.find(key)
    if child is None:child=ET.SubElement(node,key)
    child.text=value

def main():
    for comm in Path('/proc').glob('[0-9]*/comm'):
        try:name=comm.read_text().strip()
        except OSError:continue
        assert name not in ['retroarch','es-de','ES-DE'], 'Close frontend before applying: '+name
    items=json.loads((HERE/'artwork-plan.json').read_text())
    groups=collections.defaultdict(list)
    for item in items:groups[item['system']].append(item)
    stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    backup=Path.home()/('artwork-settings-backup-'+stamp);backup.mkdir()
    for src,name in [(RA/'retroarch.cfg','retroarch.cfg'),(ES/'custom_systems/es_systems.xml','es_systems.xml'),(ES/'settings/es_settings.xml','es_settings.xml')]:shutil.copy2(src,backup/name)
    shutil.copytree(ES/'gamelists',backup/'gamelists')
    systems=ET.parse(ES/'custom_systems/es_systems.xml').getroot()
    counts=collections.Counter();missing=[];links=[];hidden=0
    for system,entries in groups.items():
        sid=entries[0]['sid'];root=NAS/system
        node=next((n for n in systems.findall('system') if n.findtext('name')==sid),None)
        if node is None:
            node=ET.SubElement(systems,'system')
            settext(node,'name',sid);settext(node,'fullname',Path(entries[0]['playlist']).stem)
            settext(node,'platform',sid);settext(node,'theme',sid)
            core=entries[0]['core_path']
            command='/usr/bin/retroarch -f '+('-L '+core+' ' if core!='DETECT' else '')+'%ROM%'
            settext(node,'command',command)
        oldroot=Path(node.findtext('path',str(root))).expanduser()
        settext(node,'path',str(root))
        exts={Path(i['path']).suffix for i in entries}|{p.suffix for p in root.iterdir() if p.suffix in {'.chd','.rvz'}}
        settext(node,'extension',' '.join(sorted(exts|{e.upper() for e in exts})))
        glpath=ES/'gamelists'/sid/'gamelist.xml'
        oldgames={}
        if glpath.exists():
            for g in ET.parse(glpath).getroot().findall('game'):
                oldgames[Path(g.findtext('path','')).name]=g
        gamelist=ET.Element('gameList');paths=set()
        for item in entries:
            rom=Path(item['path']);assert rom.is_file()
            paths.add(rom)
            game=copy.deepcopy(oldgames[rom.name]) if rom.name in oldgames else ET.Element('game')
            settext(game,'path','./'+str(rom.relative_to(root)))
            settext(game,'name',item['search'] if system.startswith(('Arcade','SNK - NEO GEO')) else item['label'])
            if game.find('hidden') is not None:game.remove(game.find('hidden'))
            gamelist.append(game)
            present=[]
            for kind,a in item['art'].items():
                src=Path(a['dest'])
                if not src.is_file():continue
                target=ES/'downloaded_media'/sid/art.TYPES[kind]/rom.relative_to(root).with_suffix('.png')
                target.parent.mkdir(parents=True,exist_ok=True)
                if target.is_symlink():
                    if target.resolve()!=src.resolve():
                        shutil.copy2(target,backup/(sid+'-'+art.TYPES[kind]+'-'+target.name))
                        target.unlink();target.symlink_to(src)
                elif not target.exists():target.symlink_to(src)
                counts[kind]+=1;present.append(kind);links.append(str(target))
            if not present:missing.append(dict(system=system,label=item['label']))
        # The media remain on the NAS, while redundant disc entries are hidden.
        for p in sorted(root.iterdir()):
            if p.is_file() and p.suffix in exts and p not in paths:
                game=ET.SubElement(gamelist,'game');settext(game,'path','./'+p.name);settext(game,'name',p.stem);settext(game,'hidden','true');hidden+=1
        write(glpath,xmltext(gamelist))
        # RetroArch aliases support the existing shortened playlist names.
        dbroot=RA/'thumbnails'/entries[0]['db'];alias=RA/'thumbnails'/Path(entries[0]['playlist']).stem
        if alias!=dbroot and not alias.exists() and not alias.is_symlink():alias.symlink_to(dbroot,target_is_directory=True)
    write(ES/'custom_systems/es_systems.xml',xmltext(systems))
    settings=ES/'settings/es_settings.xml';s=settings.read_text()
    s=re.sub(r'(<bool name="ShowHiddenGames" value=")[^"]*',r'\g<1>false',s)
    write(settings,s)
    cfg=RA/'retroarch.cfg';s=cfg.read_text()
    for key,value in {'menu_thumbnails':'2','menu_left_thumbnails':'1'}.items():
        line=f'{key} = "{value}"'
        if re.search(r'^'+key+r'\s*=.*$',s,re.M):s=re.sub(r'^'+key+r'\s*=.*$',lambda _:line,s,flags=re.M)
        else:s+='\n'+line+'\n'
    write(cfg,s)
    # The installed grid theme normally omits screenshots as a fallback.
    theme=ES/'themes/adroit-es-de/theme_grid.xml'
    if theme.exists():
        s=theme.read_text()
        old='<imageType>cover,marquee,titlescreen</imageType>'
        if old in s:
            shutil.copy2(theme,backup/'theme_grid.xml')
            write(theme,s.replace(old,'<imageType>cover,marquee,titlescreen,screenshot</imageType>'))
    for link in links:assert Path(link).is_file(),link
    report=dict(games=len(items),systems=len(groups),shared_images=sum(counts.values()),types=dict(counts),without_art=missing,hidden_disc_or_bios_entries=hidden,backup=str(backup),rom_bytes_copied=0)
    (HERE/'artwork-installation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
