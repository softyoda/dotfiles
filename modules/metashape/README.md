# Agisoft Metashape Professional

Version installée : **2.1.3**. Le module télécharge l'archive officielle
`https://download.agisoft.com/metashape-pro_2_1_3_amd64.tar.gz` (motif :
`metashape-pro_<majeur>_<mineur>_<patch>_amd64.tar.gz`) et la décompresse dans
`/opt/metashape-pro`. Pour changer de version, modifier `VERSION` dans
`apply.sh` puis relancer le module.

Le script `add_to_applications.sh` fourni par Agisoft n'est pas utilisé : les
trois lanceurs (`agisoft-metashape-pro`, `agisoft-viewer`, `agisoft-monitor`)
sont déployés dans `/usr/share/applications` par le module. La commande fish
`metashape` appelle `/opt/metashape-pro/metashape`.

## Étape manuelle : licence

La licence n'est **jamais** versionnée (le fichier `metashape.lic` reste hors
du dépôt, de même que toute clé).

1. Lancer Metashape ; à la première ouverture, saisir la clé d'activation
   (Aide → Activer le produit) ou pointer vers un serveur de licences
   flottantes. Le fichier `/opt/metashape-pro/metashape.lic` est alors créé.
2. Pour restaurer une machine : récupérer la clé dans le gestionnaire de mots
   de passe, ou sauvegarder `metashape.lic` à part (hors dépôt public).
3. Si l'activation échoue après réinstallation du dossier `/opt`, c'est que le
   dossier a été vidé : refaire l'activation.
