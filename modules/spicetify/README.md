# Spotify + Spicetify

- **Spotify** : Flatpak `com.spotify.Client` installé **en mode utilisateur**
  (`~/.local/share/flatpak`) : Spicetify doit pouvoir modifier les fichiers de
  l’application, ce qu’une installation `--system` interdit sans root.
- **Spicetify** : CLI officiel dans `~/.spicetify` (version épinglée dans
  `apply.sh`, mise à jour ensuite par `spicetify update`). Le paquet AUR
  `spicetify-cli` n’est pas utilisé (installé dans `/opt`, géré par pacman).
  `~/.spicetify` est ajouté au PATH par la config fish.
- **Marketplace** : application personnalisée + thème « marketplace » (thèmes et
  extensions se choisissent ensuite depuis le Marketplace, dans Spotify).
- Réglages notables : `experimental_features`, `home_config`, `expose_apis`,
  `disable_sentry`, `disable_ui_logging` ; chemins vers le Flatpak utilisateur.
  Ils sont posés clé par clé avec `spicetify config` (la section `[Backup]` du
  fichier est gérée par spicetify).

## Ré-application automatique

`spicetify-reapply.path` (systemd utilisateur) surveille le dossier de
déploiement Flatpak de Spotify ; à chaque mise à jour il lance
`~/.local/bin/spicetify-reapply` (`spicetify backup apply`, en fermant Spotify
si besoin ; ne fait rien si l’appli est déjà patchée).

À la main : `spicetify-reapply`, ou `spicetify restore` pour revenir à Spotify d’origine.

## Première installation

Spotify doit avoir été lancé une fois (fichier `prefs` créé) avant le premier
patch : sinon `apply.sh` le signale ; lancer Spotify, se connecter, puis
relancer `dotctl apply spicetify`.
