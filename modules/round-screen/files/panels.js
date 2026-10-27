// Écran rond : heure seule en haut (arc du haut), dock en bas (menu · applis · notifications).
// Panneaux ajustés au contenu et centrés ; le dock flotte pour décoller du bord.
var scr = 0;
for (var i = 0; i < screenCount; ++i) {
    var g = screenGeometry(i);
    if (g.width == g.height) scr = i;
}
panels().forEach(function (p) { if (p.screen == scr) p.remove(); });

// ── Haut : l'heure, lisible, centrée
var top = new Panel;
top.screen = scr;
top.location = "top";
top.height = 30;
top.lengthMode = "fit";
top.alignment = "center";
top.floating = false;
var clock = top.addWidget("org.kde.plasma.digitalclock");
clock.currentConfigGroup = ["Appearance"];
clock.writeConfig("autoFontAndSize", true);
clock.writeConfig("showDate", false);

// ── Bas : menu · applis ouvertes (icônes seules) · notifications réduites
var dock = new Panel;
dock.screen = scr;
dock.location = "bottom";
dock.height = 42;
dock.lengthMode = "fit";
dock.alignment = "center";
dock.floating = true;

var menu = dock.addWidget("org.kde.plasma.kickoff");
menu.currentConfigGroup = ["General"];
menu.writeConfig("icon", "start-here-kde-symbolic");

var tasks = dock.addWidget("org.kde.plasma.icontasks");
tasks.currentConfigGroup = ["General"];
tasks.writeConfig("launchers", "");          // seulement les applis ouvertes
tasks.writeConfig("maxStripes", 1);

var tray = dock.addWidget("org.kde.plasma.systemtray");
tray.currentConfigGroup = ["General"];
tray.writeConfig("shownItems", ["org.kde.plasma.devicenotifier", "org.kde.plasma.networkmanagement", "org.kde.plasma.volume"]);
tray.writeConfig("hiddenItems", ["org.kde.plasma.bluetooth", "org.kde.plasma.brightness", "org.kde.plasma.battery",
    "org.kde.plasma.clipboard", "org.kde.plasma.notifications", "org.kde.kscreen", "org.kde.plasma.keyboardlayout",
    "org.kde.plasma.cameraindicator", "org.kde.plasma.manage-inputmethod", "org.kde.plasma.printmanager",
    "org.kde.kdeconnect", "org.kde.plasma.mediacontroller", "org.kde.plasma.keyboardindicator", "org.kde.plasma.weather"]);
