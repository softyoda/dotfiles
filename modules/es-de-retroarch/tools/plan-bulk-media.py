import collections,json,zipfile,xml.etree.ElementTree as E
from pathlib import Path
p=json.load(open('bulk-metadata-plan.json'));ids={i['id'] for i in p};images=collections.defaultdict(list)
z=zipfile.ZipFile('/tmp/launchbox-metadata.zip');ctx=E.iterparse(z.open('Metadata.xml'),events=['start','end']);_,root=next(ctx)
for ev,e in ctx:
 if ev!='end':continue
 if e.tag in ['Game','GameAlternateName','GameImage']:
  if e.tag=='GameImage' and e.findtext('DatabaseID') in ids:
   images[e.findtext('DatabaseID')].append({c.tag:c.text or '' for c in e})
  root.clear()
print(collections.Counter(i['Type'] for v in images.values() for i in v))
json.dump(images,open('bulk-media-catalog.json','w'))
