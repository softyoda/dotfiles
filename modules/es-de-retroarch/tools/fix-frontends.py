import os
from pathlib import Path
import shutil,datetime,re,json,subprocess,xml.etree.ElementTree as ET,base64
H=Path.home();RA=H/'.config/retroarch';ES=H/'ES-DE';X=H/'.local/share/xemu/xemu';stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S');backup=H/('.local/share/emulation-backups/'+stamp);backup.mkdir(parents=True)
def save(p):
 if p.exists():
  d=backup/p.relative_to(H);d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,d)
def cfg(p,settings):
 save(p);s=p.read_text() if p.exists() else ''
 for k,v in settings.items():
  line=f'{k} = "{v}"'
  if re.search(r'^'+re.escape(k)+r'\s*=',s,re.M):s=re.sub(r'^'+re.escape(k)+r'\s*=.*$',lambda _:line,s,flags=re.M)
  else:s+='\n'+line+'\n'
 p.write_text(s)
# Frontend-specific close behavior. Appended settings never replace the user's global config.
session=ES/'settings/retroarch-session.cfg';save(session);session.write_text('quit_on_close_content = "1"\nconfig_save_on_exit = "false"\nquit_press_twice = "false"\n')
p=ES/'custom_systems/es_systems.xml';save(p);tree=ET.parse(p);systems=tree.getroot().findall('system')
for s in systems:
 c=s.find('command')
 if c.text.startswith('/usr/bin/retroarch '): c.text=c.text.replace('/usr/bin/retroarch ',f'/usr/bin/retroarch --appendconfig "{session}" ',1)
 if s.findtext('name')=='xbox':s.find('path').text=os.environ['ROMS_NAS_DIR']+'/Xbox/xbox'
ET.indent(tree,space='  ');tree.write(p,encoding='utf-8',xml_declaration=True)
cfg(RA/'retroarch.cfg',{'quit_on_close_content':'0','xmb_theme':'6','menu_dynamic_wallpaper_enable':'true'})
# User-provided xemu system files, preserving the old disk and BIOS.
pkg=H/'Téléchargements/xemu-0.8.134-windows-x86_64';bios=X/'bios/Complex_4627v1.03.bin';save(bios);shutil.copy2(pkg/'BIOS/Complex_4627v1.03.bin',bios)
hdd=X/'xbox_hdd-package.qcow2'
if not hdd.exists():shutil.copy2(pkg/'Xbox Hard Disk Image/xbox_hdd.qcow2',hdd)
p=X/'xemu.toml';save(p);s=p.read_text();s=re.sub(r'^flashrom_path = .*$',f"flashrom_path = '{bios}'",s,flags=re.M);s=re.sub(r'^hdd_path = .*$',f"hdd_path = '{hdd}'",s,flags=re.M);s=re.sub(r'^games_dir = .*$',"games_dir = '"+os.environ['ROMS_NAS_DIR']+"/Xbox/xbox'",s,flags=re.M);p.write_text(s)
# Complete the wallpaper collection using existing community assets.
wall=RA/'assets-retrorama/wallpapers';source=Path('/tmp/retrorama/Retrorama Dynamic Wallpapers')
for title in ['MAME 2003-Plus','SNK - Neo Geo']:
 p=wall/(title+'.png');save(p);shutil.copy2(source/p.name,p)
def uri(p):return 'data:image/png;base64,'+base64.b64encode(Path(p).read_bytes()).decode()
# Native SVG layout with unmodified community illustrations.
for title,heading,art in [('NEC - PC Engine CD','NEC PC ENGINE CD',source/'NEC - PC Engine - TurboGrafx 16.png'),('Microsoft - Xbox','MICROSOFT XBOX',Path('/tmp/retrorama-xbox.png'))]:
 if title.startswith('NEC'):
  body=f'<image href="{uri(art)}" width="1920" height="1080"/>'
 else:
  body=f'<image href="{uri("/tmp/retrorama-template-base.png")}" width="1920" height="1080"/><image href="{uri(art)}" x="1140" y="390" width="700" height="630" preserveAspectRatio="xMidYMid meet"/>'
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080">{body}<rect x="960" y="0" width="960" height="149" fill="#141318"/><text x="1895" y="80" text-anchor="end" font-family="DejaVu Sans" font-weight="bold" font-size="62" fill="#f7ecd0">{heading}</text><text x="1895" y="132" text-anchor="end" font-family="DejaVu Sans" font-weight="bold" font-size="32" fill="#d6bc98">RETRORAMA · PHILL’S DOODLES</text></svg>'
 out=RA/'assets-retrorama/sources'/(title+'.svg');save(out);out.write_text(svg);target=wall/(title+'.png');save(target);subprocess.run(['rsvg-convert',str(out),'-o',str(target)],check=True)
