# Mode automatique pour Cachy-Update

Installation utilisateur : `bash scripts/setup-cachy-update.sh`.

Au premier choix de mise à jour :
- `A` ou `a` : confirmations automatiques pour pacman, paru et Flatpak ;
- `Y` : mode interactif habituel ;
- `n` : annulation.

Le mode A applique aussi les nettoyages des paquets orphelins, runtimes Flatpak inutilisés et caches prévus par ces scripts, et sélectionne tous les services proposés au redémarrage. L'authentification administrateur, la gestion des `.pacnew` et le redémarrage du PC peuvent encore demander une intervention.

`--skipreview` est transmis à paru uniquement en mode A : aucun changement de `/etc/paru.conf` n'est nécessaire. Les bibliothèques personnalisées sont installées dans `~/.local/share/arch-update/lib`, les autres suivent la version système par liens symboliques. L'installateur sauvegarde les anciens réglages et ne modifie pas les bibliothèques système.

Compatible avec Cachy-Update / Arch-Update 4.4.1. Après une évolution majeure de l'application, vérifier la compatibilité des bibliothèques personnalisées.

Tests hors ligne, sans exécuter de mise à jour :

```sh
python cachy-update/test-auto-mode.py
```
