# Bibliothèque NAS — terminée

21 systèmes, 2 698 entrées de lancement, 380,152 Go de fichiers. Extraction effectuée directement sur le NAS, puis relecture et contrôle CRC32 avant suppression des 27 archives de collections et des ZIP internes des consoles. Les 514 ZIP Arcade/Neo Geo sont conservés, dont le BIOS `neogeo.zip` exclu des listes de jeux.

Jeux : `$ROMS_NAS_DIR/`, avec un dossier par système. Les parties alphabétiques et mises à jour sont regroupées. Les listes multidisques sont vérifiées ; les disques supplémentaires restent sur le NAS et ne créent pas de doublons dans les menus.

Les 21 listes sont intégrées dans `~/.config/retroarch/playlists/` et leurs 2 698 chemins NAS ont été vérifiés. Seuls ces petits fichiers de métadonnées sont locaux : **aucune ROM copiée sur le PC**. Raccourci : [NAS](~/Jeux/ROMs/NAS).

Les noms des listes, les cœurs existants et leurs réglages sont conservés. 30 petits préréglages par dossier sont ajoutés pour les noms des dossiers NAS ; `retroarch.cfg`, les manettes et l’interface ne sont pas modifiés. Anciennes listes sauvegardées dans `~/.config/retroarch/backup-nas-20261011-173908/`.

Les cœurs Arcade/Neo Geo précédemment retirés ne sont pas réinstallés : leurs jeux sont classés et référencés, mais nécessitent encore un cœur compatible. L’intégrité et les chemins sont contrôlés ; les jeux n’ont pas été testés à l’exécution dans cette opération.

[Inventaire complet par génération et système]($ROMS_NAS_DIR/INVENTAIRE-ROMs.md). Le journal `extraction-journal.jsonl` et les inventaires JSON sont également conservés sur le NAS. Le bilan local du raccordement est dans `nas-retroarch-integration.json`.
