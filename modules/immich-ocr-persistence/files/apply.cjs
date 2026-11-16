// Patch only the recognized OCR manager; never run OCR or change asset data.
const fs = require('node:fs');
const path = require('node:path');
const zlib = require('node:zlib');
const vm = require('node:vm');
const KEY = 'immich.ocr.showOverlay';
const MARKER = '/*immich-ocr-preference-v1*/';

function patch(source) {
  if (source.includes(MARKER)) return source;
  const pattern = /new class\{[^{}]*#[\w$]+=\w+\([^;]+;get showOverlay\(\)[\s\S]*?toggleOcrBoundingBox\(\)\{this.showOverlay=!this.showOverlay\}\}/g;
  const matches = [...source.matchAll(pattern)].filter(m => m[0].includes('getAssetOcr'));
  if (matches.length !== 1) throw Error('Structure du gestionnaire OCR inconnue (aucune modification)');
  const original = matches[0][0];
  const slot = original.match(/get showOverlay\(\)\{return [\w$]+\(this\.(#[\w$]+)\)\}/)?.[1];
  if (!slot) throw Error('Champ de préférence OCR inconnu');
  const init = new RegExp(slot + '=([\\w$]+)\\(!1\\)');
  if (!init.test(original) || !original.includes(',this.showOverlay=!1}toggleOcrBoundingBox'))
    throw Error('Initialisation ou remise à zéro OCR inconnue');
  let changed = original.replace(init, (_, signal) =>
    slot + '=' + signal + '((()=>{try{return globalThis.localStorage.getItem("' + KEY + '")==="true"}catch{return false}})())');
  changed = changed.replace(',this.showOverlay=!1}toggleOcrBoundingBox', '}toggleOcrBoundingBox');
  changed = changed.replace('toggleOcrBoundingBox(){this.showOverlay=!this.showOverlay}',
    'toggleOcrBoundingBox(){this.showOverlay=!this.showOverlay;try{globalThis.localStorage.setItem("' + KEY + '",String(this.showOverlay))}catch{}}');
  // Parse the isolated class before touching any live file.
  new vm.Script('(' + changed + ')');
  return source.replace(original, MARKER + changed);
}


const crypto = require('node:crypto');
const cache = require('./cache.cjs');
const MANAGER_HASH = 'bc8a205c2aadda1787ff45ba9820a4433a9cde41e3a9fb642399eb6d326bfa7b';
const VIEWER_HASH = 'f8c3016aa1382ca7955f2d76aa95447f5fcdc9a3d7d9a360800ffd1b4ba6a44f';
const PANEL_MARKER = '/* immich-ocr-text-panel-v1:';
const hash = s => crypto.createHash('sha256').update(s).digest('hex');
function writeVariants(file, content) {
  const bytes = Buffer.from(content);
  const variants = [[file,bytes],[file+'.gz',zlib.gzipSync(bytes)],[file+'.br',zlib.brotliCompressSync(bytes)]];
  const backups = variants.map(([name]) => fs.existsSync(name) ? fs.readFileSync(name) : null);
  const suffix = '.ocr-tmp-'+process.pid;
  try {
    for (const [name,data] of variants) fs.writeFileSync(name+suffix,data);
    for (const [name] of variants) fs.renameSync(name+suffix,name);
  } catch (e) {
    variants.forEach(([name],i) => {
      if (backups[i] !== null) fs.writeFileSync(name,backups[i]);
      else fs.rmSync(name,{force:true});
    });
    throw e;
  } finally {
    for (const [name] of variants) fs.rmSync(name+suffix,{force:true});
  }
}
function apply(root, statusFile='/usr/src/app/upload/.immich-maintenance/ocr-status.json') {
  let changed = false, index;
  let status = {schema:1, enabled:false, reason:'incompatible', revision:'ocr-panel-v1'};
  const files = fs.readdirSync(root).filter(f => f.endsWith('.js'));
  const sources = files.map(name => {
    const file = path.join(root,name), current = fs.readFileSync(file,'utf8');
    const base = (current.includes(MARKER) || current.includes(PANEL_MARKER)) && fs.existsSync(file+'.ocr-original')
      ? fs.readFileSync(file+'.ocr-original','utf8') : current;
    return {file,current,base};
  });
  try {
    index = cache.indexInfo(root,hash);
    const managers = sources.filter(s => hash(s.base) === MANAGER_HASH);
    if (managers.length !== 1 || !sources.some(s => hash(s.base) === VIEWER_HASH))
      throw Error('Interface non vérifiée : extension désactivée');
    const {file,current,base} = managers[0];
    const names = [...base.matchAll(/(?:var |,)([\w$]+)=new class\{[^{}]*#[\w$]+=\w+\([^;]+;get showOverlay\(\)/g)];
    if (names.length !== 1) throw Error('Gestionnaire OCR ambigu');
    const panelSource = fs.readFileSync(path.join(__dirname,'panel.js'),'utf8');
    if (panelSource.split('__IMMICH_OCR_MANAGER__').length !== 2) throw Error('Source du panneau invalide');
    const addition = panelSource.replace('__IMMICH_OCR_MANAGER__',names[0][1]);
    new vm.Script(addition); // parse only, never execute browser code on the server
    const after = patch(base) + '\n;' + addition;
    if (after !== current) {
      if (!fs.existsSync(file+'.ocr-original')) fs.writeFileSync(file+'.ocr-original',base);
      writeVariants(file,after); changed = true;
    }
    const digest=hash(after).slice(0,16);
    changed = cache.publish(root,index,digest,writeVariants) || changed;
    status = {...status, enabled:true,reason:'ok',assetPrefix:'/_app/immutable-ocr-'+digest+'/'};
    console.log('OCR : préférence et panneau Tout copier vérifiés.');
  } catch (e) {
    // Remove our extension on a previously patched, now unsupported frontend.
    for (const {file,current,base} of sources)
      if (current !== base) { writeVariants(file,base); changed = true; }
    changed = cache.restore(index,writeVariants) || changed;
    console.warn('OCR : extension désactivée ; interface standard conservée. '+e.message);
  }
  fs.mkdirSync(path.dirname(statusFile),{recursive:true});
  fs.writeFileSync(statusFile+'.tmp',JSON.stringify(status)+'\n',{mode:0o644});
  fs.renameSync(statusFile+'.tmp',statusFile);
  if(changed) console.log('OCR_ASSETS_CHANGED');
  return status;
}
module.exports = { patch, apply, KEY };
if (require.main === module) {
  try { apply(process.argv[2] || '/build/www/_app/immutable/chunks', process.argv[3]); }
  catch (e) {
    console.error('OCR : erreur du hook — '+e.message);
    try {
      const p = process.argv[3] || '/usr/src/app/upload/.immich-maintenance/ocr-status.json';
      fs.mkdirSync(path.dirname(p),{recursive:true});
      fs.writeFileSync(p,JSON.stringify({schema:1,enabled:false,reason:'hook-error',revision:'ocr-panel-v1'})+'\n');
    } catch { console.error('OCR : statut indisponible, consulter les logs du conteneur.'); }
    process.exitCode=2;
  }
}
