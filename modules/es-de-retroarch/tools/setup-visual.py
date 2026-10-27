#!/usr/bin/env python3
"""Install reviewed community assets and per-console organisation; no ROM downloads."""
from pathlib import Path
import json,shutil,re,datetime,subprocess
R=Path.home()/'.config/retroarch'; S=Path('/usr/share/libretro/shaders/shaders_slang'); T=Path('/tmp/retrorama'); names=json.load(open('/tmp/core-names.json'))
# title, official database/theme name, preferred installed core, source folder, display preset
rows=[
('Atari - 2600','Atari - 2600','stella','Atari 2600','crt'),
('Atari - 5200','Atari - 5200','a5200','Atari 5200','crt'),
('Atari - 7800','Atari - 7800','prosystem','Atari 7800','crt'),
('Atari - Jaguar','Atari - Jaguar','virtualjaguar','Jaguar','crt'),
('NEC - PC Engine','NEC - PC Engine - TurboGrafx 16','mednafen_pce_fast','PC Engine','crt'),
('Nintendo - NES','Nintendo - Nintendo Entertainment System','mesen','NES','crt'),
('Nintendo - Super Nintendo','Nintendo - Super Nintendo Entertainment System','snes9x','SNES','crt'),
('Nintendo - Nintendo 64','Nintendo - Nintendo 64','mupen64plus_next','N64','crt-light'),
('Nintendo - GameCube','Nintendo - GameCube','dolphin','GameCube',None),
('Nintendo - Wii','Nintendo - Wii','dolphin','Wii',None),
('Nintendo - Game Boy','Nintendo - Game Boy','gambatte','Game Boy','gb'),
('Nintendo - Game Boy Color','Nintendo - Game Boy Color','gambatte','Game Boy Color','gbc'),
('Nintendo - Game Boy Advance','Nintendo - Game Boy Advance','mgba','Game Boy Advance','gba'),
('Nintendo - Nintendo DS','Nintendo - Nintendo DS','melondsds','Nintendo DS','lcd'),
('Nintendo - Nintendo 3DS','Nintendo - Nintendo 3DS','azahar','Nintendo 3DS',None),
('Sega - Master System','Sega - Master System - Mark III','genesis_plus_gx','Master System','crt'),
('Sega - Mega Drive','Sega - Mega Drive - Genesis','genesis_plus_gx','Mega Drive','crt'),
('Sega - Mega-CD','Sega - Mega-CD - Sega CD','genesis_plus_gx','Mega-CD','crt'),
('Sega - 32X','Sega - 32X','picodrive','32X','crt'),
('Sega - Saturn','Sega - Saturn','kronos','Saturn','crt-light'),
('Sega - Dreamcast','Sega - Dreamcast','flycast','Dreamcast','crt-light'),
('Sega - Game Gear','Sega - Game Gear','genesis_plus_gx','Game Gear','gg'),
('SNK - Neo Geo Pocket','SNK - Neo Geo Pocket Color','mednafen_ngp','Neo Geo Pocket','ngpc'),
('Sony - PlayStation','Sony - PlayStation','swanstation','PlayStation','crt-light'),
('Sony - PlayStation 2','Sony - PlayStation 2','pcsx2','PlayStation 2',None),
('Sony - PSP','Sony - PlayStation Portable','ppsspp','PSP','psp'),
]
presets={'crt':'bezel/Mega_Bezel/Presets/MBZ__3__STD.slangp','crt-light':'crt/crt-easymode.slangp','gb':'handheld/console-border/gb-dmg-alt.slangp','gbc':'handheld/console-border/gbc-lcd-grid-v2.slangp','gba':'handheld/console-border/gba-lcd-grid-v2.slangp','gg':'handheld/console-border/gg.slangp','ngpc':'handheld/console-border/ngpc.slangp','psp':'handheld/console-border/psp.slangp','lcd':'handheld/lcd-grid-v2.slangp'}
assert subprocess.run(['pgrep','-x','retroarch'],stdout=subprocess.DEVNULL).returncode!=0,'Close RetroArch before installing'
assert (T/'Retrorama/font.ttf').exists()
backup=R/('backup-visual-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir()
for f in ['retroarch.cfg','config','playlists']:
 p=R/f
 if p.is_dir():shutil.copytree(p,backup/f)
 elif p.exists():shutil.copy2(p,backup/f)
assets=R/'assets-retrorama'; assets.mkdir(exist_ok=True);(assets/'xmb').mkdir(exist_ok=True)
for p in Path('/usr/share/retroarch/assets').iterdir():
 dest=assets/p.name
 if p.name!='xmb' and not dest.exists():dest.symlink_to(p,target_is_directory=p.is_dir())
for p in Path('/usr/share/retroarch/assets/xmb').iterdir():
 dest=assets/'xmb'/p.name
 if p.name!='custom' and not dest.exists():dest.symlink_to(p,target_is_directory=p.is_dir())
custom=assets/'xmb/custom';shutil.copytree(T/'Retrorama',custom,dirs_exist_ok=True)
# Supply icons introduced after the theme without replacing its artwork.
for p in Path('/usr/share/retroarch/assets/xmb/monochrome/png').glob('*.png'):
 dest=custom/'png'/p.name
 if not dest.exists():dest.symlink_to(p)
wall=assets/'wallpapers';wall.mkdir(exist_ok=True)
created=[];fallback=[]
def write(p,s):
 p.parent.mkdir(parents=True,exist_ok=True)
 if not p.exists():p.write_text(s);created.append(str(p))
def preset(p,k):write(p,'#reference "'+str(S/presets[k])+'"\n'+('HSM_INTRO_WHEN_TO_SHOW = "0"\n' if k=='crt' else ''))
# Keep the downloaded originals; install only graphics useful for this library.
for n in ['bg','Settings','Favorites','History','Import Content']:
 src=T/'Retrorama Dynamic Wallpapers'/f'{n}.png'
 if src.exists():shutil.copy2(src,wall/f'{n}.png')
for fr,en in [('Réglages','Settings'),('Favoris','Favorites'),('Historique','History'),('Importer du contenu','Import Content'),('Menu principal','bg')]:
 if (wall/f'{en}.png').exists():shutil.copy2(wall/f'{en}.png',wall/f'{fr}.png')
for title,db,core,folder,effect in rows:
 assert core in names and (R/'cores'/f'{core}_libretro.so').exists(),core
 src=T/'Retrorama Dynamic Wallpapers'/f'{db}.png'
 if src.exists():shutil.copy2(src,wall/f'{title}.png')
 else:fallback.append(title)
 for suffix in ['','-content']:
  src=custom/'png'/f'{db}{suffix}.png';dst=custom/'png'/f'{title}{suffix}.png'
  if src.exists() and src!=dst:shutil.copy2(src,dst)
 rom=Path.home()/'Jeux/ROMs'/folder;rom.mkdir(parents=True,exist_ok=True)
 corepath=str(R/'cores'/f'{core}_libretro.so')
 info=(R/'info'/f'{core}_libretro.info').read_text();display=re.search(r'^display_name = "(.*)"',info,re.M)[1]
 items=[];exts=names[core]['extensions'].split('|')
 for f in sorted(rom.rglob('*')):
  if f.is_file() and f.suffix[1:].lower() in exts:
   items.append(dict(path=str(f),label=f.stem,core_path=corepath,core_name=display,crc32='',db_name=db+'.lpl'))
 pl=dict(version='1.5',default_core_path=corepath,default_core_name=display,label_display_mode=0,right_thumbnail_mode=0,left_thumbnail_mode=0,sort_mode=1,scan_content_dir=str(rom),scan_file_exts=' '.join(exts),scan_dat_file_path='',scan_search_recursively=True,scan_search_archives=False,scan_filter_dat_content=False,scan_overwrite_playlist=False,items=items)
 write(R/'playlists'/f'{title}.lpl',json.dumps(pl,ensure_ascii=False,indent=2)+'\n')
 if effect:
  runtime=names[core]['name'];d=R/'config'/runtime
  # Folder presets disambiguate GB/GBC and Sega's multiple systems.
  preset(d/f'{folder}.slangp',effect)
  for f in items:preset(d/(Path(f['path']).parent.name+'.slangp'),effect)
  if core not in ['gambatte','genesis_plus_gx']:preset(d/f'{runtime}.slangp',effect)
  if effect in ['crt','gb','gbc','gba','gg','ngpc','psp']:
   write(d/f'{folder}.cfg','aspect_ratio_index = "24"\nvideo_scale_integer = "false"\ninput_overlay_enable = "false"\n')
# Safe generic defaults for mixed-system cores; their folder presets take priority.
preset(R/'config/Gambatte/Gambatte.slangp','lcd')
preset(R/'config/Genesis Plus GX/Genesis Plus GX.slangp','crt-light')
# Expose a small selection instead of asking the user to explore thousands of shader files.
selection=R/'shaders-selection';selection.mkdir(exist_ok=True)
for label,k in [('01 - CRT avec cadre et reflets','crt'),('02 - CRT leger','crt-light'),('03 - Game Boy avec bordure','gb'),('04 - Game Boy Color avec bordure','gbc'),('05 - Game Boy Advance avec bordure','gba'),('06 - Ecran LCD','lcd')]:preset(selection/f'{label}.slangp',k)
for p in [S/'handheld',S/'crt',S/'bezel']:
 dest=selection/p.name
 if not dest.exists():dest.symlink_to(p,target_is_directory=True)
# Community controller-reactive overlays available on demand; avoid stacking them over shader borders.
ov=R/'overlays';ov.mkdir(exist_ok=True)
for p in Path('/usr/share/libretro/overlays').iterdir():
 dest=ov/p.name
 if not dest.exists():dest.symlink_to(p,target_is_directory=p.is_dir())
updates={'menu_driver':'xmb','assets_directory':str(assets),'xmb_theme':'6','xmb_font':str(custom/'font.ttf'),'dynamic_wallpapers_directory':str(wall),'menu_dynamic_wallpaper_enable':'true','menu_wallpaper':str(wall/'bg.png'),'menu_shader_pipeline':'0','menu_wallpaper_opacity':'1.000000','xmb_alpha_factor':'100','menu_thumbnails':'0','menu_left_thumbnails':'1','menu_thumbnail_background_enable':'false','content_show_images':'false','content_show_music':'false','content_show_video':'false','content_show_netplay':'false','content_show_contentless_cores':'0','content_show_explore':'false','content_show_add_entry':'1','content_show_favorites':'true','content_show_history':'true','menu_show_advanced_settings':'false','playlist_show_inline_core_name':'0','playlist_show_sublabels':'false','video_driver':'glcore','video_shader_enable':'true','video_shader_dir':str(selection),'input_overlay_enable':'false'}
f=R/'retroarch.cfg';s=f.read_text()
for k,v in updates.items():
 line=f'{k} = "{v}"'
 if re.search(r'^'+re.escape(k)+r' = .*$',s,re.M):s=re.sub(r'^'+re.escape(k)+r' = .*$',lambda m:line,s,flags=re.M)
 else:s+='\n'+line+'\n'
f.write_text(s)
manifest=dict(backup=str(backup),created=created,consoles=rows,fallback_wallpapers=fallback,assets=str(assets),shader_presets=presets)
Path('visual-installation.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));print(json.dumps({k:manifest[k] for k in ['backup','fallback_wallpapers']},ensure_ascii=False));print(len(rows),'console sections')
