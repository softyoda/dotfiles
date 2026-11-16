const fs=require('fs'),vm=require('vm'),assert=require('assert/strict'),{EventEmitter}=require('events');
const source=fs.readFileSync(require('path').join(__dirname,'files/update-nas.cjs'),'utf8').replace(/main\(\)\.catch\([\s\S]*$/,'main()');
async function scenario(mode){
 const files=new Map([['ocr-hook/config.json',JSON.stringify({server_url:'http://server',worker_ping:'http://worker/ping'})],['.env','IMMICH_VERSION=v3.4.1\n']]);
 let up=false,backup=false,paused=false,token,execs=[];
 const fakefs={readFileSync(p){if(!files.has(p))throw Error('ENOENT');return files.get(p)},
 writeFileSync(p,v){files.set(p,v);if(p.endsWith('request.tmp')){const d=JSON.parse(v);token=d.token;paused=d.phase==='pending'}},
 mkdirSync(){},renameSync(a,b){files.set(b,files.get(a));files.delete(a)},copyFileSync(a,b){files.set(b,files.get(a))},openSync(){backup=true;return 5},closeSync(){},statSync(){return{size:42}}};
 const child={
 spawnSync(cmd,args,opts){
  execs.push(args.join(' '));
  if(mode==='hook-fail' && args.includes('/opt/immich-ocr/apply.cjs'))return{status:2};
  if(args[0]==='inspect')return{status:0,stdout:JSON.stringify({State:{Health:{Status:'healthy'}},Config:{Image:'immich:v3.4.2'}})};
  if(args[0]==='exec'&&args[2]==='node'&&args[3]==='-e'){
   if(mode==='online'&&args[4].includes('ack.json'))files.set('/usr/src/app/upload/.immich-maintenance/ack.json',JSON.stringify({token}));
   let out='';vm.runInNewContext(args[4],{require:()=>fakefs,console:{log:s=>out=s}});return{status:0,stdout:out};
  }
  if(args.includes('up'))up=true;
  return{status:0,stdout:''};
 },
 spawn(){const p=new EventEmitter();process.nextTick(()=>p.emit('exit',mode==='backup-fail'?1:0));return p}
 };
 const ctx={require:n=>n==='node:fs'?fakefs:n==='node:child_process'?child:require(n),
 fetch:async url=>{
  if(url.includes('/api/server/version'))return{ok:true,json:async()=>({major:3,minor:4,patch:1})};
  if(url.includes('github'))return{ok:true,json:async()=>({tag_name:'v3.4.2',html_url:'https://example.test'})};
  return{ok:mode==='no-ack'};
 },process:{argv:[],env:{}},AbortSignal,console:{log(){},error(){},warn(){}},setTimeout:f=>queueMicrotask(f)};
 let error;try{await vm.runInNewContext(source,ctx)}catch(e){error=e}
 if(mode==='online'||mode==='offline'||mode==='hook-fail'){assert(!error,String(error));assert(up);assert(backup);assert(!paused);assert(files.get('.env').includes('v3.4.2'))}
 else{assert(error);assert(!up);assert.equal(files.get('.env'),'IMMICH_VERSION=v3.4.1\n')}
 console.log('PASS updater '+mode);
}
(async()=>{for(const m of ['online','offline','no-ack','backup-fail','hook-fail'])await scenario(m)})().catch(e=>{console.error(e);process.exitCode=1});
