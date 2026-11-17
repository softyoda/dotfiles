// ==UserScript==
// @name         SensCritique on Google Search
// @version      1.1.3
// @description  Adds a button to search SensCritique via Google Search
// @author       Alexyoe (modified)
// @namespace    https://github.com/Alexyoe/Reddit-on-Google-Search
// @license      MIT
// @include      http*://www.google.*/search*
// @include      http*://google.*/search*
// @run-at       document-end
// @updateURL    https://raw.githubusercontent.com/softyoda/dotfiles/master/modules/firefox-settings/files/userscripts/senscritique-on-google-search.user.js
// @downloadURL  https://raw.githubusercontent.com/softyoda/dotfiles/master/modules/firefox-settings/files/userscripts/senscritique-on-google-search.user.js
// ==/UserScript==

const settings = {
  // Choose exactly one: "icon" or "label"
  displayMode: "icon",
  btnPosition: "start", // "start", "end", or "afterai"
  fixSize: false,
};

// Start Code
const queryRegex = /q=[^&]+/g;
const siteRegex = /\+site(?:%3A|\:).+\.[^&+]+/g;
const targetUrl = "+site%3Asenscritique.com";

// SensCritique Icon (Text Version)
// This uses an SVG <text> element to render a bold "SC"
let scIcon = `
<svg focusable="false" fill="currentColor" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="17" height="17">
  <text x="50%" y="54%" dy=".35em" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-weight="900" font-size="18" letter-spacing="-1">SC</text>
</svg>`;

// Trusted Types for CSP
if (typeof trustedTypes !== "undefined") {
  const p = trustedTypes.createPolicy("html", { createHTML: (x) => x });
  scIcon = p.createHTML(scIcon);
}

(function waitForNav() {
  const nav = Array.from(
    document.querySelectorAll('div[role="navigation"]')
  ).find((n) => n.querySelector('div[role="listitem"] a'));
  if (!nav) return setTimeout(waitForNav, 200);

  // 1) grab the first wrapper <div role="listitem">
  const sampleItem = nav.querySelectorAll(':scope div[role="listitem"]');
  if (!sampleItem) return;

  // 2) clone the entire wrapper
  const itemToClone = sampleItem[2] || sampleItem[0];
  const newItem = itemToClone.cloneNode(true);

  // 3) inside that clone, find the <a>
  const btn = newItem.querySelector("a");
  btn.href = window.location.href.replace(queryRegex, (m) =>
    m.search(siteRegex) >= 0 ? m.replace(siteRegex, targetUrl) : m + targetUrl
  );

  // find their inner div (jsname) or fallback to the <a>
  const inner = btn.querySelector("div[jsname]") || btn;

  if (settings.displayMode === "label") {
    const textWrapper = document.createElement("span");
    inner.innerHTML = "";
    textWrapper.textContent = "SensCritique";
    textWrapper.className = "R1QWuf";
    inner.appendChild(textWrapper);
  } else {
    inner.innerHTML = "";
    const iconWrapper = document.createElement("span");
    iconWrapper.className = "R1QWuf";
    iconWrapper.style.lineHeight = "17px";
    iconWrapper.innerHTML = scIcon;
    inner.appendChild(iconWrapper);
  }

  // 4) insert the **wrapper** at the requested position
  const first = nav.querySelector(':scope div[role="listitem"]');
  if (settings.btnPosition === "start") {
    first ? first.before(newItem) : nav.prepend(newItem);
  } else if (settings.btnPosition === "end") {
    nav.append(newItem);
  } else {
    first ? first.after(newItem) : nav.append(newItem);
  }

  // optional: prevent wrapping
  if (settings.fixSize) {
    nav.style.maxWidth = "inherit";
    nav.style.overflowX = "auto";
    nav.style.whiteSpace = "nowrap";
  }
})();
