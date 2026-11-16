/* immich-ocr-text-panel-v1: receives only the active viewer's existing OCR manager. */
(function installOcrTextPanel(manager) {
  'use strict';
  if (typeof document === 'undefined') return;
  const ID = 'immich-ocr-text';
  let generation = 0, loading = false, disabled = false, queued = false;
  let availableData = manager.data;
  let panel = null, textarea = null, feedback = null, lastData = null, text = '';
  function remove() {
    panel?.remove(); panel = textarea = feedback = null;
    lastData = null; text = '';
  }
  function fail() {
    disabled = true; remove(); observer.disconnect();
    if (document.getElementById('immich-ocr-warning')) return;
    const alert = document.createElement('div');
    alert.id = 'immich-ocr-warning'; alert.setAttribute('role', 'alert');
    Object.assign(alert.style, {position:'fixed',bottom:'20px',right:'20px',zIndex:'10000',
      maxWidth:'400px',padding:'16px',background:'#292524',color:'#fff',border:'1px solid #fbbf24',borderRadius:'8px'});
    const message = document.createElement('p');
    message.textContent = 'Le panneau de texte OCR a été désactivé : cette interface est incompatible. Immich reste utilisable.';
    const close = document.createElement('button'); close.type = 'button';
    close.textContent = 'Fermer'; close.onclick = () => alert.remove();
    alert.append(message, close); document.body.append(alert);
  }
  function format(boxes) {
    if (!Array.isArray(boxes) || boxes.length > 10000) throw Error('OCR shape');
    const valid = boxes.filter(b => b.isVisible !== false && typeof b.text === 'string' && b.text.trim());
    const ids = new Set(valid.map(b => b.assetId).filter(Boolean));
    if (ids.size > 1) throw Error('Mixed assets');
    const sorted = valid.map((b,i) => {
      const xs = [b.x1,b.x2,b.x3,b.x4], ys = [b.y1,b.y2,b.y3,b.y4];
      if (![...xs,...ys].every(Number.isFinite)) throw Error('OCR coordinates');
      return {text:b.text, x:Math.min(...xs), y:(Math.min(...ys)+Math.max(...ys))/2,
        h:Math.max(0.000001, Math.max(...ys)-Math.min(...ys)), i};
    }).sort((a,b) => a.y-b.y || a.x-b.x || a.i-b.i);
    const rows = [];
    for (const b of sorted) {
      const row = rows.at(-1);
      if (row && Math.abs(b.y-row.y) <= Math.min(b.h,row.h)*0.5) row.boxes.push(b);
      else rows.push({y:b.y,h:b.h,boxes:[b]});
    }
    const result = rows.map(r => r.boxes.sort((a,b) => a.x-b.x || a.i-b.i).map(b => b.text).join(' ')).join('\n');
    if (result.length > 1000000) throw Error('OCR size');
    return result;
  }
  function render() {
    if (disabled) return;
    const host = document.querySelector('[data-testid="detail-panel"]');
    const anchor = host?.querySelector(':scope > section.relative.p-2 > div:first-child');
    if (loading || !host || !host.classList.contains('w-90')) { remove(); return; }
    if (!anchor) { fail(); return; }
    const data = availableData;
    if (!Array.isArray(data) || !data.length) { remove(); return; }
    if (lastData !== data) { text = format(data); lastData = data; }
    if (!text) { remove(); return; }
    if (panel && !panel.isConnected) { panel = textarea = feedback = null; }
    if (!panel) {
      panel = document.createElement('section'); panel.id = ID;
      panel.setAttribute('aria-labelledby', ID+'-title');
      panel.className = 'p-4'; 
      const title = document.createElement('h2'); title.id = ID+'-title';
      title.textContent = 'Texte reconnu'; Object.assign(title.style,{marginBottom:'8px',fontSize:'14px',fontWeight:'400',color:'var(--color-immich-dark-fg, inherit)'});
      textarea = document.createElement('textarea'); textarea.readOnly = true;
      textarea.setAttribute('aria-label', 'Texte reconnu dans cette image');
      textarea.setAttribute('translate', 'no'); textarea.spellcheck = false; textarea.rows = 7;
      Object.assign(textarea.style, {width:'100%',boxSizing:'border-box',maxHeight:'320px',resize:'vertical',
        background:'transparent',color:'inherit',border:'none',borderRadius:'0',
        padding:'0',fontFamily:'inherit',fontSize:'14px',lineHeight:'1.5',userSelect:'text',cursor:'text'});
      // Do not let Immich's global photo shortcuts handle keys inside the text field.
      textarea.addEventListener('keydown', e => e.stopPropagation());
      const copy = document.createElement('button'); copy.type = 'button';
      copy.textContent = 'Tout copier';
      copy.className = 'text-sm hover:opacity-80';
      copy.addEventListener('keydown', e => e.stopPropagation());
      Object.assign(copy.style, {marginTop:'8px',padding:'6px 0',border:'none',background:'transparent',color:'inherit',fontFamily:'inherit',fontSize:'14px',cursor:'pointer'});
      feedback = document.createElement('p'); feedback.setAttribute('role','status');
      feedback.style.fontSize = '12px'; feedback.style.marginTop = '6px';
      copy.onclick = async () => {
        const field = textarea, note = feedback, token = generation;
        if (!field?.isConnected || loading || disabled) return;
        try {
          await navigator.clipboard.writeText(field.value);
          if (generation === token && note.isConnected) note.textContent = 'Texte copié.';
        } catch {
          if (generation === token && field.isConnected) {
            field.focus(); field.select();
            note.textContent = 'Copie non autorisée par le navigateur. Utilisez Ctrl+C sur le texte sélectionné.';
          }
        }
      };
      panel.append(title, textarea, copy, feedback);
      anchor.after(panel);
    }
    if (textarea.value !== text) { textarea.value = text; feedback.textContent = ''; }
  }
  function safeRender() { try { render(); } catch { fail(); } }
  function schedule() {
    if (queued || disabled) return;
    queued = true; queueMicrotask(() => { queued = false; safeRender(); });
  }
  // Observe panel mount/unmount only: no timers, API requests, or image scanning.
  const observer = new MutationObserver(records => {
    if (records.some(r => !r.target.closest?.('#'+ID) &&
      (r.target.closest?.('[data-testid="detail-panel"]') ||
      [...r.addedNodes,...r.removedNodes].some(n =>
        n.matches?.('[data-testid="detail-panel"]') || n.querySelector?.('[data-testid="detail-panel"]'))))) schedule();
  });
  try {
    if (typeof manager.getAssetOcr !== 'function' || typeof manager.clear !== 'function') throw Error('Manager shape');
    const load = manager.getAssetOcr, clear = manager.clear;
    manager.getAssetOcr = async function(...args) {
      const token = ++generation; loading = true; availableData = []; remove();
      if (!disabled) observer.observe(document.body,{childList:true,subtree:true});
      let success = false;
      try { const result = await load.apply(this,args); success = true; return result; }
      finally { if (generation === token) {
        availableData = success ? manager.data : [];
        loading = false; safeRender();
      } }
    };
    manager.clear = function(...args) {
      ++generation; loading = false; availableData = []; remove(); observer.disconnect();
      return clear.apply(this,args);
    };
    observer.observe(document.body,{childList:true,subtree:true});
    safeRender();
  } catch { fail(); }
})(__IMMICH_OCR_MANAGER__);
