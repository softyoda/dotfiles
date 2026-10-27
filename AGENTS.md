# Préférences de maintenance

- Répondre en français.
- Lorsqu'une personnalisation durable du bureau ou des outils est installée pour l'utilisateur, l'intégrer aussi à ces dotfiles avec sa procédure de restauration. Demander en cas de doute sur le périmètre à sauvegarder.
- Préserver les modifications locales existantes ; utiliser un arbre de travail séparé si nécessaire.
- Ne pas inclure de mots de passe, jetons, profils Wi-Fi secrets ni identifiants matériels privés dans le dépôt.
- Demander confirmation avant de modifier des fichiers système ; privilégier les installations utilisateur lorsque cela convient.
- Toute nouvelle fonctionnalité = un module `modules/<id>/` (format : `modules/README.md`) ; une appli sans config = une ligne dans `catalog/apps.toml`. Puis `bin/update-readme`.
- Valeurs propres à une machine/au réseau → `vars` du profil privé ; secrets → `secrets.env` du dossier privé (bibliothèque Seafile chiffrée `dotfiles-private`). Rien de tout ça dans ce repo public.
- Vérifier avec `dotctl info <id>` et `dotctl status` ; sur une machine où la fonctionnalité existe déjà, le module doit sortir « à jour ».
