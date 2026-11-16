// Invoked by Dockge's authenticated Update action, under flock.
const fs=require('node:fs'),path=require('node:path'),{spawnSync,spawn}=require('node:child_process');
const crypto=require('node:crypto');
const cfg=JSON.parse(fs.readFileSync('ocr-hook/config.json','utf8'));
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
function run(args,opts={}){
 const p=spawnSync(args[0],args.slice(1),{stdio:'inherit',...opts});
 if(p.error||p.status!==0)throw Error(args[0]+' a échoué ('+p.status+')');
 return p.stdout;
}
function read(args){return run(args,{encoding:'utf8',stdio:['ignore','pipe','inherit']}).trim()}
function execNode(code){return read(['docker','exec','immich-server','node','-e',code])}
function writeRequest(req){
 execNode('const fs=require("fs"),p="/usr/src/app/upload/.immich-maintenance";fs.mkdirSync(p,{recursive:true});fs.writeFileSync(p+"/request.tmp",'+JSON.stringify(JSON.stringify(req))+');fs.renameSync(p+"/request.tmp",p+"/request.json")');
}
async function version(){
 const r=await fetch(cfg.server_url+'/api/server/version',{signal:AbortSignal.timeout(8000)});
 if(!r.ok)throw Error('Serveur indisponible');
 const v=await r.json();return 'v'+v.major+'.'+v.minor+'.'+v.patch;
}
async function mlOnline(){
 try{const r=await fetch(cfg.worker_ping,{signal:AbortSignal.timeout(4000)});return r.ok}
 catch{return false}
}
async function backup(file){
 const fd=fs.openSync(file,'wx',0o600);
 try{
  await new Promise((resolve,reject)=>{
   const p=spawn('docker',['exec','immich-db','sh','-c','exec pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB"'],{stdio:['ignore',fd,'inherit']});
   p.on('error',reject);p.on('exit',code=>code===0?resolve():reject(Error('Sauvegarde PostgreSQL échouée')));
  });
 }finally{fs.closeSync(fd)}
 if(fs.statSync(file).size===0)throw Error('Sauvegarde vide');
}
async function main(){
 run(['docker','compose','config','--quiet']);
 const current=await version();
 if(process.argv.includes('--resume')){
  const state=JSON.parse(read(['docker','inspect','immich-server','--format','{{json .}}']));
  if(state.State.Health?.Status!=='healthy')throw Error('Serveur non sain : reprise refusée');
  writeRequest({phase:'ready',target:current});
  console.log('Reprise autorisée sur le serveur sain '+current);return;
 }
 const release=await fetch('https://api.github.com/repos/immich-app/immich/releases/latest',{headers:{'User-Agent':'immich-maintenance'},signal:AbortSignal.timeout(30000)}).then(r=>{if(!r.ok)throw Error('GitHub indisponible');return r.json()});
 const target=release.tag_name;
 if(release.draft||release.prerelease||!/^v\d+\.\d+\.\d+$/.test(target))throw Error('Version stable invalide');
 console.log('Serveur '+current+' ; cible '+target+'\n'+release.html_url);
 if(process.argv.includes('--check')){console.log('Préflight OK, aucune mise à jour lancée.');return}
 const a=target.slice(1).split('.').map(Number),b=current.slice(1).split('.').map(Number);
 const older=a.some((v,i)=>v<b[i]&&a.slice(0,i).every((x,j)=>x===b[j]));
 if(older)throw Error('Refus de rétrograder le serveur');
 if(a[0]!==b[0])throw Error('Version majeure : lire les notes et effectuer une migration explicite');
 if(current===target){
  run(['docker','exec','immich-server','node','/opt/immich-ocr/apply.cjs']);
  console.log('Déjà à jour ; OCR vérifié.');return;
 }
 const stamp=new Date().toISOString().replace(/[:.]/g,'-');
 const dc=(...args)=>run(['docker','compose',...args],{env:{...process.env,IMMICH_VERSION:target}});
 console.log('Téléchargement du serveur…');dc('pull','immich-server');
 console.log('Sauvegarde PostgreSQL…');await backup('db-backup-pre-'+target+'-'+stamp+'.sql');
 const token=crypto.randomUUID();writeRequest({phase:'pending',token,target});
 console.log('Mise en pause des workers ; attente de confirmation…');
 let acknowledged=false;
 for(let i=0;i<30;i++){
  const ack=execNode('const fs=require("fs");try{console.log(fs.readFileSync("/usr/src/app/upload/.immich-maintenance/ack.json","utf8"))}catch{console.log("{}")}');
  if(JSON.parse(ack).token===token){acknowledged=true;break}
  await sleep(2000);
 }
 if(!acknowledged){
  for(let i=0;i<3;i++){if(await mlOnline())throw Error('Worker joignable mais pause non confirmée : serveur inchangé');await sleep(1000)}
  console.log('Worker hors ligne : mise à jour du NAS seul, alignement différé au retour du PC.');
 }
 const envFile='.env',old=fs.readFileSync(envFile,'utf8');
 fs.copyFileSync(envFile,envFile+'.pre-update-'+stamp);
 const pattern=/^[ \t]*(?:export[ \t]+)?IMMICH_VERSION[ \t]*=.*$/m;
 fs.writeFileSync(envFile,pattern.test(old)?old.replace(pattern,'IMMICH_VERSION='+target):old+'\nIMMICH_VERSION='+target+'\n');
 console.log('Démarrage du nouveau serveur…');dc('up','-d','--no-deps','immich-server');
 let healthy=false;
 for(let i=0;i<90;i++){
  const d=JSON.parse(read(['docker','inspect','immich-server','--format','{{json .}}']));
  if(d.State.Health?.Status==='healthy'&&d.Config.Image.endsWith(':'+target)){healthy=true;break}
  await sleep(4000);
 }
 if(!healthy)throw Error('Serveur non sain : workers maintenus en pause, consulter les journaux');
 writeRequest({phase:'ready',token,target});
 run(['docker','exec','immich-server','node','/opt/immich-ocr/apply.cjs']);
 console.log('NAS à jour, OCR vérifié. Les workers se réalignent automatiquement quand le PC est disponible.');
}
main().catch(e=>{console.error('ÉCHEC : '+e.message);process.exitCode=1});
