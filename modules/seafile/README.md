# Seafile

- Flatpak `com.seafile.Client` (installation système).
- Démarrage automatique (`seafile-applet`) avec la fenêtre principale masquée :
  le client reste dans la barre système.
- Adresse du serveur pré-remplie depuis la variable `SEAFILE_SERVER_URL` du
  profil privé (ex. `https://cloud.exemple.fr/`).

## Étapes manuelles

1. Lancer Seafile : au premier démarrage il demande le dossier où ranger les
   bibliothèques (ici `~/seafile_<serveur>/Seafile`).
2. Se connecter : Compte → Ajouter un compte → serveur pré-rempli, identifiant,
   mot de passe (et code 2FA éventuel). Le jeton de session n’est jamais sauvegardé ici.
3. Choisir les bibliothèques à synchroniser (clic droit → Synchroniser).
