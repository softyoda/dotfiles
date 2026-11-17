# Firefox : sauvegarde et restauration sélectives

L'écran **Firefox…** dans Dotfiles, ou `dotctl firefox`, permet de choisir le
profil local et de cocher séparément :

- les préférences `about:config`, sélectionnables une par une, notamment
  `toolkit.tabbox.switchByScrolling` (onglets à la molette) ;
- uBlock Origin : extension, filtres et réglages ;
- Violentmonkey : extension, userscripts, valeurs persistantes et réglages.

Le module ajoute aussi une entrée « Firefox — sauvegarde des réglages » au menu.
Il ne restaure rien sans sélection explicite dans cet écran.

## Mes filtres uBlock Origin

Les filtres perso sont versionnés en clair dans
[`files/ublock-mes-filtres.txt`](files/ublock-mes-filtres.txt) (Twitter, mise
en page classique de YouTube). Pour les remettre sans restaurer tout le profil :
tableau de bord uBlock Origin → **Mes filtres** → coller le contenu du fichier →
**Appliquer les changements**. Après une modification dans uBlock, recopier
l'onglet **Mes filtres** dans ce fichier.

## Mes userscripts Violentmonkey

Le code est versionné ici plutôt que synchronisé en fichier : chaque script
pointe sur sa propre URL `raw` GitHub (`@updateURL` / `@downloadURL`). Pour
l'installer, ouvrir le lien « installer » dans Firefox ; Violentmonkey le met
ensuite à jour tout seul à chaque commit **si `@version` a été incrémentée**.
Les scripts tiers déjà publiés ne sont pas copiés : on les installe depuis leur
source, qui gère leurs mises à jour. Aucun script n'enregistre de valeurs
(`GM_setValue`) ; rien de privé n'est donc perdu en réinstallant.

Versionnés dans [`files/userscripts/`](files/userscripts/) :

| Script | Rôle | État | |
|---|---|---|---|
| X to XCancel Redirect | menu « View on XCancel » sur x.com | actif | [installer](https://raw.githubusercontent.com/softyoda/dotfiles/master/modules/firefox-settings/files/userscripts/x-to-xcancel-redirect.user.js) |
| Epic Games Overflow Fix | corrige le défilement du site Epic Games | actif | [installer](https://raw.githubusercontent.com/softyoda/dotfiles/master/modules/firefox-settings/files/userscripts/epic-games-overflow-fix.user.js) |
| SensCritique on Google Search | bouton SensCritique dans Google (dérivé de *Reddit on Google Search*, MIT) | actif | [installer](https://raw.githubusercontent.com/softyoda/dotfiles/master/modules/firefox-settings/files/userscripts/senscritique-on-google-search.user.js) |
| Original Youtube Audio | force la piste audio originale (auteur : LiefLayer) | actif | [installer](https://raw.githubusercontent.com/softyoda/dotfiles/master/modules/firefox-settings/files/userscripts/original-youtube-audio.user.js) |
| Redirect translated Reddit post to original | retire la traduction automatique de Reddit (auteur : neozetare) | actif | [installer](https://raw.githubusercontent.com/softyoda/dotfiles/master/modules/firefox-settings/files/userscripts/reddit-redirect-translated-to-original.user.js) |
| Calculating Empires – Tile Crawler | parcours et téléchargement des tuiles de calculatingempires.net | désactivé | [installer](https://raw.githubusercontent.com/softyoda/dotfiles/master/modules/firefox-settings/files/userscripts/calculating-empires-tile-crawler.user.js) |

Installés depuis leur source :

| Script | État | Source |
|---|---|---|
| DuckDuckGo to Google shortcut (and viceversa) | actif | [Greasy Fork 27892](https://greasyfork.org/scripts/27892) |
| Google Search Domain Button – Robust Version | actif | [Greasy Fork 500508](https://greasyfork.org/scripts/500508) |
| Reddit on Google Search | actif | [Greasy Fork 462356](https://greasyfork.org/scripts/462356) |
| Blue Marble (wplace.live) | actif | [GitHub SwingTheVine/Wplace-BlueMarble](https://github.com/SwingTheVine/Wplace-BlueMarble) |
| sketchfab (téléchargement de modèles) | désactivé | [Greasy Fork 492877](https://greasyfork.org/scripts/492877) |
| DuckDuckGo Extended | désactivé, source morte | userscripts-mirror.org, script 129505 |
| Reddit Place – Armée de Kameto | désactivé, événement terminé | [GitHub CorentinGC/reddit-place-kcorp](https://github.com/CorentinGC/reddit-place-kcorp) |
Le module « Firefox : second profil » sert uniquement à créer un autre profil.

## Sauvegarder

1. Configurer le dossier privé dans `~/.config/dotfiles/private-path`.
2. Fermer le profil Firefox concerné. L'outil vérifie le verrou de Firefox.
3. Ouvrir **Firefox…**, sélectionner le profil et les données souhaitées.
4. Cliquer sur **Sauvegarder la sélection** ; chaque sauvegarde est datée.
5. Vérifier dans Seafile que le dossier privé est effectivement synchronisé.

Les profils Firefox classique et Nightly restent séparés. Ne pas sélectionner
Violentmonkey pour un profil où il n'est pas installé.
Les préférences proposées couvrent les onglets, la molette, le défilement,
l'accessibilité et plusieurs réglages d'interface ; elles ne représentent pas
l'intégralité du profil Firefox. L’option « Afficher aussi les autres préférences »
permet de sélectionner des clés supplémentaires ; elles sont décochées par défaut
car certaines sont internes ou propres à une machine. Les cookies, mots de passe et sessions ne sont
pas sauvegardés. Les personnalisations `userChrome.css` ne sont pas incluses.

## Restaurer sur un autre ordinateur

1. Synchroniser la bibliothèque privée et configurer `private-path`.
2. Installer Firefox et le lancer une fois pour créer son profil, puis le fermer.
3. Ouvrir **Firefox…**, choisir le profil cible et une sauvegarde.
4. Cocher les éléments souhaités. Pour les préférences, choisir
   « Préférences de la sauvegarde » puis les clés à restaurer.
5. Cliquer sur **Restaurer la sélection**, puis relancer Firefox. Si Firefox
   demande d'activer les extensions restaurées, le faire dans `about:addons`.

La restauration fusionne uniquement les préférences choisies et remplace les
données des extensions sélectionnées. Une copie des fichiers remplacés est
conservée dans `dotfiles-backups/<date>/` à l'intérieur du profil ; `restore.json`
liste les chemins concernés et indique lesquels n'existaient pas auparavant.
En cas d'erreur pendant l'écriture, ces fichiers sont remis en place automatiquement.

Les extensions utilisent le stockage Firefox d'origine, avec leur UUID et leur
XPI signé. Restaurer vers une version de Firefox au moins aussi récente que la
source ; ce format ne vise ni Chromium ni une ancienne version de Firefox.
Ne pas modifier simultanément les données depuis plusieurs machines : il s'agit
de sauvegardes datées et d'une restauration explicite, pas d'une fusion en direct.

## Confidentialité et synchronisation

Les sauvegardes sont dans `<dossier privé>/firefox/`, jamais dans GitHub public.
Elles peuvent contenir des sites privés et des valeurs enregistrées par les
userscripts : utiliser la bibliothèque Seafile **chiffrée** prévue pour les
configurations privées. Le bouton **Synchroniser** de Dotfiles fait un `git pull`
des vrais dépôts Git ; il ne transfère pas les fichiers d'une bibliothèque Seafile.
La présence locale d'une sauvegarde n'est pas une preuve de transfert distant.
