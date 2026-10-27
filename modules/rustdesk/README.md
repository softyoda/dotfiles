# RustDesk

- Paquet AUR `rustdesk-bin`, service système `rustdesk.service` activé
  (le serveur tourne même sans session graphique ouverte).
- Options posées dans `~/.config/rustdesk/*.toml` (section `[options]`, clé par
  clé, sans toucher au reste du fichier) :
  - `allow-linux-headless = Y` : connexion possible sans session ouverte ;
  - `verification-method = use-permanent-password` : seul le mot de passe
    permanent est accepté (pas de mot de passe à usage unique) ;
  - `enable-check-update = N` : pas de vérification de mise à jour (gérée par paru).
- Serveur : les serveurs publics RustDesk (la valeur `rendezvous_server` du
  fichier est choisie automatiquement par RustDesk, ce n’est pas un réglage).
  Pour un serveur auto-hébergé : `RUSTDESK_SERVER=hôte dotctl apply rustdesk`.

## Jamais dans le dépôt

`RustDesk.toml` (identifiant chiffré, mot de passe, sel, paire de clés),
`2fa`, `access_token`, `trusted`, `peers/`, carnet d’adresses : propres à la
machine et secrets.

## Étapes manuelles

1. Définir le mot de passe permanent (au choix) :
   - interface : Paramètres → Sécurité → « Définir le mot de passe permanent » ;
   - terminal : `sudo rustdesk --password 'MotDePasse'`.
2. Noter l’ID affiché (`rustdesk --get-id`) pour s’y connecter depuis un autre appareil.
3. Facultatif : se connecter à son compte RustDesk et activer la double authentification
   (Paramètres → Sécurité).
