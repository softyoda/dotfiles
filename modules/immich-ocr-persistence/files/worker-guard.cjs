// Hold background jobs until the NAS and this image agree; acknowledge update pauses.
const fs=require('node:fs'), {spawn}=require('node:child_process');
const dir='/usr/src/app/upload/.immich-maintenance';
let child=null, stopping=false;
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
function request(){try{return JSON.parse(fs.readFileSync(dir+'/request.json','utf8'))}catch{return null}}
async function stop(){
  if(!child)return;
  const p=child;
  // start.sh may spawn several processes; terminate its entire process group.
  try{process.kill(-p.pid,'SIGTERM')}catch{}
  await Promise.race([new Promise(r=>p.once('exit',r)),sleep(30000)]);
  if(child===p){try{process.kill(-p.pid,'SIGKILL')}catch{};child=null}
}
async function main(){
  for(;;){
    const req=request();
    if(req?.phase==='pending'){
      await stop();
      fs.mkdirSync(dir,{recursive:true});
      fs.writeFileSync(dir+'/ack.json',JSON.stringify({token:req.token,at:Date.now()}));
    } else if(!child&&!stopping){
      try{
        const r=await fetch(process.env.IMMICH_SERVER_URL+'/api/server/version',{signal:AbortSignal.timeout(5000)});
        if(!r.ok)throw Error('version unavailable');
        const v=await r.json(),version='v'+v.major+'.'+v.minor+'.'+v.patch;
        if(version===process.env.IMMICH_WORKER_EXPECTED_VERSION){
          child=spawn('start.sh',[],{stdio:'inherit',detached:true});
          const p=child;p.once('exit',()=>{if(child===p)child=null});
          console.log('Worker autorisé en '+version);
        }
      }catch{} // Fail closed while the NAS is unavailable.
    }
    if(stopping)return;
    await sleep(2000);
  }
}
for(const sig of ['SIGTERM','SIGINT'])process.on(sig,async()=>{stopping=true;await stop();process.exit(0)});
main().catch(e=>{console.error(e);process.exit(1)});
