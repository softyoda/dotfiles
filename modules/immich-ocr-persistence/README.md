# Préférence OCR Immich et maintenance

Le bouton OCR conserve son état dans le stockage local du navigateur, entre
photos et après fermeture. Il reste initialement désactivé. Seules les zones
OCR déjà disponibles sont affichées : aucun travail ML supplémentaire.

Le correctif vérifie la structure du bundle compilé, conserve un original et
régénère gzip/Brotli. Il est idempotent, testé sur Immich v3.4.1.
Le panneau de droite affiche désormais « Texte reconnu » et « Tout copier »,
indépendamment de la visibilité des cadres sur la photo.
Une structure incompatible désactive l'extension (panneau et préférence) ;
Immich démarre avec son interface standard et produit un avertissement. Après installation : recharger sans cache
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
de version. Un timer utilisateur est installé. Aucun raccourci n’est créé sur le bureau.

Prérequis : noms de conteneurs standard (immich-server, immich-db,
immich-microservices, immich-machine-learning, dockge), Docker local,
sudo Docker via SSH sur le NAS, Python YAML sur le NAS, Node/start.sh dans
Immich et flock dans Dockge. Formats Compose inconnus : arrêt sans écrasement.
Ne pas appliquer simultanément l'ancien module immich-worker qui déplace la
stack locale.

## Boutons de mise à jour

Le bouton existant de la zone de notification utilise immich-update.py.
La mise à jour reste accessible depuis l’icône de l’application microservices
dans la zone de notification.

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
personnalisée est indisponible ; utiliser le bouton de l’application microservices dans ce cas.

Validation : tests OCR sur le bundle réel, tests simulés de mise à jour avec
worker présent/absent, refus sans accusé de pause et sauvegarde en échec,
puis pause/reprise réelle sans changement de version et vérification HTTP gzip.


## Texte reconnu et sécurité

Le panneau reprend la police héritée, les marges et la sobriété du menu.
Le panneau se place sous le titre Information, uniquement pour une photo avec
des résultats OCR déjà chargés par le gestionnaire du visualiseur. Il n'appelle
aucune API, ne lit aucun jeton et ne déclenche aucun travail ML. La transcription
n'est ni stockée dans le navigateur ni envoyée à un service externe.
Seule la préférence booléenne d'affichage des cadres reste dans localStorage.

Les textes passent uniquement par textarea.value et textContent, jamais par
innerHTML, un interpréteur Markdown ou une URL. Aucune permission Immich,
politique CSP, authentification ou route réseau n'est modifiée. La copie
utilise navigator.clipboard.writeText seulement à la suite d'un clic explicite.
En cas de refus du navigateur, le texte est sélectionné pour Ctrl+C.
Les raccourcis du visualiseur sont neutralisés dans le champ de texte.

Les zones sont regroupées par ligne puis triées de gauche à droite ; l'ordre
des colonnes complexes, textes inclinés et documents RTL reste approximatif.
Les zones masquées sont exclues. Données mixtes, coordonnées non numériques
ou volumes excessifs désactivent le panneau plutôt que d'afficher un résultat
ambigu. Le texte est effacé au changement de photo et à la fermeture.
L'observateur DOM se déconnecte à la sortie du visualiseur ; aucun polling web.

## Compatibilité et notifications

Le hook n'accepte que les empreintes SHA-256 des bundles originaux de la version
v3.4.1 effectivement testée (MANAGER_HASH et VIEWER_HASH dans files/apply.cjs,
INDEX_HASH dans files/cache.cjs).
Un nouvel assemblage, même avec la même version, désactive l'extension tant qu'il
n'a pas été relu et testé. Il ne suffit pas de remplacer les empreintes pour
déclarer une nouvelle version compatible : revoir le gestionnaire OCR, la
structure du panneau et exécuter les tests de navigation/sécurité.

En cas d'incompatibilité :
1. Aucun correctif n'est injecté ; un ancien correctif dans ce conteneur est
   retiré à partir de sa sauvegarde originale et gzip/Brotli sont régénérés.
2. Le serveur et sa mise à jour continuent ; la vérification OCR est facultative
   dans update-nas.cjs. Une erreur OCR ne bloque pas l'alignement des workers.
3. Un statut sans donnée personnelle est écrit dans
   UPLOAD_LOCATION/.immich-maintenance/ocr-status.json.
4. Le terminal Dockge et les logs indiquent la désactivation. Le timer utilisateur
   lit ce statut sur le montage NAS existant et affiche une notification de bureau
   sur Ryzen (au prochain contrôle, y compris après son retour). Une seule
   notification par version/raison ; le rétablissement réarme cette notification.
