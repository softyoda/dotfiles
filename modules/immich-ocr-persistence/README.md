# Préférence OCR Immich et maintenance

Le bouton OCR conserve son état dans le stockage local du navigateur, entre
photos et après fermeture. Il reste initialement désactivé. Seules les zones
OCR déjà disponibles sont affichées : aucun travail ML supplémentaire.

Le correctif vérifie la structure du bundle compilé, conserve un original et
régénère gzip/Brotli. Il est idempotent, testé sur Immich v3.4.1.
Une structure incompatible laisse Immich démarrer avec l'interface standard
et produit un avertissement. Après installation : recharger sans cache
(Ctrl+Maj+R). Le choix est propre au navigateur et à l'adresse du site.

## Restauration

Configurer les valeurs dans le profil privé :
- IMMICH_UPDATE_LOCAL_STACK : stack Compose locale des workers.
- IMMICH_UPDATE_NAS_STACK : stack Immich sur le NAS.
- IMMICH_UPDATE_NAS_SSH : alias SSH du NAS.
- IMMICH_UPDATE_SERVER_URL : URL Immich accessible depuis le NAS et le PC.
- IMMICH_UPDATE_WORKER_PING : URL /ping du moteur ML du PC.
- IMMICH_UPDATE_DOCKGE_STACK : chemin de la stack Immich vu dans Dockge.
- IMMICH_UPDATE_DOCKGE_HOST_STACK : chemin de la stack Dockge sur le NAS.

Examiner avec « dotctl plan immich-ocr-persistence --json », puis appliquer
avec « dotctl apply immich-ocr-persistence ». Les Compose sont sauvegardés.
Seuls Immich serveur, microservices et Dockge sont recréés, sans mise à jour
de version. Un raccourci de bureau et un timer utilisateur sont installés.

Prérequis : noms de conteneurs standard (immich-server, immich-db,
immich-microservices, immich-machine-learning, dockge), Docker local,
sudo Docker via SSH sur le NAS, Python YAML sur le NAS, Node/start.sh dans
Immich et flock dans Dockge. Formats Compose inconnus : arrêt sans écrasement.
Ne pas appliquer simultanément l'ancien module immich-worker qui déplace la
stack locale.

## Boutons de mise à jour

Le bouton existant de la zone de notification utilise immich-update.py.
Le nouveau raccourci « Mettre à jour Immich » ouvre une confirmation.

Dans Dockge, stack Immich, utiliser le bouton existant **Mettre à jour**.
Il exécute la procédure côté NAS, même si le PC est éteint, sous l'authentification
Dockge. Aucun endpoint HTTP de mise à jour ni clé supplémentaire n'est créé.
Les autres stacks gardent leur comportement habituel.

Les deux boutons utilisent la même procédure sous verrou flock :
téléchargement, sauvegarde PostgreSQL, pause confirmée des microservices
(ou ML hors ligne), bascule du serveur, contrôle de santé et du correctif OCR.
Les versions majeures et rétrogradations sont refusées.

Un garde arrête les microservices lors d'une maintenance et empêche leur
démarrage sur une version différente du NAS. Le timer utilisateur vérifie
l'alignement chaque minute et télécharge les images à leur retour.
Les workers volontairement arrêtés ne sont pas redémarrés. Sans session
utilisateur, le garde attend jusqu'au prochain alignement.

## Contrôles et dépannage

- immich-update.py --check : préflight, aucune mise à jour.
- immich-update.py --resume : reprendre après diagnostic, seulement si le serveur est sain.
- immich-update.py --align-only : alignement local uniquement.
- immich-ocr-hook --check : vérifier/réappliquer le correctif OCR.
- journalctl --user -u immich-worker-align.service : alignement local.
- Terminal Dockge et logs des conteneurs : maintenance et garde.
- node modules/immich-ocr-persistence/test.cjs : tests de préférence.
  Un chemin de bundle original peut être ajouté pour vérifier la version réelle.

Après une interruption, les workers peuvent rester en pause : examiner la
version et la santé du serveur avant de reprendre. Ne jamais rétrograder
automatiquement la base après migration. Les sauvegardes DB et Compose restent
sur le NAS.

Retrait : désactiver le timer, restaurer les Compose pré-ocr/pré-immich en
préservant les modifications ultérieures, puis recréer ces services.
Retirer seulement les fichiers montés sans retirer les commandes personnalisées
empêcherait le démarrage. L'image officielle sans hook rétablit le web original.

Le hook Dockge est également réappliqué à son démarrage. Si son code devient
incompatible, Dockge démarre normalement et signale que son action Immich
personnalisée est indisponible ; utiliser le bouton du bureau dans ce cas.

Validation : tests OCR sur le bundle réel, tests simulés de mise à jour avec
worker présent/absent, refus sans accusé de pause et sauvegarde en échec,
puis pause/reprise réelle sans changement de version et vérification HTTP gzip.
