# Vesktop

- Paquet AUR `vesktop` (client Discord avec Vencord intégré).
- `~/.config/vesktop/settings.json` : réduction dans la barre système, arRPC
  (statut de jeu), correcteur orthographique français, couleurs de l’écran de démarrage.
- Lanceur `~/.local/share/applications/vesktop.desktop` et démarrage
  automatique réduit (`--start-minimized`) : tous deux lancés via
  `mullvad-exclude` quand Mullvad est installé (Discord hors tunnel VPN),
  sinon lancement direct. Relancer le module après avoir installé/retiré Mullvad.
- Gestionnaire par défaut des liens `discord://`.

Non sauvegardé : `sessionData/` (session Discord, jetons) — se reconnecter à la
main. Les réglages Vencord (`settings/settings.json`) sont ceux par défaut ;
pour les synchroniser, utiliser la synchro cloud de Vencord (Paramètres → Vencord → Cloud).
