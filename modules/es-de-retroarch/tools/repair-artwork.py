import importlib.util,json,pathlib,urllib.parse
s=importlib.util.spec_from_file_location('a','game-artwork.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
p=pathlib.Path('artwork-plan.json');items=json.loads(p.read_text());fixed=[]
for i in items[:1800]:
 for kind,a in i['art'].items():
  if kind!='Named_Boxarts' or not (i['label'].startswith(('Mega Man Battle Network 3','Mega Man Battle Network 4','Mega Man Battle Network 6','Sonic Rush Adventure'))):continue
  if 'Virtual Console' in i['label']:continue
  assert kind=='Named_Boxarts'
  name=a['matched'].replace('(USA)','(Europe)').replace('3 - Blue Version','3 - Blue').replace('3 - White Version','3 - White')
  if 'Battle Network 6' in name:name=name.replace('Mega Man','Megaman -').replace('(Europe)','(USA)')
  b=dict(a,url=m.HOST+urllib.parse.quote(i['source'],safe='')+'/'+kind+'/'+urllib.parse.quote(name,safe=''),matched=name,mode='same_game_europe_replaces_invalid_source')
  result=m.download_one(b);assert result[0]!='missing',b
  a.update(b);fixed.append(i['label']);p.write_text(json.dumps(items,ensure_ascii=False,indent=2));print('Repaired',i['label'],flush=True)
p.write_text(json.dumps(items,ensure_ascii=False,indent=2))
pathlib.Path('artwork-repairs.json').write_text(json.dumps(fixed,indent=2))
