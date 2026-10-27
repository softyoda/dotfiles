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

## Sous-parties sélectionnables

Une sous-partie possède un identifiant stable `module/partie`. Elle réutilise le
dossier du module et son README, mais déclare ses propres fichiers, dépendances,
paquets et scripts. Le module parent constitue le **socle commun** : ses paquets,
fichiers et éventuel `apply.sh` sont appliqués avant chaque sous-partie.

```toml
[[parts]]
id = "autostart"
name = "Démarrer à l’ouverture de session"
description = "Ajoute le raccourci de démarrage automatique."
default = true
# requires = ["autre-module"]
# apply = "configure-autostart.sh"
# check = "check-autostart.sh"

[[parts.files]]
src = "files/app.desktop"
dst = "~/.config/autostart/app.desktop"
```

- `dotctl apply module/partie` applique le socle, les dépendances déclarées et
  **cette seule partie**, jamais ses sœurs.
- `dotctl apply module` applique le socle et les parties choisies dans le dossier
  privé ; sans choix enregistré, il prend celles avec `default = true`.
- `dotctl configure module --parts none` choisit uniquement le socle.
- Décocher ne désinstalle rien. Une opération de retrait doit être implémentée
  explicitement ; ne jamais faire supprimer des fichiers implicitement.
- Les scripts parent ne sont pas hérités comme scripts enfants. Déplacer les
  effets optionnels de l'ancien `apply.sh` vers les scripts des parties.
- Ne pas découper arbitrairement un script en cases : déclarer les dépendances
  nécessaires et conserver ensemble les fichiers qui doivent rester cohérents.
- Les empreintes des sous-parties concernent leur propre déclaration, fichiers et
  scripts. Modifier une sœur ne force pas leur réapplication.

## Champs de formulaire

Les `vars` et `secrets` existants donnent automatiquement des champs texte ou
masqués. Déclarer `[[inputs]]` (ou `[[parts.inputs]]`) pour préciser les libellés,
les types et les validations :

```toml
[[inputs]]
key = "SHARED_CONFIG"
label = "Dossier de configuration privée"
type = "path"
path_kind = "directory" # ou file
must_exist = true
required = false
help = "Laisser vide pour une configuration autonome."

[[inputs]]
key = "HIDE_WINDOW"
label = "Masquer la fenêtre au démarrage"
type = "bool"
default = true
```

Types : `text`, `path`, `bool`, `choice` (avec `choices = ["a", "b"]`),
`integer`, `secret`. Une expression régulière `pattern` peut valider du texte.
Ne jamais fournir de valeur par défaut à un secret. `HOME`, `PATH`, `USER`,
`UID`, `DOTFILES`, `MODULE_DIR` et `DOTFILES_LIB` sont réservées.
Les booléens deviennent les chaînes `true` / `false` dans les scripts.

L'interface enregistre les champs modifiés et les choix dans
`<dossier privé>/settings/<hostname>.json`, avec permissions `600`. Les secrets
y sont séparés des variables et ne sont jamais imprimés par les exports JSON
ou l'aperçu. Le client Seafile assure la synchronisation de ce fichier.
Les réglages sont propres à une machine : ils ne configurent pas silencieusement
une autre workstation. Les agents peuvent préparer ses valeurs dans le fichier
correspondant, sans y recopier des chemins inadaptés.

Priorité des valeurs : profil `[vars]`, fichiers `secrets.env`, puis réglages de
l'interface pour cette machine ; les valeurs par défaut complètent les absences.
Une modification de champs déjà appliqués est détectée dans le statut du module.
Les valeurs privées ne vont jamais dans un manifeste ou fichier Git public.

## Interface, agents et CLI

Le bouton **Configurer…** ouvre les champs et sous-parties, le README et l'aperçu.
**Enregistrer les choix** ne déploie rien ; **Appliquer cette sélection** déploie
le module et ses dépendances après confirmation. Chaque ligne permet de copier
son ID ou une référence complète pour un agent. **Dossier privé…** configure le
chemin local de la bibliothèque déjà synchronisée ; il ne connecte pas Seafile
au compte et ne connaît pas son mot de passe de chiffrement.

```sh
# Découvrir le catalogue et ses schémas sans exposer les valeurs privées
dotctl list --json
dotctl info seafile/client-settings --json

# Enregistrer un choix et des champs, sans application
dotctl configure seafile --parts autostart,client-settings \
  --set SEAFILE_SERVER_URL=https://cloud.example.org --set SEAFILE_HIDE_WINDOW=true

# Examiner puis appliquer une seule sous-partie
dotctl plan paseo/launcher --json
dotctl apply paseo/launcher
dotctl status paseo/launcher

# Remonter uniquement ses fichiers non templates pour une revue par l'agent
dotctl diff paseo/launcher
dotctl capture paseo/launcher
```

`--values-file /chemin/prive/valeurs.json` accepte un objet de valeurs ; `-` lit
stdin. Utiliser ce mécanisme ou le formulaire pour les secrets : `--set` les
refuse pour éviter leur présence dans l'historique du shell ou la liste des
processus. `configure` valide les champs fournis ; `plan` signale les champs
obligatoires manquants, et `apply` refuse les parties concernées.

**Synchroniser** récupère les changements Git ; **Appliquer** les déploie ;
**capture** remonte les fichiers locaux dans le checkout de l'agent. Aucune de
ces commandes ne crée automatiquement de commit. L'agent vérifie le diff,
écarte toute donnée privée, puis committe et pousse selon `AGENTS.md`.
