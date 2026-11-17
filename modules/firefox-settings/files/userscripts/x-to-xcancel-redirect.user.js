// ==UserScript==
// @name         X to XCancel Redirect
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  Add context menu item to redirect from X to XCancel
// @author       softyoda
// @match        https://x.com/*
// @match        https://twitter.com/*
// @grant        GM_registerMenuCommand
// @grant        GM.registerMenuCommand
// @grant        GM_openInTab
// @updateURL    https://raw.githubusercontent.com/softyoda/dotfiles/master/modules/firefox-settings/files/userscripts/x-to-xcancel-redirect.user.js
// @downloadURL  https://raw.githubusercontent.com/softyoda/dotfiles/master/modules/firefox-settings/files/userscripts/x-to-xcancel-redirect.user.js
// ==/UserScript==

(function() {
    'use strict';

    GM.registerMenuCommand("View on XCancel", function() {
        const currentPath = window.location.pathname;
        window.location.href = 'https://xcancel.com' + currentPath;
    });
})();
