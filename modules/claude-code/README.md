# Claude Code (abonnement)

Claude Code s’utilise avec l’**abonnement** Anthropic (Pro/Max) — plus via Poe,
claude-code-router (CCR) ni le proxy claude-cache-fix (abandonnés et retirés du repo).

## Ce que fait le module

- installe Claude Code avec l’installeur natif officiel :
  `curl -fsSL https://claude.ai/install.sh | bash`
  (binaire dans `~/.local/share/claude/versions/`, lien `~/.local/bin/claude`, mises à jour automatiques) ;
- déploie `~/.claude/settings.json` (langue, modèle, permissions, hook de contrôle des commandes `gh`,
  `SUDO_ASKPASS=ksshaskpass`) ;
- déploie l’agent `~/.claude/agents/gemini.md` ;
- déploie `~/.config/fish/conf.d/claude-subscription.fish`, qui supprime `ANTHROPIC_API_KEY`,
  `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_BASE_URL`, `ANTHROPIC_CUSTOM_HEADERS` et `POE_API_KEY`
  hérités d’une ancienne session : sinon Claude Code utiliserait la clé API au lieu de l’abonnement.
  (Les fichiers de `conf.d` sont lus *avant* `config.fish` : un `POE_API_KEY` défini dans
  `~/.config/fish/secrets.fish` reste donc disponible pour OpenCode.)

## Étape manuelle

```fish
claude          # puis /login → compte Claude (abonnement)
```

Les identifiants (`~/.claude/.credentials.json`, `~/.claude.json`) ne sont jamais versionnés.

## Notes

- `settings.json` est réécrit par Claude Code lui-même (`/config`, thème, modèle…) : en cas de
  « modifié localement », `dotctl diff claude-code` puis `dotctl capture claude-code`.
- `~/.claude/settings.local.json` reste local (non géré).
- La permission `sudo -n /usr/local/bin/hdmi-redetect` ne sert que sur la machine qui a ce script ;
  elle est sans effet ailleurs.
- L’agent `gemini.md` contient encore la balise `<CCR-SUBAGENT-MODEL>` de l’époque CCR : sans CCR
  elle est ignorée, et l’agent ne fonctionne que si le modèle indiqué est accessible.
- Le hook `gh` utilise `jq`.
