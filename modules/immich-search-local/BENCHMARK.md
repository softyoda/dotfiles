# Mesures du 16 novembre 2026

Immich v3.4.1 ; modèle ViT-B-32__openai ; vecteurs de dimension 512.
NAS Intel N100, 4 cœurs, 16 Go ; worker avec RTX 3080 10 Go.

## Encodage de la phrase seule

20 appels directs à /predict, phrases synthétiques en français. Mesures chaudes
après un premier appel. Le GPU est mesuré pour comparaison, pas pour imposer
sa présence pendant les recherches.

| Moteur | Médiane | P95 | CPU consommé/requête | RAM chargée |
| --- | ---: | ---: | ---: | ---: |
| NAS CPU, 2 threads | 268,5 ms | 365,7 ms | 576,3 ms CPU | 505 Mio |
| NAS CPU, 1 thread (retenu) | 152,0 ms | 164,7 ms | 157,5 ms CPU | 500 Mio |
| RTX 3080, TensorRT RTX | 2,6 ms | 5,5 ms | 6,5 ms CPU | 938 Mio |

La première préparation du modèle CPU a pris 6,44 s ; son rechargement avec
les artefacts optimisés en cache a pris 1,24 s. Ce ne sont pas deux essais
strictement identiques à froid : le premier inclut l'optimisation du modèle.
Le premier chargement/préparation GPU a pris 7,50 s.

Après déchargement du modèle de test, le conteneur CPU était autour de 171 Mio
et un instantané Docker donnait 0,25 % de CPU. Les fenêtres de dix secondes
juste après les requêtes incluent nettoyage, contrôles de santé et effets de
fin de traitement : elles ne représentent pas un coût de veille permanent.
Les mesures brutes de ces fenêtres sont conservées dans measurements.json.

## Recherche complète, PC indisponible

Les deux services Immich du PC étaient arrêtés. Requêtes authentifiées depuis
le NAS vers son API via le réseau Docker, dix résultats demandés par appel :

| Recherche | Durée observée |
| --- | ---: |
| Première recherche intelligente | 972 ms |
| Nouvelle phrase (9 requêtes, médiane) | 614 ms |
| Phrase déjà en cache (10 requêtes, médiane) | 435 ms |
| Recherche OCR (1 requête) | 166 ms |
| Filtre d'une personne reconnue (1 requête) | 50 ms |

Tous les appels ont réussi, avec dix résultats reçus. Les résultats eux-mêmes,
identités de personnes, clés API et chemins privés ne sont pas conservés.
Ces mesures incluent l'API, PostgreSQL et la réponse JSON ; elles excluent
la 4G, le proxy distant et le téléchargement des miniatures dans le navigateur.
OCR/personne : une mesure fonctionnelle chacun, pas une distribution statistique.
Aucune puissance électrique en watts n'a été mesurée.

## Méthode

Temps monotone autour de la requête HTTP. CPU : différence de usage_usec du
cgroup, divisée par le nombre de requêtes ; inclut un peu d'instrumentation et
les tâches de fond du conteneur. RAM : memory.current moins inactive_file.
Conteneur NAS de test limité à 2 CPU et 1536 Mio ; aucun swap disponible.
Le moteur de production utilise un TTL de 300 s (60 s pour les essais isolés).
Les conteneurs temporaires ont été supprimés ; les modèles en cache sont conservés.


Scripts reproductibles dans tools/ :
- bench-model.py NOM_DU_CONTENEUR : modèle déjà présent dans /cache, appels
  textuels uniquement ; BENCH_NO_SUDO=1 pour Docker accessible sans sudo.
- bench-api.py : à lancer sur le NAS avec un objet JSON contenant api_key sur
  stdin, jamais dans les arguments. Ne conserve ni la clé ni les résultats.
  Arrêter les workers séparément si l'on veut reproduire le test d'indépendance,
  puis les remettre dans leur état initial ; le script n'arrête aucun service.
