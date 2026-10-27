# Shell fish

- `~/.config/fish/config.fish` : charge la config CachyOS (`cachyos-fish-config`), met
  `~/.local/bin` en tête du PATH (une seule fois), source `secrets.fish`, ajoute
  `~/.spicetify` et `~/.opencode/bin` s'ils existent.
- `~/.config/fish/functions/fish_user_key_bindings.fish` : raccourcis fzf
  (Ctrl+R historique, Ctrl+T fichiers, Alt+C dossiers).
- Prompt **Pure**, **autopair** et notifications **done** (fin des commandes longues) :
  fournis par les paquets `fish-pure-prompt`, `fish-autopair` et `cachyos-fish-config`
  (dépôts CachyOS), pas par fisher. Réglages Pure = valeurs par défaut. `fisher` est
  installé pour d'éventuels plugins supplémentaires : s'ils sont listés dans
  `~/.config/fish/fish_plugins`, `apply.sh` lance `fisher update`.
- Shell de connexion passé à fish (`chsh`) si ce n'est pas déjà le cas.

## Secrets

`~/.config/fish/secrets.fish` contient les clés API (`set -gx NOM valeur`). Il n'est **jamais**
commité : `apply.sh` le crée vide (droits 600) depuis `files/secrets.fish.example` s'il
n'existe pas. Les variables propres à un outil (ex. Claude) sont gérées par leur module
(`conf.d/…`), pas ici.

Sur Arch sans dépôts CachyOS, `cachyos-fish-config`, `fish-pure-prompt` et `fish-autopair`
n'existent pas : installer `pure-fish/pure` et `jorgebucaran/autopair.fish` via fisher.
