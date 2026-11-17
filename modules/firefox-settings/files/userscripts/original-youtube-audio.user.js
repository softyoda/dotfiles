// ==UserScript==
// @name         Original Youtube Audio
// @namespace    Original Youtube Audio
// @version      1.30
// @description  Original Youtube Audio
// @author       LiefLayer
// @match        https://*.youtube.com/*
// @grant        none
// @updateURL    https://raw.githubusercontent.com/softyoda/dotfiles/master/modules/firefox-settings/files/userscripts/original-youtube-audio.user.js
// @downloadURL  https://raw.githubusercontent.com/softyoda/dotfiles/master/modules/firefox-settings/files/userscripts/original-youtube-audio.user.js
// ==/UserScript==

function changeAudioTrackToOriginal(){
console.log("YouTube video loaded!");
document.querySelector('.ytp-button.ytp-settings-button').click()
console.log("Is the audio track available?")
const audioTrackNode = [...document.querySelectorAll('div.ytp-menuitem')].filter(x => x.textContent.toLowerCase().includes('traccia audio'))
if (audioTrackNode === undefined || audioTrackNode.length == 0) {
console.log("Audio track not available, exiting...")
}
else {
console.log("Audio track available, expanding menu")
audioTrackNode[0].click()
const audioTracks = [...document.querySelectorAll('div.ytp-menuitem')].filter(x => x.textContent.toLowerCase().includes('originale'))
if (audioTracks === undefined || audioTracks.length == 0) {
console.log("Original audio track not available, exiting...")
audioTrackNode[0].click()
document.querySelector('.ytp-button.ytp-settings-button').click()
}
else {
console.log("Change language to original!");
audioTracks[0].click()
console.log("Closing menu");
}
}
document.querySelector('.ytp-button.ytp-settings-button').click()
}
var cUrl = "originalUrl"

document.addEventListener("DOMContentLoaded", function () {
var video = document.querySelector("video");
if (video) {
video.onloadeddata = function() {
if(this.src !== cUrl) {
cUrl = this.src
changeAudioTrackToOriginal()
}
}
}
else {
setTimeout(() => {
console.log("Waited for 5 seconds");
video = document.querySelector("video");
if (video) {
cUrl = this.src
changeAudioTrackToOriginal()
} else {
console.log("Could not find 'video' element");
}
}, 5000);
}
});

(function() {
    'use strict';

    setTimeout( () => {
        //Give time for element to appear in DOM...
        var video = document.querySelector("video");
      if (video) {
changeAudioTrackToOriginal()
} else {
console.log("Could not find 'video' element");
}
    },5000);})();
