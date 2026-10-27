# Firefox : sauvegarde et restauration sélectives

L'écran **Firefox…** dans Dotfiles, ou `dotctl firefox`, permet de choisir le
profil local et de cocher séparément :

- les préférences `about:config`, sélectionnables une par une, notamment
  `toolkit.tabbox.switchByScrolling` (onglets à la molette) ;
- uBlock Origin : extension, filtres et réglages ;
- Violentmonkey : extension, userscripts, valeurs persistantes et réglages.

Le module ajoute aussi une entrée « Firefox — sauvegarde des réglages » au menu.
Il ne restaure rien sans sélection explicite dans cet écran.
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
