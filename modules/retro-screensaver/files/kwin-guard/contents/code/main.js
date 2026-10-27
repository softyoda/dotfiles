function update() {
    const blocked = workspace.windowList().some(w => !w.minimized && w.fullScreen && !String(w.resourceClass).toLowerCase().includes('xscreensaver') && String(w.resourceClass) !== 'plasmashell');
    callDBus('local.RetroSaver', '/RetroSaver', 'local.RetroSaver', 'SetFullscreen', blocked);
}
function watch(w) {
    w.fullScreenChanged.connect(update);
    w.minimizedChanged.connect(update);
    update();
}
workspace.windowList().forEach(watch);
workspace.windowAdded.connect(watch);
workspace.windowRemoved.connect(update);
workspace.windowActivated.connect(update);
update();
