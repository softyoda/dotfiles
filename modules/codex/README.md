# Codex (ChatGPT)

Codex CLI d’OpenAI, utilisé avec l’**abonnement ChatGPT** (pas de clé API).

## Ce que fait le module

- installe le paquet `openai-codex` (dépôt CachyOS) ;
- crée `~/.codex/config.toml` à partir de `files/config.toml` s’il n’existe pas ;
  sinon ajoute seulement les clés manquantes `model_context_window = 872000` et
  `model_auto_compact_token_limit = 800000` (Codex réécrit ce fichier : projets de confiance, TUI…).

Non versionné : projets de confiance (`[projects."…"]`, propres à la machine) et le serveur MCP
Blender, qui pointe vers le venv d’un projet local (exemple commenté dans `files/config.toml`).

## Étape manuelle

```fish
codex login     # ouvre le navigateur → compte ChatGPT
```

`~/.codex/auth.json` contient les jetons : jamais versionné.
