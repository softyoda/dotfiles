# Blender Launcher

Installe le paquet AUR `blender-launcher-v2-bin` et son raccourci utilisateur.
L’identifiant `app-blender` est conservé depuis le catalogue des applications,
pour rester compatible avec les profils existants.

## Installation et restauration

```sh
bin/dotctl apply app-blender
```

Quitter complètement Blender Launcher, y compris son icône dans la barre système,
puis le relancer depuis le menu des applications.

Le raccourci définit `PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring`
uniquement pour ce lancement : Blender Launcher ne consulte plus le trousseau
et ne peut plus y enregistrer ses identifiants de proxy. Le trousseau des autres
applications reste inchangé. Un lancement direct de `/usr/bin/blenderlauncher`
ne bénéficie pas de ce réglage.

Pour réactiver le trousseau, supprimer
`~/.local/share/applications/blenderlauncher.desktop` puis relancer l’application.
Réappliquer le module restaure la désactivation.

Le paquet du launcher se met à jour via `cachy-update` lorsque la gestion AUR
est activée et qu’une mise à jour du paquet est disponible. Les versions de
Blender téléchargées sont gérées séparément dans Blender Launcher.

## Choix dans l’installateur

Le socle `app-blender` installe le paquet. La sous-partie
`app-blender/no-keyring`, cochée par défaut, déploie le raccourci sans trousseau.
Elle peut être appliquée seule : `dotctl apply app-blender/no-keyring`.
La décocher évite son déploiement ; cela ne supprime pas un raccourci déjà installé.

## Icône officielle dans We10X

`app-blender/official-icon` remplace uniquement `blender.svg` dans le pack
utilisateur We10X-black. We10X-black-dark partage ce fichier par lien symbolique.
Le thème sélectionné et les autres icônes sont conservés, et les fenêtres Blender
lancées depuis Blender Launcher utilisent aussi cette icône.

Restauration après installation du thème ou réinstallation du pack :

```sh
bin/dotctl apply app-blender/official-icon
```

Le SVG est celui fourni avec la distribution officielle Blender 5.2.2 LTS
(`blender.svg`, également disponible dans le dépôt Blender :
https://projects.blender.org/blender/blender/src/branch/main/release/freedesktop/icons/scalable/apps/blender.svg).
Le logo reste une marque de la Blender Foundation.
Les caches sont rafraîchis à l’application ; relancer Blender si son ancienne
icône reste affichée. Décocher cette option ne restaure pas le dessin du pack :
réinstaller le pack We10X pour le retrouver.
