import collections,importlib.util,json
from pathlib import Path
s=importlib.util.spec_from_file_location('a','game-artwork.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
items=json.load(open('artwork-plan.json'));counts=collections.Counter();bad=[];missing=[];size=0
for i in items:
 good=0
 for kind,a in i['art'].items():
  p=Path(a['dest'])
  if not m.valid(p):bad.append(dict(label=i['label'],kind=kind,**a));continue
  counts[kind]+=1;size+=p.stat().st_size;good+=1
 if not good:missing.append(i['label'])
r=dict(games=len(items),illustrated_games=len(items)-len(missing),images=sum(counts.values()),types=dict(counts),bytes=size,invalid_or_missing=bad,games_without_image=missing)
Path('artwork-audit.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print(json.dumps(r,ensure_ascii=False,indent=2))
