// Give the customized asset graph its own URL namespace; don't alter cache/security policies.
const fs=require('node:fs'),path=require('node:path');
const INDEX_HASH='1091eb8150774530f012cf6fbaf2f8e3de7e700044b3769bead5db038186dd77';
function indexInfo(root,hash){
 const file=path.resolve(root,'../../../index.html');
 const current=fs.readFileSync(file,'utf8');
 const original=fs.existsSync(file+'.ocr-original')?fs.readFileSync(file+'.ocr-original','utf8'):current;
 if(hash(original)!==INDEX_HASH)throw Error('Index web non vérifié');
 return {file,current,original};
}
function publish(root,index,digest,writeVariants){
 const immutable=path.dirname(root),app=path.dirname(immutable);
 const name='immutable-ocr-'+digest, target=path.join(app,name);
 if(!fs.existsSync(target)){
  const tmp=target+'.tmp-'+process.pid;
  try{
   fs.cpSync(immutable,tmp,{recursive:true,filter:p=>!p.endsWith('.ocr-original')&&!p.includes('.ocr-tmp-')});
   const visit=dir=>{
    for(const entry of fs.readdirSync(dir,{withFileTypes:true})){
     const file=path.join(dir,entry.name);
     if(entry.isDirectory())visit(file);
     else if(/\.(js|css)$/.test(entry.name)){
      const before=fs.readFileSync(file,'utf8'),after=before.replaceAll('/_app/immutable/','/_app/'+name+'/');
      if(after!==before)writeVariants(file,after);
     }
    }
   };visit(tmp);
   fs.renameSync(tmp,target);
  }finally{fs.rmSync(tmp,{recursive:true,force:true})}
 }
 const html=index.original.replaceAll('/_app/immutable/','/_app/'+name+'/');
 if(html!==index.current){
  if(!fs.existsSync(index.file+'.ocr-original'))fs.writeFileSync(index.file+'.ocr-original',index.original);
  writeVariants(index.file,html);return true;
 }
 return false;
}
function restore(index,writeVariants){
 if(index && index.current!==index.original){writeVariants(index.file,index.original);return true}
 return false;
}
module.exports={indexInfo,publish,restore};
