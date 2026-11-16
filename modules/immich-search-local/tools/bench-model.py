import json,subprocess,time,urllib.request,statistics,sys,os
container=sys.argv[1]
def docker(*a):
 return subprocess.check_output((['docker'] if os.environ.get('BENCH_NO_SUDO') else ['sudo','-n','docker'])+list(a),text=True).strip()
def metric():
 cpu={k:int(v) for k,v in (l.split() for l in docker('exec',container,'cat','/sys/fs/cgroup/cpu.stat').splitlines())}
 mem=int(docker('exec',container,'cat','/sys/fs/cgroup/memory.current'))
 stat={k:int(v) for k,v in (l.split() for l in docker('exec',container,'cat','/sys/fs/cgroup/memory.stat').splitlines())}
 return {'cpu_us':cpu['usage_usec'],'ram_working_MiB':round((mem-stat.get('inactive_file',0))/2**20,1),'ram_cgroup_MiB':round(mem/2**20,1)}
d=json.loads(docker('inspect',container))[0]
ip=next(iter(d['NetworkSettings']['Networks'].values()))['IPAddress']
url='http://'+ip+':3003'
def encode(text):
 boundary='immich-benchmark-boundary'
 entries={'clip':{'textual':{'modelName':'ViT-B-32__openai','options':{'language':'fr'}}}}
 body=b''
 for key,value in [('entries',json.dumps(entries)),('text',text)]:
  body+=('--'+boundary+'\r\nContent-Disposition: form-data; name="'+key+'"\r\n\r\n'+value+'\r\n').encode()
 body+=('--'+boundary+'--\r\n').encode()
 req=urllib.request.Request(url+'/predict',data=body,headers={'Content-Type':'multipart/form-data; boundary='+boundary},method='POST')
 t=time.perf_counter()
 with urllib.request.urlopen(req,timeout=90) as r:
  data=json.load(r)
 embedding=data['clip']
 if isinstance(embedding,str):embedding=json.loads(embedding)
 return (time.perf_counter()-t)*1000,len(embedding)
with urllib.request.urlopen(url+'/ping',timeout=5) as r:assert r.status==200
before=metric()
cold,dim=encode('cheval métal essai de mesure')
after_cold=metric()
queries=['un cheval en métal','une sculpture dans un jardin','un chat noir','une voiture rouge','un coucher de soleil','un bateau sur la mer','une montagne enneigée','un repas en famille','une forêt en automne','un bâtiment ancien']*2
warm=[];cpu_start=metric()['cpu_us']
for q in queries:
 ms,_=encode(q);warm.append(ms)
after=metric()
t=time.monotonic();cpu_idle=after['cpu_us'];time.sleep(10);idle=metric()
print(json.dumps({'container':container,'model':'ViT-B-32__openai','dimension':dim,'samples':len(warm),
 'cold_ms':round(cold,1),'cold_cpu_ms':round((after_cold['cpu_us']-before['cpu_us'])/1000,1),
 'warm_median_ms':round(statistics.median(warm),1),'warm_p95_ms':round(sorted(warm)[int(.95*(len(warm)-1))],1),
 'warm_min_ms':round(min(warm),1),'warm_max_ms':round(max(warm),1),
 'warm_cpu_ms_per_query':round((after['cpu_us']-cpu_start)/1000/len(warm),1),
 'ram_before_MiB':before['ram_working_MiB'],'ram_loaded_MiB':after['ram_working_MiB'],
 'idle_cpu_percent_one_core':round((idle['cpu_us']-cpu_idle)/1e6/(time.monotonic()-t)*100,3),
 'memory_limit_MiB':d['HostConfig']['Memory']/2**20},ensure_ascii=False))
