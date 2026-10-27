import collections,datetime,importlib.util,json,re,shutil,unicodedata,xml.etree.ElementTree as E
from pathlib import Path
HERE=Path(__file__).resolve().parent;ES=Path.home()/'ES-DE'
s=importlib.util.spec_from_file_location('art',HERE/'game-artwork.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
PLAT={'atari2600':['Atari 2600'],'nes':['Nintendo Entertainment System','Nintendo Famicom Disk System'],'snes':['Super Nintendo Entertainment System'],'n64':['Nintendo 64'],'gb':['Nintendo Game Boy'],'gbc':['Nintendo Game Boy Color'],'gba':['Nintendo Game Boy Advance'],'nds':['Nintendo DS'],'gc':['Nintendo GameCube'],'mastersystem':['Sega Master System'],'megadrive':['Sega Genesis'],'gamegear':['Sega Game Gear'],'segacd':['Sega CD'],'saturn':['Sega Saturn'],'dreamcast':['Sega Dreamcast'],'psx':['Sony Playstation'],'psp':['Sony PSP','Sony PSP Minis'],'pcengine':['NEC TurboGrafx-16','PC Engine SuperGrafx'],'pcenginecd':['NEC TurboGrafx-CD'],'arcade':['Arcade'],'neogeo':['SNK Neo Geo AES','SNK Neo Geo MVS','Arcade']}
items=json.load(open(HERE/'artwork-plan.json'));db=json.load(open('/tmp/launchbox-games.json'));games={g['DatabaseID']:g for g in db['games']};idx=collections.defaultdict(set)
def norm(s):
 s=re.sub(r', (The|A|An) - ', ' - ', s)
 return a.base(s.replace('&','and'))
for g in games.values():idx[g['Platform'],norm(g['Name'])].add(g['DatabaseID'])
for alt in db['alts']:
 g=games.get(alt['DatabaseID'])
 if g:idx[g['Platform'],norm(alt['AlternateName'])].add(g['DatabaseID'])
aliases=json.load(open(HERE/'artwork-aliases.json'));chosen=[];unmatched=[]
for i in items:
 queries=([i['search']] if i['sid']=='arcade' else [i['search'],i['label']])+[x[2] for x in aliases if x[0]==i['system'] and i['label'].startswith(x[1])]
 queries += [v['matched'][:-4] for v in i['art'].values()]
 queries += [part.strip() for q in list(queries) if '~' in q for part in q.split('~')]
 ids=set()
 for plat in PLAT[i['sid']]:
  for q in queries:
   ids=idx.get((plat,norm(q)),set())
   released={gid for gid in ids if games[gid].get('ReleaseType')=='Released'}
   if released:ids=released
   exact={gid for gid in ids if norm(games[gid]['Name'])==norm(q)}
   if exact:ids=exact
   if len(ids)>1 and len({norm(games[gid]['Name']) for gid in ids})==1:
    best=max(ids,key=lambda gid:(int(games[gid].get('CommunityRatingCount','0')), -len(games[gid]['Name'])))
    ids={best}
   if len(ids)==1:break
  if len(ids)==1:break
 manual={'s1945iii':'2463','cyvern':'34297','fantzn2':'459124','gunforc2':'31633','offroad':'37363','parodius':'38529','robotron':'31219','rohgau':'39082','truxton2':'29094','wbmlb':'8756','alpham2':'10036','Donald Duck - Quack Attack (Europe) (En,Fr,De,Es,It)':'20732','Legend of Heroes, The - Trails in the Sky (USA)':'13218'}
 if len(ids)!=1 and i['label'] in manual:ids={manual[i['label']]}
 if len(ids)!=1:unmatched.append(dict(sid=i['sid'],label=i['label'],path=i['path'],search=i['search']));continue
 gid=next(iter(ids));chosen.append(dict(sid=i['sid'],path=i['path'],label=i['label'],id=gid,metadata=games[gid]))
(HERE/'bulk-metadata-plan.json').write_text(json.dumps(chosen,ensure_ascii=False,indent=2));(HERE/'bulk-metadata-unmatched.json').write_text(json.dumps(unmatched,ensure_ascii=False,indent=2))
print(json.dumps(dict(matched=len(chosen),unmatched=len(unmatched))))
if '--apply' not in __import__('sys').argv:raise SystemExit
for c in Path('/proc').glob('[0-9]*/comm'):
 try:assert c.read_text().strip() not in ['es-de','ES-DE'],'ES-DE must be closed'
 except FileNotFoundError:pass
backup=Path.home()/('esde-before-bulk-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));shutil.copytree(ES/'gamelists',backup/'gamelists');groups=collections.defaultdict(list)
for i in chosen:groups[i['sid']].append(i)
fields=collections.Counter();updated=0
for sid,entries in groups.items():
 p=ES/'gamelists'/sid/'gamelist.xml';t=E.parse(p);nodes={Path(g.findtext('path','')).name:g for g in t.getroot().findall('game')}
 for item in entries:
  node=nodes[Path(item['path']).name];g=item['metadata'];values={k:g.get(v,'') for k,v in {'desc':'Overview','developer':'Developer','publisher':'Publisher','genre':'Genres','players':'MaxPlayers'}.items()}
  date=g.get('ReleaseDate','');year=g.get('ReleaseYear','')
  if date:values['releasedate']=date[:10].replace('-','')+'T000000'
  elif year and len(year)==4:values['releasedate']=year+'0101T000000'
  if g.get('CommunityRating'):
   try:values['rating']=str(round(float(g['CommunityRating'])/5,4))
   except ValueError:pass
  changed=False
  for k,v in values.items():
   if not v or node.findtext(k):continue
   n=node.find(k)
   if n is None:n=E.SubElement(node,k)
   n.text=v;fields[k]+=1;changed=True
  updated+=changed
 E.indent(t);tmp=p.with_suffix('.bulk-tmp');t.write(tmp,encoding='utf-8',xml_declaration=True);tmp.replace(p)
report=dict(source='https://gamesdb.launchbox-app.com/Metadata.zip',matched=len(chosen),unmatched=len(unmatched),updated_games=updated,added_fields=dict(fields),backup=str(backup),existing_metadata_preserved=True)
(HERE/'bulk-metadata-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False))
