# Écrire un module

Un module = une fonctionnalité réinstallable : `modules/<id>/` (id en kebab-case).

```
modules/<id>/
├── module.toml   # obligatoire
├── apply.sh      # optionnel : étapes après le déploiement des fichiers
├── check.sh      # optionnel : exit 0 si la fonctionnalité est en place
├── README.md     # optionnel : notes, étapes manuelles, aide-mémoire
└── files/        # fichiers déployés par [[files]]
```

## module.toml

```toml
name = "Nom lisible"
category = "kde"            # base | kde | hardware | apps | ai | creative | retro | homelab
description = "Une phrase : ce que ça fait pour l'utilisateur."
requires = ["autre-module"] # dépendances (appliquées avant)
vars = ["NAS_HOST"]         # variables NON secrètes, fournies par le profil privé [vars]
secrets = ["SMB_PASSWORD"]  # secrets, lus dans ~/.config/dotfiles/secrets.env (jamais commités)
manual = true               # s'il reste des étapes manuelles (décrites dans README.md)

[packages]
pacman = ["xpadneo-dkms"]
aur = ["xone-dkms"]
flatpak = ["com.spotify.Client"]

[[files]]                   # copiés tels quels (sauvegarde .bak-AAAAMMJJ si différent)
src = "files/power.conf"
dst = "/etc/systemd/logind.conf.d/power.conf"   # ~ et ${VAR} acceptés
root = true                 # déployé via sudo install -D
mode = "644"                # optionnel
template = true             # optionnel : ${VAR} remplacés par les vars/secrets
```

## Ordre d'application

1. paquets (pacman → AUR via paru → flatpak), groupés pour tous les modules sélectionnés
2. `[[files]]`
3. `apply.sh` avec `DOTFILES`, `MODULE_DIR`, `DOTFILES_LIB` et les vars/secrets dans l'environnement

`apply.sh` doit être **idempotent** (relançable sans casse). Commencer par
`source "$DOTFILES_LIB"` pour `as_root`, `enable_user`, `enable_system`, `need_vars`,
`ensure_groups`, `ensure_line_root`, `info/success/warn/error`.

## Statut (dotctl status / interface)

- **non installé** : paquet manquant, `check.sh` en échec, ou fichiers absents
- **à jour** : tout correspond
- **mise à jour dispo** : le module a changé dans le repo depuis la dernière application
- **modifié localement** : un fichier déployé a été modifié sur la machine →
  `dotctl diff <id>` puis `dotctl capture <id>` pour le remonter dans le repo

## Règles

- Jamais de secret, clé, mot de passe, jeton, IP publique, nom de compte dans le repo public.
  Les valeurs machine (hôtes, IP LAN, UUID disques…) vont dans le **profil privé** via `vars`.
- Les fichiers de config KDE se règlent de préférence avec `kwriteconfig6` dans `apply.sh`
  (clé par clé) plutôt qu'en écrasant un rc entier.
- Pas de binaires lourds : télécharger dans `apply.sh` (URL + version épinglée).
- Les applis « juste un paquet » vont dans `catalog/apps.toml`, pas dans un module.
