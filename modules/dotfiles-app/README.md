
## Installer avec des choix détaillés

- **Configurer…** : sous-parties à cocher, champs de configuration et onglet README.
- **Voir ce qui sera appliqué** : aperçu du socle commun, des parties et des dépendances.
- **Enregistrer les choix** : conserve les choix dans Seafile privé sans rien installer.
- **Appliquer cette sélection** : applique uniquement le module sélectionné et ses dépendances.
- **Copier ID / Pour un agent** : référence stable comme `paseo/launcher`, utilisable en CLI.
- **Dossier privé…** : choisit la bibliothèque Seafile déjà synchronisée sur cet ordinateur.

Les sous-parties sont déclarées par les mainteneurs/agents, pas déduites des
fichiers. Les modules encore monolithiques restent applicables en entier.
Le découpage initial couvre Blender Launcher, Seafile et Paseo ; Firefox garde
son écran de sauvegarde/restauration sélective. Voir `modules/README.md` pour
les schémas et commandes d'automatisation.
