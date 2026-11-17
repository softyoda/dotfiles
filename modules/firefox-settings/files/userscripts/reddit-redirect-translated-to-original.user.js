// ==UserScript==
// @name         Redirect translated Reddit post to original
// @namespace    neozetare
// @version      2024-05-17
// @description  Redirect translated Reddit post to original by redirecting to the same URL without the lang information (in search parameter "tl" or at the end of pathname)
// @author       neozetare
// @match        https://www.reddit.com/r/*/comments/*/*/?*tl=*
// @match        https://www.reddit.com/r/*/comments/*/*/*/*
// @grant        none
// @run-at       document-start
// @updateURL    https://raw.githubusercontent.com/softyoda/dotfiles/master/modules/firefox-settings/files/userscripts/reddit-redirect-translated-to-original.user.js
// @downloadURL  https://raw.githubusercontent.com/softyoda/dotfiles/master/modules/firefox-settings/files/userscripts/reddit-redirect-translated-to-original.user.js
// ==/UserScript==

// If anything stops working, contact me @neozetare on Reddit/Discord/Twitter
// Thanks to u/Gliglue for the help

// Get the URL
const l = window.location;

// Delete "tl" search parameter (where the lang could be) and other that could lead to its creation
const params = new URLSearchParams(l.search);
params.delete('tl');
params.delete('translated');
params.delete('pretranslation_language');

// Deal with other search parameters to preserve them (which shouldn't happen but who knows)
let search = "";
if (params.values().next().done === false) {
    search = `?${params.toString()}`
}

// Strip anything after the 6th "/" in the pathname (where the lang could be)
const pathname = l.pathname.split('/').slice(0, 6).join('/') + '/';

// Redirect to the new URL
const location = `${l.protocol}//${l.host}${pathname}${search}${l.hash}`
window.location.replace(location);
