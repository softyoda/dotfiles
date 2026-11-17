// ==UserScript==
// @name         Epic Games Overflow Fix
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  Force overflow: visible sur Epic Games pour éviter overflow: hidden
// @author       You
// @match        https://*.epicgames.com/*
// @match        https://epicgames.com/*
// @grant        none
// @run-at       document-start
// @updateURL    https://raw.githubusercontent.com/softyoda/dotfiles/master/modules/firefox-settings/files/userscripts/epic-games-overflow-fix.user.js
// @downloadURL  https://raw.githubusercontent.com/softyoda/dotfiles/master/modules/firefox-settings/files/userscripts/epic-games-overflow-fix.user.js
// ==/UserScript==

(function() {
    'use strict';

    // Fonction pour forcer overflow: visible
    function forceOverflowVisible() {
        const body = document.body;
        if (body) {
            body.style.setProperty('overflow', 'visible', 'important');
        }
    }

    // Observer pour surveiller les changements sur le body
    function setupObserver() {
        const body = document.body;
        if (!body) return;

        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'attributes' &&
                    (mutation.attributeName === 'style' || mutation.attributeName === 'class')) {
                    forceOverflowVisible();
                }
            });
        });

        observer.observe(body, {
            attributes: true,
            attributeFilter: ['style', 'class']
        });

        // Force initial
        forceOverflowVisible();
    }

    // Démarrage quand le DOM est prêt
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', setupObserver);
    } else {
        setupObserver();
    }

    // Backup avec un intervalle pour être sûr
    setInterval(forceOverflowVisible, 1000);

})();