5. Un changement inattendu du DOM pendant l'utilisation désactive seulement le
   panneau pour cette page et affiche un avertissement refermable dans Immich.

Ce sont des notifications du bureau et un avertissement dans la page, pas une
écriture dans la base de notifications native d'Immich. Sans session utilisateur,
consulter les logs du NAS ; la notification de bureau attend le retour de Ryzen.

Les ressources personnalisées sont publiées dans un répertoire statique
/_app/immutable-ocr-<empreinte>/ et l'index HTML pointe vers celui-ci.
Les imports absolus sont réécrits dans cette copie, les imports relatifs restent
cohérents. Cela évite les anciens fichiers conservés dans le cache du navigateur
ou du CDN, sans changer leurs politiques ni la CSP. La copie est d'environ
27 Mo sur cette version, créée uniquement lors d'un changement du correctif.
Le service worker Immich reste inchangé (il ne gère ici que les images API).

L'index original est aussi vérifié par SHA-256 et sauvegardé. Une incompatibilité
restaure cet index. L'installation redémarre le serveur uniquement lorsque les
ressources ont changé, car Immich les charge en mémoire. Un onglet déjà ouvert
doit être rechargé ; Ctrl+Maj+R reste utile en cas de cache ancien.

## Tests de l'extension

- node modules/immich-ocr-persistence/test.cjs
- node modules/immich-ocr-persistence/test-update.cjs
- python3 modules/immich-ocr-persistence/test-notify.py
- node modules/immich-ocr-persistence/test-compat.cjs /chemin/bundles-originaux
  (CUVvskNU.js, CC5MOeVu.js et index.html de v3.4.1, ne pas stocker les bundles dans Git).
- test-browser.cjs utilise playwright-core et Chromium système. Installer
  playwright-core dans un dossier de test temporaire, définir NODE_PATH vers
  ses node_modules, puis lancer node sur ce test. OCR_TEST_SCREENSHOT permet
  facultativement de conserver une capture de la page de test.

Les tests navigateur utilisent des données synthétiques, sans compte connecté :
injection HTML, copie explicite/refus, texte absent, chargement tardif, navigation,
réouverture du panneau, structure incompatible et absence d'erreurs JavaScript.
Les tests de notification interceptent notify-send ; ils n'envoient pas d'alerte.


## Recherche intelligente : liaison du serveur au moteur IA

Le serveur API du NAS a lui aussi besoin du moteur IA pour encoder les requêtes
de recherche. Des microservices sains sur le PC ne prouvent pas que cette liaison
fonctionne. Avec un moteur déporté, le nom Docker immich-machine-learning n'est
pas résolu depuis le réseau du NAS.

configure-ml.py enregistre l'URL distante dans machineLearning.urls via l'API
administrative officielle, à partir de IMMICH_UPDATE_WORKER_PING. Il remplace
l'adresse Docker locale inapplicable et conserve les autres URLs personnalisées.
Ce réglage persiste dans Immich après redémarrage et recréation du conteneur.
Aucun extra_hosts temporaire ni changement d'exposition réseau n'est ajouté.

Prérequis : IMMICH_API_KEY dans le .env existant de la stack locale, avec droit
de lire/modifier les paramètres système. La clé n'est jamais copiée dans Git ni
affichée. Le script lit la configuration complète en mémoire et ne change que
machineLearning.urls. L'ancienne liste est sauvegardée dans le dossier d'état
utilisateur, fichier ml-urls-before.json en mode 600.

Validation effectuée : ping du moteur depuis le conteneur API, relecture de la
configuration, puis requête authentifiée POST /api/search/smart (« cheval metal »),
HTTP 200 avec dix résultats. Ne pas se limiter au healthcheck des conteneurs
ou au chargement de la page de connexion.

Si le PC hébergeant le moteur IA est éteint et qu'aucun autre moteur n'est
configuré, la recherche intelligente est indisponible. Le panneau OCR utilise
les résultats déjà enregistrés et ne dépend pas de ce moteur pour l'affichage.


Avec le module immich-search-local installé, configure-ml.py conserve au contraire
le nom Docker immich-machine-learning : il se résout vers le CPU sur le NAS et
vers CUDA sur le worker. Le marqueur utilisateur local-search-enabled sélectionne
cette architecture. La procédure de mise à jour inclut alors le moteur ML du NAS
dans les téléchargements, la bascule et les contrôles de santé.
