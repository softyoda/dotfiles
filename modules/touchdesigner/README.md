# TouchDesigner sous Wine

Le module installe le lanceur, les icônes, le type MIME et les associations de
fichiers. **Le préfixe Wine, le runner et TouchDesigner lui-même sont à
reconstruire à la main** (trop lourds pour le dépôt : plusieurs Go).

## Ce que fait `launch-touchdesigner.sh`

- Force XWayland (`WAYLAND_DISPLAY=""`) et `__GL_YIELD=USLEEP` (évite les
  blocages de `GLXMakeCurrent` sous KDE Plasma 6).
- Cherche `TouchDesigner.exe` dans le préfixe, convertit les chemins Linux en
  `z:\…`, décode les URI `file://`.
- Avant le lancement, vérifie les `.toe` (NewProject, modèle de démarrage de
  `pref.txt`, fichier passé en argument) : s'ils n'ont pas le composant
  `wine_ui_fixes`, il est fusionné via `toeexpand.exe` / `toecollapse.exe`
  (sauvegarde du `.toe` d'origine dans `~/.local/share/touchdesigner-linux/backups`,
  purgée après 30 jours).
- Variables : `TD_BASE_DIR` (défaut `~/.local/share/touchdesigner-linux`),
  `TOUCHDESIGNER_EXE_OVERRIDE`, option `--exe <chemin>`.

## Reconstruire l'environnement

Arborescence attendue dans `~/.local/share/touchdesigner-linux/` :
`runner/` (build de Wine), `prefix/` (préfixe 64 bits, utilisateur `steamuser`),
`wine_ui_fixes.tox` (déployé par le module).

Aucune note ni aucun script de construction n'existe sur la machine ; les
étapes ci-dessous sont déduites de l'état actuel du préfixe.

1. **Runner** : le runner actuel est un Wine TkG « valve-exp-bleeding » 9.0
   (build du 2024-04-29, issu de Frogging-Family/wine-tkg-git). Récupérer un
   build équivalent (Wine TkG staging) et le décompresser dans `runner/`
   de façon à avoir `runner/bin/wine64`. Alternative plus simple : installer
   le module `wine` (paquet `wine-tkg-staging-wow64-bin`) puis faire pointer
   `runner/bin/wine64` vers `/usr/bin/wine64` (non testé).
2. **Préfixe** :
   ```
   export WINEPREFIX=~/.local/share/touchdesigner-linux/prefix WINEARCH=win64
   runner/bin/wine64 wineboot -i
   ```
3. **Bibliothèques Windows** (winetricks, voir `prefix/winetricks.log`) :
   `corefonts`, `d3dx11_43`, `ucrtbase2019`, `vcrun2019` (paquet `winetricks`).
   `winetricks` doit utiliser le même `WINEPREFIX` et le `wine64` du runner
   (`WINE=…/runner/bin/wine64`).
4. **TouchDesigner 2025.32820** : télécharger l'installateur officiel
   `https://download.derivative.ca/TouchDesigner.2025.32820.exe` (≈ 3 Go) et
   l'exécuter avec le runner :
   `runner/bin/wine64 TouchDesigner.2025.32820.exe` ; il s'installe dans
   `C:\Program Files\TouchDesigner`. La licence se saisit dans l'interface
   (jamais dans le dépôt).
5. Relancer ce module, puis lancer « TouchDesigner » depuis le menu : les
   correctifs d'interface s'appliquent au premier projet ouvert.

Voir aussi le module `helios-laser` (sortie laser depuis TouchDesigner).
