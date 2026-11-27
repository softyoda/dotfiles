# Spotify + Spicetify

Le paquet natif `spotify-launcher` installe le client officiel dans
`~/.local/share/spotify-launcher/install/usr/share/spotify`. Spicetify peut y
écrire avec les droits de l’utilisateur. Le CLI est installé dans
`~/.spicetify` et le module configure le thème et l’application Marketplace.

## Installation et mises à jour

Appliquer `dotctl apply spicetify`, puis ouvrir **Spotify** depuis le menu.
Le raccourci prépare et patche Spotify avant le démarrage. Cachy-Update vérifie
aussi les mises à jour du client et applique Spicetify à la fin de la mise à
jour système, en modes interactif et automatique. Si Spotify est ouvert, la
sauvegarde, la mise à jour et le patch sont reportés au prochain lancement. Spotify fermé,
`spicetify-reapply` peut également appliquer le patch à la main.

Le champ Spicetify `prefs_path` pointe vers un fichier dédié, généré à partir
de la version que Spotify Launcher vient d’installer. Cela permet de patcher
la bonne version avant son premier démarrage et préserve les préférences de
Spotify.

## Sauvegarde et restauration du Marketplace

Spotify stocke les extensions, thèmes, snippets et réglages installés depuis
le Marketplace dans les dossiers Chromium `Local Storage` et `IndexedDB`.
Les réglages du CLI et les extensions installées manuellement se trouvent
dans `~/.config/spicetify`. Le lanceur et Cachy-Update sauvegardent ces données
localement, Spotify fermé, avant de vérifier ou d’installer une mise à jour.

Les archives privées sont dans
`${XDG_STATE_HOME:-~/.local/state}/spicetify-profile-backups`. Deux archives
identiques partagent le même fichier. Pour restaurer, quitter Spotify,
extraire une archive dans un dossier temporaire puis remettre `spicetify/`
et `spotify/prefs` dans le dossier de configuration XDG, et
`spotify/Browser/` et `spotify/Default/` dans le dossier de cache XDG. Faire
une copie du profil courant avant de remettre les dossiers archivés.
Les sauvegardes contiennent des données privées et restent sur la machine.

Lors d’une migration depuis Flatpak, les préférences sont dans
`~/.var/app/com.spotify.Client/config/spotify/` et les données Chromium
dans `~/.var/app/com.spotify.Client/cache/spotify/`. Reprendre les deux
emplacements pour retrouver les réglages et les extensions du Marketplace.

Le raccourci géré par ce module lance Spotify après avoir vérifié le patch
et les fichiers du Marketplace. S’il ne peut pas les préparer, il signale
l’erreur. La commande `spicetify-reapply --update` donne le détail.

## Incident NVIDIA du 27 novembre 2026

Après le passage du pilote NVIDIA de `620.70.06` à `620.73.04`,
KDE utilisait bien la RTX 3080. Les Flatpaks Spotify et MPC-Qt n’avaient que
l’ancienne extension graphique et chargeaient les bibliothèques Mesa. Leurs
interfaces tournaient autour de 1 FPS. L’installation de l’extension
`org.freedesktop.Platform.GL.nvidia-620-73-04` a permis de recréer un contexte
OpenGL sur la RTX 3080 dans chacun de leurs environnements Flatpak.

Le catalogue installe Spotify via le dépôt système et MPC-Qt via l’AUR. Ces
deux applications utilisent désormais la pile graphique de l’hôte et ne
dépendent plus de l’extension Flatpak liée à la version du pilote.

Pour les autres Flatpaks, si ce symptôme réapparaît après une mise à jour
NVIDIA, comparer `flatpak --gl-drivers` et
`flatpak list --runtime --columns=ref | grep 'Platform.GL.nvidia'`.
Lancer `flatpak update` après le démarrage sur le nouveau pilote, puis
redémarrer les applications affectées. [Documentation Flatpak](https://docs.flatpak.org/en/latest/extension.html)
