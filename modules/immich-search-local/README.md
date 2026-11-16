# Recherche autonome sur le NAS, ingestion IA sur GPU

Ce module complète immich-ocr-persistence et utilise sa configuration privée.
Aucun hôte, IP ni secret n'est enregistré ici.

## Architecture

- Sur le NAS : immich-server exécute l'API ; immich-machine-learning fournit
  l'encodage des requêtes sur CPU, uniquement sur le réseau Docker privé commun
  à l'API et à PostgreSQL. Aucun port ML supplémentaire n'est publié.
- Sur le PC : immich-microservices effectue les traitements d'ingestion et son
  immich-machine-learning utilise l'image NVIDIA avec réservation du GPU.
- machineLearning.urls contient le même nom Docker dans les deux contextes.
  Chaque réseau le résout vers son propre moteur. Les recherches n'attendent
  donc pas un timeout de connexion au PC absent.

La recherche OCR et le filtre par personne déjà reconnue interrogent PostgreSQL.
La recherche intelligente encode uniquement la phrase, puis compare son vecteur
aux vecteurs des images déjà enregistrés. Les répétitions peuvent réutiliser
le cache d'embeddings du serveur. Aucune réindexation n'est lancée par ce module.

Les miniatures/transcodages restent sur les microservices existants. L'exposition
de la carte graphique à ces microservices ne suffisait pas à accélérer le
conteneur ML séparé : celui-ci doit également utiliser l'image -cuda et recevoir
le périphérique NVIDIA. Le backend effectif peut être TensorRT RTX.

## Limites et ressources

Le moteur CPU du NAS est limité à deux cœurs et 1536 Mio, avec un seul thread
intra/inter-op (plus efficace sur le N100 mesuré). Le modèle se décharge après
300 secondes d'inactivité. Cache de modèles dans ml-query-cache de la stack.
Le modèle actuel est conservé : aucune modification de qualité ni réindexation.
Ces limites devront être revues si un modèle nettement plus volumineux est choisi.

Le NAS doit rester disponible et disposer de RAM suffisante ; le réseau 4G ajoute
sa propre latence et le temps de téléchargement des miniatures aux mesures locales.
Les nouvelles photos non encore analysées doivent attendre l'ingestion sur le PC.
Une personne non encore détectée n'est donc pas recherchable par visage.

## Appliquer, restaurer, retirer

Examiner avec dotctl info immich-search-local --json puis
dotctl plan immich-search-local --json ; appliquer avec dotctl apply immich-search-local.
Le module dépend du module de maintenance existant, qui fournit la configuration,
la clé API administrative locale et les hooks. Les Compose sont sauvegardés avant
édition. Les services ML sont créés/recréés ; aucune photo n'est modifiée.

Le marqueur utilisateur .config/immich-update/local-search-enabled demande au
module de maintenance de conserver ce routage local. Réappliquer le module OCR
ne remet donc pas l'ancienne dépendance au PC.

Les mises à jour du bureau et de Dockge téléchargent et vérifient maintenant
le serveur ET le moteur CPU du NAS ; l'alignement des workers conserve le suffixe
-cuda. Les versions serveur et modèles d'exécution restent synchronisées.

Pour retirer : restaurer les Compose sauvegardés en préservant les évolutions
ultérieures, retirer le marqueur, puis reconfigurer explicitement les URLs ML.
Cela réintroduira la dépendance au PC pour les nouvelles recherches intelligentes.

## Validation effectuée

- Exécution réelle d'un encodeur textuel sur CPU et GPU avec le même modèle.
- Inférence visuelle synthétique sur le moteur GPU installé (aucune écriture
  dans la photothèque).
- Recherches API authentifiées directement depuis le NAS pendant l'arrêt des
  DEUX conteneurs Immich du PC ; OCR, personne et recherche intelligente réussis.
  Les conteneurs du PC ont ensuite été restaurés.
- Test de la procédure de mise à jour avec le moteur NAS présent et absent.
- Voir BENCHMARK.md et measurements.json pour les résultats et les limites.
