# Siftbay

Le module installe une révision épinglée du dépôt privé `softyoda/siftbay`. Le lancement ouvre le client local : aucun serveur distant ni volume à scanner n’est préconfiguré. Les volumes accessibles sont détectés, puis sélectionnés dans « Volumes et scans ». Les paramètres permettent une connexion explicite à un serveur.

Le mode temporaire oublie le catalogue à la fermeture du dernier client ; les fichiers analysés ne sont jamais supprimés. Le mode conservé permet les mises à jour manuelles, planifiées ou en temps réel. La copie d’un serveur peut être conservée sur disque ou chargée en RAM, sur choix explicite. Le moteur local du prototype est Python ; Windows et le moteur SQLite WebAssembly restent des adaptations distinctes.

La sous-partie facultative `file-catalog/publisher` restaure l’ancien agent qui envoie les scans du poste à un serveur. Elle n’est pas activée par défaut et utilise uniquement les variables et clés du profil privé. Ne pas l’activer pour une installation locale ordinaire.

Pour le serveur Docker, lire `docs/deployment.md` et `docs/architecture.md` dans le dépôt privé. Les domaines, montages et clés de déploiement sont dans les dotfiles privés. Mettre à jour le pin, appliquer et vérifier `dotctl status`, puis pousser les modifications. L’administration possède une clé initiale dans le volume de données ; la publication Internet doit être protégée par un fournisseur d’identité adapté. Ne jamais exposer une API de configuration sans contrôle d’accès.
