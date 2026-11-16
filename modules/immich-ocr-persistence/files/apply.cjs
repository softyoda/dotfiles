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

function apply(root) {
  const files = fs.readdirSync(root).filter(f => f.endsWith('.js'));
  const candidates = files.filter(f => {
    const s = fs.readFileSync(path.join(root, f), 'utf8');
    return s.includes('toggleOcrBoundingBox(){') && s.includes('getAssetOcr');
  });
  if (candidates.length !== 1) throw Error('Bundle OCR introuvable ou ambigu');
  const file = path.join(root, candidates[0]);
  const before = fs.readFileSync(file, 'utf8');
  const after = patch(before);
  if (before !== after) {
    const data = Buffer.from(after);
    const outputs = [[file, data],
      [file + '.gz', zlib.gzipSync(data)],
      [file + '.br', zlib.brotliCompressSync(data)]];
    if (!fs.existsSync(file + '.ocr-original')) fs.copyFileSync(file, file + '.ocr-original');
    // Prepare every variant before replacing anything.
    for (const [name, bytes] of outputs) fs.writeFileSync(name + '.ocr-tmp', bytes);
    for (const [name] of outputs) fs.renameSync(name + '.ocr-tmp', name);
  }
  console.log('OCR : préférence persistante vérifiée (' + candidates[0] + ').');
}
module.exports = { patch, apply, KEY };
if (require.main === module) {
  try { apply(process.argv[2] || '/build/www/_app/immutable/chunks'); }
  catch (e) { console.error('OCR : correctif non appliqué — ' + e.message); process.exitCode = 2; }
}
