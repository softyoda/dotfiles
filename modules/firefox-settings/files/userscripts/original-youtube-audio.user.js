// ==UserScript==
// @name         Original Youtube Audio
// @namespace    Original Youtube Audio
// @version      2.0
// @description  Sélectionne automatiquement la piste audio d'origine sur YouTube (interface en français, anglais, italien, espagnol, allemand…)
// @author       LiefLayer (adapté par softyoda)
// @match        https://*.youtube.com/*
// @grant        none
// @run-at       document-idle
// @updateURL    https://raw.githubusercontent.com/softyoda/dotfiles/master/modules/firefox-settings/files/userscripts/original-youtube-audio.user.js
// @downloadURL  https://raw.githubusercontent.com/softyoda/dotfiles/master/modules/firefox-settings/files/userscripts/original-youtube-audio.user.js
// ==/UserScript==

(function () {
    'use strict';

    // Libellé de l'entrée « Piste audio » du menu Paramètres, selon la langue de l'interface.
    const AUDIO_TRACK = /piste audio|audio track|traccia audio|pista de audio|tonspur|faixa de áudio|audiospoor|ścieżka dźwiękowa/i;
    // Libellé de la piste d'origine : « (d'origine) », « original », « originale »…
    const ORIGINAL = /origin/i;

    const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

    async function waitFor(fn, timeout = 3000) {
        const end = Date.now() + timeout;
        while (Date.now() < end) {
            const v = fn();
            if (v) return v;
            await sleep(100);
        }
        return null;
    }

    const menuItems = () => [...document.querySelectorAll('.ytp-settings-menu .ytp-menuitem')];

    let running = false;
    let lastVideo = null;

    async function selectOriginalTrack() {
        const videoId = new URLSearchParams(location.search).get('v') || location.pathname;
        if (running || videoId === lastVideo) return;
        running = true;
        const settings = await waitFor(() => document.querySelector('.ytp-settings-button'), 10000);
        const menu = document.querySelector('.ytp-settings-menu');
        try {
            if (!settings) return;
            lastVideo = videoId;
            settings.click();
            const trackItem = await waitFor(() =>
                menuItems().find((x) => AUDIO_TRACK.test(x.querySelector('.ytp-menuitem-label')?.textContent || '')));
            if (!trackItem) return; // vidéo sans pistes audio multiples
            if (ORIGINAL.test(trackItem.querySelector('.ytp-menuitem-content')?.textContent || '')) return; // déjà d'origine
            trackItem.click();
            const original = await waitFor(() =>
                menuItems().find((x) => ORIGINAL.test(x.textContent) && !AUDIO_TRACK.test(x.textContent)));
            if (original) original.click();
        } finally {
            // Referme le menu s'il est resté ouvert.
            if (menu && menu.style.display !== 'none' && settings) settings.click();
            running = false;
        }
    }

    // YouTube est une application monopage : relancer à chaque navigation.
    document.addEventListener('yt-navigate-finish', () => {
        if (location.pathname === '/watch') {
            setTimeout(selectOriginalTrack, 1500);
        }
    });
    if (location.pathname === '/watch') setTimeout(selectOriginalTrack, 3000);
})();
