import json,sys,time,statistics,subprocess,urllib.request
secret=json.load(sys.stdin)
d=json.loads(subprocess.check_output(['sudo','-n','docker','inspect','immich-server'],text=True))[0]
ip=d['NetworkSettings']['Networks']['immich_net']['IPAddress']
base='http://'+ip+':2283/api'
def api(path,body=None):
 req=urllib.request.Request(base+path,data=json.dumps(body).encode() if body is not None else None,
   headers={'x-api-key':secret['api_key'],'Content-Type':'application/json','User-Agent':'immich-benchmark'})
 t=time.perf_counter()
 with urllib.request.urlopen(req,timeout=90) as r:data=json.load(r)
 return data,round((time.perf_counter()-t)*1000,2)
queries=['statue de cheval métallique','un bateau dans une petite rivière','un chat dans un jardin','une voiture devant une maison','une montagne sous la neige','des fleurs rouges sur une table','une rue pendant la nuit','un vélo contre un mur','un paysage de campagne','un chien sur une plage']
times=[];counts=[]
for q in queries:
 d,t=api('/search/smart',{'query':q,'language':'fr','size':10,'page':1});times.append(t);counts.append(len(d['assets']['items']))
cached=[]
for q in queries:
 _,t=api('/search/smart',{'query':q,'language':'fr','size':10,'page':1});cached.append(t)
ocr,tocr=api('/search/metadata',{'ocr':'Médecine','size':10,'page':1})
people,_=api('/people?size=1&withHidden=false')
face_time=None;face_count=None
if people.get('people'):
 faces,face_time=api('/search/metadata',{'personIds':[people['people'][0]['id']],'size':10,'page':1})
 face_count=len(faces['assets']['items'])
print(json.dumps({'location':'NAS via Docker network, no WAN','worker_isolation':'must be verified by operator',
 'smart_first_ms':times[0],'smart_fresh_median_ms':statistics.median(times[1:]),'smart_fresh_samples':len(times)-1,
 'smart_cached_median_ms':statistics.median(cached),'smart_cached_samples':len(cached),
 'smart_result_counts':counts,'ocr_ms':tocr,'ocr_count':len(ocr['assets']['items']),
 'person_filter_ms':face_time,'person_filter_count':face_count},ensure_ascii=False))