# Use recognisable platform wordmarks from Adroit instead of coloured console silhouettes.
logos=ES/'themes/adroit-es-de/files/logos';icons=RA/'assets-retrorama/xmb/custom/png';converted=[]
for system in systems:
 title=system.findtext('fullname');sid=system.findtext('theme');src=logos/(sid+'.svg')
 if not src.exists():raise RuntimeError('Missing logo '+sid)
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256"><image href="{'data:image/svg+xml;base64,'+base64.b64encode(src.read_bytes()).decode()}" x="8" y="30" width="240" height="196" preserveAspectRatio="xMidYMid meet"/></svg>'
 tmp=Path('/tmp/console-wordmark.svg');tmp.write_text(svg);dest=icons/(title+'.png');save(dest)
 if dest.is_symlink():dest.unlink()
 subprocess.run(['rsvg-convert',str(tmp),'-o',str(dest)],check=True);converted.append(title)
# Preserve the original theme and make a selectable derivative.
theme=ES/'themes/adroit-retrorama-es-de'
if not theme.exists():shutil.copytree(ES/'themes/adroit-es-de',theme)
p=theme/'capabilities.xml';p.write_text(p.read_text().replace('<themeName>Adroit</themeName>','<themeName>Adroit · Retrorama</themeName>'))
backgrounds=theme/'files/console-backgrounds';backgrounds.mkdir(exist_ok=True)
for system in systems:
 src=wall/(system.findtext('fullname')+'.png');assert src.exists(),src
 dest=backgrounds/(system.findtext('theme')+'.png')
 if not dest.exists():dest.symlink_to(src)
for name in ['theme_grid.xml','theme_list.xml']:
 p=theme/name;s=p.read_text();s=s.replace('<backgroundjpg>./files/background.jpg</backgroundjpg>','<backgroundjpg>./files/console-backgrounds/${system.theme}.png</backgroundjpg>')
 # Keep animated shapes discreet so they do not cover the per-console artwork.
 s=re.sub(r'(<video name\s*=\s*"backgroundvideo">)',r'\1\n          <opacity>0.14</opacity>',s)
 s=s.replace('<path>${backgroundjpg}</path>','<path>${backgroundjpg}</path>\n          <color>BBBBBB</color>\n          <default>./files/background.jpg</default>')
 if name=='theme_grid.xml':
  s=s.replace('<pos>0.525 0.565</pos>','<pos>0.33 0.60</pos>').replace('<size>0.95 0.825</size>','<size>0.60 0.65</size>')
  s=s.replace('<size>0.9 0.797</size>','<size>0.60 0.64</size>')
  s=re.sub(r'<gridpos>[^<]+</gridpos>','<gridpos>0.33 0.60</gridpos>',s)
 p.write_text(s)
(theme/'LOCAL-CHANGES.md').write_text('Based on Adroit by RickAndTired and Retrorama by lipebello / Phill’s Doodles. Original theme preserved as adroit-es-de. Per-system wallpapers and discreet animated layer; console wordmarks remain from Adroit.\n')
p=ES/'settings/es_settings.xml';save(p);s=p.read_text();s=re.sub(r'(<string name="Theme" value=")[^"]*',r'\g<1>adroit-retrorama-es-de',s);p.write_text(s)
report={'backup':str(backup),'logos':converted,'wallpapers':len(systems),'xbox_rom_directory':os.environ['ROMS_NAS_DIR']+'/Xbox/xbox','esde_theme':str(theme),'esde_session_config':str(session),'xemu_bios':str(bios),'xemu_hdd':str(hdd)}
Path('frontend-fixes.json').write_text(json.dumps(report,indent=2,ensure_ascii=False));print(json.dumps(report,ensure_ascii=False,indent=2))
