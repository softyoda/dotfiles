# Siftbay

Le dépôt privé `softyoda/siftbay` contient le moteur, les agents, le frontend et leur documentation. Le fichier `revision` épingle la version installée ; ce module ne duplique pas le code.

Prérequis : accès GitHub authentifié avec `gh auth login`, accès au serveur, sources et clés dans le profil privé. Le module installe les lanceurs utilisateur et le timer hebdomadaire persistant du poste. Le suivi en direct reste à la demande.

Les variables CATALOG_* décrivent le serveur, les correspondances entre sources et montages, les sources du poste et les fichiers de clés privés. Ne pas réutiliser les chemins d’un autre ordinateur sans les adapter. La clé d’agent est distincte de celle des actions desktop ; le serveur limite ses sources autorisées.

Pour héberger le serveur : consulter `docs/deployment.md` dans le dépôt de l’application et utiliser `scripts/render_server.py` avec une configuration privée. Le serveur peut désactiver son frontend web et servir uniquement l’API. Les données SQLite restent sur le disque local du serveur.

Après une évolution : tester et pousser le dépôt privé, actualiser `revision`, appliquer ce module, déployer la même version sur le serveur puis vérifier `dotctl info file-catalog` et `dotctl status` avant de pousser les dotfiles.

L’ancien module Diskover est remplacé. Sa désinstallation ne doit jamais supprimer les fichiers indexés ni les applications Docker sans rapport.

Le frontend découvre les sources du serveur ; ses paramètres permettent de choisir un autre service et les montages locaux. Les vues liste/grille et la densité sont propres au navigateur. Le serveur peut utiliser une image Docker autonome avec `bundled_app` et un Compose placé dans Dockge ; voir le guide de déploiement du dépôt privé. Les noms de domaines et règles de proxy restent dans la configuration privée, avec un script de restauration dédié.
