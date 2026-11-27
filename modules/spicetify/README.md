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
mise à jour et le patch sont reportés au prochain lancement. Spotify fermé,
`spicetify-reapply` peut également appliquer le patch à la main.

Le champ Spicetify `prefs_path` pointe vers un fichier dédié, généré à partir
de la version que Spotify Launcher vient d’installer. Cela permet de patcher
la bonne version avant son premier démarrage et préserve les préférences de
Spotify.

Pour reprendre des réglages d’une ancienne installation Flatpak, quitter
l’ancien client, sauvegarder la configuration native existante et copier le
contenu de `~/.var/app/com.spotify.Client/config/spotify/` dans
`~/.config/spotify/`. Les thèmes, extensions et réglages Spicetify restent
dans `~/.config/spicetify`. Retirer ensuite les copies Flatpak de Spotify et
de MPC-Qt une fois les versions natives vérifiées.

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
