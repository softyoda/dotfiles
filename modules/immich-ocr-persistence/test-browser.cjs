const {chromium}=require('playwright-core');
const fs=require('fs'),assert=require('assert/strict'),http=require('http');
(async()=>{
const html='<!doctype html><html><body style="background:#121212;color:#eee;font-family:sans-serif"><div data-testid="detail-panel" class="w-90" style="width:340px;margin-left:auto"><section class="relative p-2"><div><button>Fermer</button><p>Information</p></div><p>Ajouter une description</p><p>Détails</p></section></div></body></html>';
const server=http.createServer((req,res)=>{res.setHeader('Content-Type','text/html; charset=utf-8');res.end(html)}).listen(0,'127.0.0.1');
await new Promise(r=>server.once('listening',r));
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
try{
 const page=await browser.newPage({viewport:{width:1000,height:700}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:'+server.address().port);
 await page.evaluate(()=>{
  window.clipboardWrites=[];Object.defineProperty(navigator,'clipboard',{value:{writeText:async s=>window.clipboardWrites.push(s)},configurable:true});
  window.manager={data:[],async getAssetOcr(boxes,delay=0){await new Promise(r=>setTimeout(r,delay));this.data=boxes},clear(){this.data=[]}};
 });
 await page.addScriptTag({content:fs.readFileSync(require('path').join(__dirname,'files/panel.js'),'utf8').replace('__IMMICH_OCR_MANAGER__','window.manager')});
 const box=(text,x,y)=>({assetId:'one',text,x1:x,x2:x+.2,x3:x+.2,x4:x,y1:y,y2:y,y3:y+.04,y4:y+.04});
 assert.equal(await page.locator('#immich-ocr-text').count(),0);
 const malicious='<img src=x onerror="window.pwned=true">';
 await page.evaluate(boxes=>manager.getAssetOcr(boxes),[box('Ligne suivante',0,.2),box('Bonjour',0,.1),box('monde',.4,.1),box(malicious,0,.3)]);
 assert.equal(await page.locator('#immich-ocr-text textarea').inputValue(),'Bonjour monde\nLigne suivante\n'+malicious);
 assert.equal(await page.locator('#immich-ocr-text img').count(),0);
 assert.equal(await page.evaluate(()=>window.pwned),undefined);
 assert.equal(await page.evaluate(()=>clipboardWrites.length),0);
 await page.getByRole('button',{name:'Tout copier'}).click();
 assert.equal(await page.evaluate(()=>clipboardWrites[0]),'Bonjour monde\nLigne suivante\n'+malicious);
 if(process.env.OCR_TEST_SCREENSHOT) await page.screenshot({path:process.env.OCR_TEST_SCREENSHOT});
 await page.evaluate(()=>{navigator.clipboard.writeText=async()=>{throw Error('denied')}});
 await page.getByRole('button',{name:'Tout copier'}).click();
 assert.match(await page.locator('#immich-ocr-text [role=status]').textContent(),/Ctrl\+C/);
 await page.evaluate(()=>manager.clear());
 assert.equal(await page.locator('#immich-ocr-text').count(),0);
 // Late request must not recreate text from an image that has been left.
 await page.evaluate(b=>{manager.getAssetOcr([b],80);manager.clear()},box('OLD',0,0));
 await page.waitForTimeout(130);
 assert.equal(await page.locator('#immich-ocr-text').count(),0);
 await page.evaluate(b=>manager.getAssetOcr([b]),box('NOUVEAU',0,0));
 await page.evaluate(()=>{window.saved=document.querySelector('[data-testid="detail-panel"]');saved.remove()});
 await page.waitForTimeout(10);
 await page.evaluate(()=>document.body.append(saved));
 await page.waitForTimeout(10);
 assert.equal(await page.locator('#immich-ocr-text textarea').inputValue(),'NOUVEAU');
 // Removing the known panel layout disables only the extension and produces an alert.
 await page.evaluate(()=>document.querySelector('[data-testid="detail-panel"] section').className='changed-layout');
 // trigger childList, as a new upstream layout would do
 await page.evaluate(()=>document.querySelector('[data-testid="detail-panel"]').append(document.createElement('span')));
 await page.waitForTimeout(10);
 assert.equal(await page.locator('#immich-ocr-text').count(),0);
 assert.match(await page.locator('#immich-ocr-warning').textContent(),/désactivé/);
 assert.deepEqual(errors,[]);
 console.log('PASS browser: plain text/XSS, clipboard click and denial, empty assets, ordering, navigation/races, panel reopen, fail-open alert');
} finally {await browser.close();server.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
