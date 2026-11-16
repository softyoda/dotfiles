// Usage: node test-compat.cjs directory-containing-original-CUVvskNU.js-and-CC5MOeVu.js
const fs=require('fs'),os=require('os'),path=require('path'),zlib=require('zlib'),assert=require('assert/strict');
const {apply}=require('./files/apply.cjs');
const temp=fs.mkdtempSync(path.join(os.tmpdir(),'ocr-compat-'));
const root=path.join(temp,'www/_app/immutable/chunks');fs.mkdirSync(root,{recursive:true});
fs.copyFileSync(path.join(process.argv[2],'index.html'),path.join(temp,'www/index.html'));
try {
 for(const file of ['CUVvskNU.js','CC5MOeVu.js'])fs.copyFileSync(path.join(process.argv[2],file),path.join(root,file));
 const status=path.join(root,'status.json'),file=path.join(root,'CUVvskNU.js'),original=fs.readFileSync(file,'utf8');
 const first=apply(root,status); assert(first.enabled);
 const index=fs.readFileSync(path.join(temp,'www/index.html'),'utf8');assert(index.includes(first.assetPrefix));
 assert(fs.readFileSync(path.join(temp,'www',first.assetPrefix,'chunks/CUVvskNU.js'),'utf8').includes('Tout copier'));
 const patched=fs.readFileSync(file,'utf8');
 assert(patched.includes('Tout copier')); assert(patched.includes('localStorage'));
 for(const [ext,decode] of [['gz',zlib.gunzipSync],['br',zlib.brotliDecompressSync]])
  assert.equal(decode(fs.readFileSync(file+'.'+ext)).toString(),patched);
 assert(apply(root,status).enabled);assert.equal(fs.readFileSync(file,'utf8'),patched);
 fs.appendFileSync(path.join(root,'CC5MOeVu.js'),'\n// simulated upstream change');
 assert.equal(apply(root,status).enabled,false);
 assert.equal(fs.readFileSync(file,'utf8'),original);
 assert.equal(zlib.gunzipSync(fs.readFileSync(file+'.gz')).toString(),original);
 assert.equal(JSON.parse(fs.readFileSync(status)).enabled,false);
 assert.equal(fs.readFileSync(path.join(temp,'www/index.html'),'utf8'),fs.readFileSync(path.join(process.argv[2],'index.html'),'utf8'));
 console.log('PASS compatibility: exact originals, compressed variants, idempotence, unknown frontend disabled/restored, persisted warning');
}finally{fs.rmSync(temp,{recursive:true,force:true})}
