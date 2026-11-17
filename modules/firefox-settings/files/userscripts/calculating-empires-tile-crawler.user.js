// ==UserScript==
// @name         Calculating Empires - Tile Crawler + Auto Navigator
// @namespace    http://tampermonkey.net/
// @version      3.0
// @description  Downloads every map tile and drives the map around so that new tiles are fetched automatically.
// @author       You
// @match        https://calculatingempires.net/*
// @grant        GM_download
// @run-at       document-start
// @updateURL    https://raw.githubusercontent.com/softyoda/dotfiles/master/modules/firefox-settings/files/userscripts/calculating-empires-tile-crawler.user.js
// @downloadURL  https://raw.githubusercontent.com/softyoda/dotfiles/master/modules/firefox-settings/files/userscripts/calculating-empires-tile-crawler.user.js
// ==/UserScript==

/* ------------------------------------------------------------------ */
/* 0. SETTINGS                                                        */
/* ------------------------------------------------------------------ */

// folder (relative to the browser’s normal download directory)
const DOWNLOAD_DIR = 'CalculatingEmpires/tiles/';

// Define the “tour”.  A movement can be …
//
//  * ['x%2Cy%2Czoom' , duration]  pan/zoom smoothly   (duration in ms)
//  * ['x%2Cy%2Czoom']            jump instantly       (no animation)
//  * [time]                      just wait            (time in ms)
//
// Coordinates are the OpenLayers view-projection coordinates that you see
// inside the address bar after ‘?center=…&zoom=…’ on CE.

const MOVEMENTS = [
  //      x               y             z     ms
  ['0%2C0%2C1',           1000],    // zoom out to world
  [  500 ],                          // wait ½ second
  ['1000000%2C0%2C3',      2500],    // fly east
  ['1000000%2C1000000%2C4',2500],    // fly south-east
  [  1000 ],                         // wait a bit
  ['0%2C0%2C2']                     // jump back instantly
];

/* ------------------------------------------------------------------ */
/* 1.  TILE DOWNLOADER  (your original code, only cosmetically moved) */
/* ------------------------------------------------------------------ */

(function downloader() {
  'use strict';

  const downloaded = new Set();

  function sanitizeFilename(name) {
    return name.replace(/[?&=]/g, '_').replace(/[/\\]/g, '_');
  }

  function makeFilename(url) {
    const u  = new URL(url);
    const fp = (u.pathname.startsWith('/') ? u.pathname.slice(1) : u.pathname) +
               (u.search || '');
    let fn = sanitizeFilename(fp);
    if (!/\.(png|jpe?g|webp)$/i.test(fn)) fn += '.png';
    return DOWNLOAD_DIR + fn;
  }

  function fallback(url, fn) {
    fetch(url)
      .then(r => r.blob())
      .then(b => {
        const a = document.createElement('a');
        a.href = URL.createObjectURL(b);
        a.download = fn;
        a.style.display = 'none';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(a.href);
        console.log('Downloaded (fallback):', fn);
      })
      .catch(console.error);
  }

  function dl(url) {
    if (downloaded.has(url)) return;
    downloaded.add(url);
    const fn = makeFilename(url);

    if (typeof GM_download === 'function') {
      GM_download({
        url,
        name   : fn,
        saveAs : false,
        onerror: e => { console.error('GM_download error', e); fallback(url, fn); }
      });
      console.log('Downloaded:', fn);
    } else {
      fallback(url, fn);
    }
  }

  /* ---------  network interception  --------- */

  const passThruFetch = window.fetch.bind(window);
  window.fetch = function(...args) {
    const url = args[0] && (typeof args[0] === 'string' ? args[0] : args[0].url);
    return passThruFetch(...args).then(resp => {
      const ctype = resp.headers.get('content-type') || '';
      if (/image\/|\.png|\.jpe?g|\.webp|tile/i.test(url) || ctype.startsWith('image/')) {
        dl(url);
      }
      return resp;
    });
  };

  const open = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function(m, url, ...rest) {
    this._url = url;
    return open.call(this, m, url, ...rest);
  };
  const send = XMLHttpRequest.prototype.send;
  XMLHttpRequest.prototype.send = function(...rest) {
    this.addEventListener('load', function() {
      if (this.status === 200) {
        const ct = this.getResponseHeader('content-type') || '';
        if (/image\/|\.png|\.jpe?g|\.webp|tile/i.test(this._url) || ct.startsWith('image/')) {
          dl(this._url);
        }
      }
    });
    return send.apply(this, rest);
  };

  /* ---------  DOM mutation (img / canvas etc.) --------- */
  const mo = new MutationObserver(ms => {
    for (const m of ms) {
      for (const n of m.addedNodes) {
        if (n.nodeType !== 1) continue;
        if (n.tagName === 'IMG' && n.src) {
          if (/tile|\.png|\.jpe?g|\.webp/i.test(n.src)) dl(n.src);
        }
        // inline background-image
        const bg = n.style && n.style.backgroundImage;
        if (bg) {
          const u = /url\(['"]?([^'")]+)['"]?\)/.exec(bg);
          if (u && /tile|\.png|\.jpe?g|\.webp/i.test(u[1])) dl(u[1]);
        }
      }
    }
  });
  document.addEventListener('DOMContentLoaded', () => {
    mo.observe(document.body, {childList:true, subtree:true});
  });

  /* intercept canvas & WebGL uploads as before */
  const drawImage = CanvasRenderingContext2D.prototype.drawImage;
  CanvasRenderingContext2D.prototype.drawImage = function(img, ...rest) {
    if (img && img.src && /tile|\.png|\.jpe?g|\.webp/i.test(img.src)) dl(img.src);
    return drawImage.call(this, img, ...rest);
  };
  if (window.WebGLRenderingContext) {
    const tex = WebGLRenderingContext.prototype.texImage2D;
    WebGLRenderingContext.prototype.texImage2D = function(...rest) {
      for (const a of rest) {
        if (a && a.src && /tile|\.png|\.jpe?g|\.webp/i.test(a.src)) dl(a.src);
      }
      return tex.apply(this, rest);
    };
  }

  console.log('[TileCrawler] ready – saving to', DOWNLOAD_DIR);
})();

