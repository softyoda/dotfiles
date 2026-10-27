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
