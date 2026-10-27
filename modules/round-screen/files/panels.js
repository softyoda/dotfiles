// Écran rond : une barre en haut, épaisse et non flottante, contenu centré.
// L'épaisseur repousse le contenu dans la partie large de l'arc ; les icônes
// gardent une taille fixe (police d'horloge fixe, icônes de notification fixes).
var scr = 0;
for (var i = 0; i < screenCount; ++i) {
    var g = screenGeometry(i);
    if (g.width == g.height) scr = i;
}
panels().forEach(function (p) { if (p.screen == scr) p.remove(); });

var bar = new Panel;
bar.screen = scr;
bar.location = "top";
bar.height = 76;
bar.lengthMode = "fit";
bar.alignment = "center";
bar.floating = false;

// Ordre : liste des fenêtres | menu (au centre, là où l'arc est le plus haut) | heure | notifications
bar.addWidget("org.kde.plasma.windowlist");

var menu = bar.addWidget("org.kde.plasma.kickoff");
menu.currentConfigGroup = ["General"];
menu.writeConfig("icon", "start-here-kde-symbolic");

var clock = bar.addWidget("org.kde.plasma.digitalclock");
clock.currentConfigGroup = ["Appearance"];
clock.writeConfig("autoFontAndSize", false);
clock.writeConfig("fontSize", 13);
clock.writeConfig("showDate", false);

var tray = bar.addWidget("org.kde.plasma.systemtray");