/* ------------------------------------------------------------------ */
/* 2.  MAP AUTOMATION  (“animateMap”)                                 */
/* ------------------------------------------------------------------ */

/**
 * Runs the given movement list on an OpenLayers map.
 * @param {ol.Map} map
 * @param {Array}   moves   – see explanation at top of file
 * @returns {Function} call to cancel the tour
 */
function runTour(map, moves) {
  let cancelled = false;
  const cancel = () => { cancelled = true; map.un('pointerdrag', cancel); };

  async function step(m) {
    if (cancelled) return;
    if (m.length === 1) {
      if (typeof m[0] === 'number') {          // wait
        await new Promise(r => setTimeout(r, m[0]));
      } else {                                 // jump
        const [x,y,z] = m[0].split('%2C').map(parseFloat);
        map.getView().setCenter([x,y]); map.getView().setZoom(z);
      }
    } else {
      const [coord, dur] = m;
      const [x,y,z] = coord.split('%2C').map(parseFloat);
      await new Promise(r =>
        map.getView().animate({center:[x,y], zoom:z, duration:dur}, r)
      );
    }
  }

  (async () => {
    for (const m of moves) { if (cancelled) break; await step(m); }
    console.log('[TileCrawler] tour finished');
  })();

  map.on('pointerdrag', cancel);   // if user touches map: stop
  map.on('pointerdown', cancel);
  return cancel;
}

/* ------------------------------------------------------------------ */
/* 3.  WAIT FOR THE OpenLayers MAP INSTANCE AND START THE TOUR        */
/* ------------------------------------------------------------------ */

/**
 * Many pages expose the map instance as `window.map`; others keep it private.
 * We hook the Map constructor *early* and capture the first instance that
 * gets created.
 */
(function grabMapInstance() {
  const retry = () => setTimeout(grabMapInstance, 500);

  if (!(window.ol && window.ol.Map)) { retry(); return; }

  // Hook only once
  if (window.__ce_hooked__) return; window.__ce_hooked__ = true;

  const OrigMap = window.ol.Map;
  window.ol.Map = function(...a) {          // proxy constructor
    const inst = new OrigMap(...a);
    window.__ce_map__ = inst;               // expose globally
    startWhenReady(inst);
    return inst;
  };
  window.ol.Map.prototype = OrigMap.prototype;   // keep prototype chain
  // If the map was already created before we injected, try common globals:
  if (window.map instanceof OrigMap) startWhenReady(window.map);

  function startWhenReady(map) {
    if (map.__ce_tourStarted__) return;
    map.__ce_tourStarted__ = true;
    console.log('[TileCrawler] map hooked – starting tour …');
    runTour(map, MOVEMENTS);
  }
})();
