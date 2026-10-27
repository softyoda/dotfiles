# Ctrl+Maj+Échap = Mission Center

Un script KWin enregistre le raccourci global `Ctrl+Shift+Escape` ; il démarre l'unité
utilisateur `mission-center.service` (Flatpak `io.missioncenter.MissionCenter`) via D-Bus.
Le service n'est pas activé au démarrage : il est lancé à la demande.
Effectif après reconnexion si le script KWin n'est pas chargé tout de suite.
