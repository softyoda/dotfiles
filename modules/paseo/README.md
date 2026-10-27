# Paseo

[Paseo](https://paseo.sh) est une interface unique (appli de bureau + appli web/mobile via
`app.paseo.sh`) pour lancer et suivre des agents de code : un démon local (`127.0.0.1:6767`) pilote
Claude Code, Codex et OpenCode, et le relais permet de les suivre depuis le téléphone.

## Les trois fournisseurs

| Agent dans Paseo | Outil | Compte utilisé | Module |
|------------------|-------|----------------|--------|
| Claude | Claude Code (`~/.local/bin/claude`) | abonnement Claude (Pro/Max) | `claude-code` |
| GPT | Codex (`openai-codex`) | abonnement ChatGPT | `codex` |
| Poe (Opus, DeepSeek…) | OpenCode (`~/.opencode/bin/opencode`) | clé API Poe | `opencode-poe` |

## Ce que fait le module

- installe `paseo-bin` (AUR) ;
- `~/.local/bin/paseo` : wrapper qui retire `ANTHROPIC_*` et `POE_API_KEY` de l’environnement avant
  de lancer `/usr/bin/paseo`, pour que Claude Code utilise l’abonnement et non une clé API héritée ;
- `~/.local/share/applications/paseo.desktop` : surcharge du lanceur système pour passer par ce wrapper ;
- `~/.paseo/config.json` : démon local sur `127.0.0.1:6767`, CORS `https://app.paseo.sh`, relais activé
  (aucun secret) ;
- `~/.config/Paseo/desktop-settings.json` : canal stable, son des notifications, démon géré par l’appli
  et arrêté à la fermeture.

Jamais versionné : `~/.paseo/{daemon-keypair.json,local-credential,push-tokens.json,cli-client-id,server-id}`,
les cookies/stockages de `~/.config/Paseo`.

## Étapes manuelles (nouvelle machine)

1. `claude` puis `/login` (abonnement Claude) ;
2. `codex login` (compte ChatGPT) ;
3. `opencode auth login` → Poe ;
4. lancer Paseo, vérifier que les trois agents sont détectés ;
5. ré-appairer l’appli mobile / web (nouvelle paire de clés du démon).

`config.json` et `desktop-settings.json` peuvent être réécrits par Paseo : en cas de « modifié
localement », `dotctl diff paseo` puis `dotctl capture paseo`.
