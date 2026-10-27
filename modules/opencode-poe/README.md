# OpenCode (Poe)

OpenCode sert **uniquement pour Poe** (Claude passe par Claude Code + abonnement, GPT par Codex +
ChatGPT). Il est piloté depuis Paseo (module `paseo`) ou lancé directement avec `opencode`.

## Ce que fait le module

- installe OpenCode avec l’installeur officiel
  (`curl -fsSL https://opencode.ai/install | bash -s -- --no-modify-path` → `~/.opencode/bin/opencode`) ;
- ajoute `~/.opencode/bin` au PATH via `~/.config/fish/conf.d/opencode.fish`
  (la ligne `fish_add_path ~/.opencode/bin` de l’ancien `config.fish` devient inutile) ;
- configure `~/.config/opencode` selon deux modes :

| Mode | Condition | Résultat |
|------|-----------|----------|
| **a — partagé** | var `OPENCODE_SHARED_CONFIG` définie et dossier accessible | `opencode.jsonc`, `agent/`, `plugin/`, `skills/` deviennent des liens vers ce dossier (NAS) |
| **b — autonome** | sinon | copie de `files/standalone/` (agents, plugins, `CODING-RULES.md`, `opencode.jsonc`) |

Le mode **a** suppose le NAS monté : appliquer aussi le module `nas-mounts` (non déclaré en
dépendance pour que le mode b reste possible sur une machine sans NAS). Si le dossier partagé est
inaccessible au moment de l’application, le module se rabat sur le mode b.

Variables (profil privé `[vars]`, toutes optionnelles) :

```toml
OPENCODE_SHARED_CONFIG = "/mnt/nas/03_Shared/Config/Opencode"
LLM_SERVER_URL = "http://flystation.local:8081/v1"   # LLM local (mode b), défaut http://localhost:8081/v1
```

Copie autonome = config du NAS assainie : la clé Poe littérale est remplacée par
`{env:POE_API_KEY}`, l’URL du provider `qwen-local` par `${LLM_SERVER_URL}`, les chemins NAS par
`~/.config/opencode`. Non repris : `MEMORY*.md` (notes personnelles/infra), `SHARED-CONFIG.md` et
`SETUP-STATUS.md` (notes de l’installation partagée), le plugin `session-sync.ts` (export des
sessions vers le NAS).

## Clé Poe (secret)

Au choix :

1. **recommandé** : `opencode auth login` → choisir *Poe* → coller la clé
   (stockée dans `~/.local/share/opencode/auth.json`, jamais versionné) ;
2. variable d’environnement pour le provider `anthropic` → `api.poe.com` de `opencode.jsonc`
   (`"apiKey": "{env:POE_API_KEY}"`) : dans `~/.config/fish/secrets.fish` (non commité, lu par
   `config.fish`) :

   ```fish
   set -gx POE_API_KEY "…"
   ```

   Le wrapper Paseo et `claude-subscription.fish` (module `claude-code`) retirent `POE_API_KEY` de
   l’environnement de Claude Code ; dans Paseo, OpenCode doit donc s’appuyer sur `opencode auth login`.

## ⚠ Clé en clair sur le NAS

Le fichier partagé `/mnt/nas/03_Shared/Config/Opencode/opencode.jsonc` contient actuellement la clé
Poe **en clair** dans `provider.anthropic.options.apiKey`. La remplacer par `"{env:POE_API_KEY}"`
(et définir la variable comme ci-dessus) ; `apply.sh` le signale tant que ce n’est pas fait.
De même, `SHARED-CONFIG.md` sur le NAS contient un mot de passe SMB en clair : à retirer.

## Dépendances des plugins

`package.json` (`@opencode-ai/plugin`) est copié s’il manque ; OpenCode installe lui-même les
dépendances dans `~/.config/opencode/node_modules` au démarrage. Les serveurs MCP de la config
utilisent `npx` (paquet `nodejs`/`npm`).
