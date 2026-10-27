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

## Bibliothèque privée et copie locale

Créer la bibliothèque **chiffrée depuis le client de bureau**, puis synchroniser
`dotfiles-private` dans le dossier Seafile local. Si une création affiche une
erreur serveur, actualiser la liste avant de réessayer : la bibliothèque peut
avoir été créée avant l'échec d'une opération secondaire.

Après synchronisation, inscrire son chemin local dans
`~/.config/dotfiles/private-path`. Migrer les données de l'ancien dossier privé
après comparaison des fichiers ; vérifier dans Seafile le transfert terminé
avant de retirer les anciennes copies. Ne jamais publier ces données sur GitHub.

Le chiffrement de bibliothèque protège le contenu stocké sur le serveur. Les
noms de fichiers et métadonnées restent visibles. Les fichiers synchronisés sur
un ordinateur sont déchiffrés : protéger aussi le compte local et le disque, ou
utiliser un coffre chiffré local verrouillable pour les données qui le nécessitent.
Ne pas placer la copie déchiffrée dans un partage SMB accessible aux autres utilisateurs.

Révoquer une session/un appareil empêche ses prochains accès autorisés au
serveur, mais ne retire pas les fichiers déjà copiés. Un effacement distant,
lorsqu'il est disponible, dépend du client qui se reconnecte ; ce n'est pas un
verrouillage cryptographique des copies hors ligne. Un portail de raccourcis
n'ajoute pas cette protection aux applications qu'il référence.

Les bases SQLite et index utilisés par un service NAS doivent rester dans ses
volumes privés, hors des partages collectifs. Synchroniser des sauvegardes
cohérentes (application arrêtée ou API de sauvegarde), pas leurs fichiers actifs.
Un service qui recherche ou traite ces données sur le NAS doit pouvoir les lire :
le chiffrement E2E Seafile ne protège pas cette copie de travail contre le serveur.

Références : [bibliothèques chiffrées](https://help.seafile.com/security_and_encryption/use_encrypted_libraries/),
[limites du chiffrement](https://manual.seafile.com/latest/administration/security_features/).

## Dépannage serveur : création réussie suivie d'une erreur

Une erreur SQL `1045 Access denied` dans `repo_created_cb` / `seafevents` peut
provenir d'un mot de passe MariaDB obsolète dans `seafevents.conf`, alors que
`seafile.conf` et `seahub_settings.py` utilisent le bon identifiant.

Avant toute modification, comparer les hôtes/comptes et tester la connexion
sans afficher les secrets. Vérifier aussi si la bibliothèque existe déjà et si
elle est chiffrée. Sauvegarder le fichier, aligner uniquement l'identifiant de
la base des événements avec celui validé, puis redémarrer Seafile. Contrôler la
connexion et l'API après redémarrage. Ne pas modifier les identifiants MariaDB
ni recréer la bibliothèque pour contourner cette erreur.
