from pathlib import Path
import json,shutil,xml.etree.ElementTree as E,datetime,subprocess
home=Path.home();root=home/'ES-DE';m=json.load(open('visual-installation.json'));names=json.load(open('/tmp/core-names.json'))
if root.exists():shutil.copytree(root,home/('ES-DE-backup-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')))
for d in ['settings','custom_systems','themes','gamelists','downloaded_media']: (root/d).mkdir(parents=True,exist_ok=True)
shutil.copytree('/tmp/esde-themes/adroit-es-de-main',root/'themes/adroit-es-de',dirs_exist_ok=True)
config=E.Element('settings')
for tag,name,value in [('string','Theme','adroit-es-de'),('string','ThemeVariant','Grid'),('string','ThemeColorScheme','Animated'),('string','ThemeTransitions','slide'),('string','ApplicationLanguage','fr_FR'),('string','ROMDirectory',str(home/'Jeux/ROMs')),('string','InputControllerType','xbox'),('bool','NavigationSounds','false'),('bool','VideoAudio','false'),('string','CollectionSystemsAuto',''),('string','ThemeAspectRatio','16:9')]:E.SubElement(config,tag,name=name,value=value)
E.indent(config);E.ElementTree(config).write(root/'settings/es_settings.xml',encoding='utf-8',xml_declaration=True)
ids=['atari2600','atari5200','atari7800','atarijaguar','pcengine','nes','snes','n64','gc','wii','gb','gbc','gba','nds','n3ds','mastersystem','megadrive','segacd','sega32x','saturn','dreamcast','gamegear','ngpc','psx','ps2','psp']
systems=E.Element('systemList');media=0
for sid,row in zip(ids,m['consoles']):
 title,db,core,folder,effect=row;rom=home/'Jeux/ROMs'/folder
 system=E.SubElement(systems,'system')
 for key,val in [('name',sid),('fullname',title),('path',str(rom)),('extension',' '.join('.'+e+' .'+e.upper() for e in names[core]['extensions'].split('|'))),('command','/usr/bin/retroarch -f -L '+str(home/'.config/retroarch/cores'/f'{core}_libretro.so')+' %ROM%'),('platform',sid),('theme',sid)]:E.SubElement(system,key).text=val
 playlist=home/'.config/retroarch/playlists'/f'{title}.lpl';items=json.loads(playlist.read_text()).get('items',[])
 if not items:continue
 gameList=E.Element('gameList')
 for item in items:
  rel=Path(item['path']).relative_to(rom);game=E.SubElement(gameList,'game');E.SubElement(game,'path').text='./'+str(rel);E.SubElement(game,'name').text=item['label']
  for source,target in [('Named_Boxarts','covers'),('Named_Snaps','screenshots'),('Named_Titles','titlescreens')]:
   src=home/'.config/retroarch/thumbnails'/db/source/(item['label']+'.png')
   dst=root/'downloaded_media'/sid/target/rel.with_suffix('.png')
   if src.exists():dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);media+=1
 d=root/'gamelists'/sid;d.mkdir(exist_ok=True);E.indent(gameList);E.ElementTree(gameList).write(d/'gamelist.xml',encoding='utf-8',xml_declaration=True)
E.indent(systems);E.ElementTree(systems).write(root/'custom_systems/es_systems.xml',encoding='utf-8',xml_declaration=True)
app=next((home/'Applications').glob('ES-DE_x64*.AppImage'))
# AppImageLauncher already installed its application-menu shortcut.
print(json.dumps({'app':str(app),'systems':len(ids),'media':media,'theme':'Adroit / Animated'},ensure_ascii=False))
Path('esde-installation.json').write_text(json.dumps({'app':str(app),'root':str(root),'systems':ids,'theme':'adroit-es-de','color_scheme':'Animated','media_imported':media},indent=2))
