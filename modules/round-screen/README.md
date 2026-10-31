# Linux Rond — installation par les dotfiles

Le projet est désormais maintenu dans **[softyoda/linux-rond](https://github.com/softyoda/linux-rond)**.
Le code Plasma/KWin, les scripts de configuration et le maillage approuvé ont été
retirés de ces dotfiles. Les développements et validations doivent être commités
et publiés dans ce nouveau dépôt.

Ce module est uniquement un adaptateur d’installation :

- `upstream.env` fixe l’URL et la révision Git validée ; aucune mise à jour implicite de `main`.
- Le dépôt est récupéré dans `${XDG_DATA_HOME:-~/.local/share}/linux-rond/source`.
- Les réglages `ROUND_SCALE` et `ROUND_OUTPUT` restent dans le profil/réglage privé de la machine.
- Un checkout modifié localement ou provenant d’une autre origine est conservé ; l’installation s’arrête.

## Appliquer

```sh
dotctl info round-screen --json
dotctl plan round-screen --json
dotctl apply round-screen
```

Le socle installe/actualise le conteneur de panneau et le script de zone sûre.
Il conserve les panneaux actuels. Pour créer ou refaire les deux barres en arc,
choisir explicitement la sous-partie **`round-screen/panels`** :

```sh
dotctl plan round-screen/panels --json
dotctl apply round-screen/panels
```

Cette sous-partie remplace les panneaux de l’unique sortie carrée, sauvegarde la
configuration complète et relance Plasma. Elle refuse les sorties carrées multiples.
Pour restaurer une disposition, utiliser `scripts/restore-panels.sh` du dépôt installé
avec le chemin de sauvegarde affiché lors de la configuration.

## Statut du mode projeté

La barre et le maillage sont validés ; la projection interactive, la correction souris/tactile,
les préférences par application et le partage en demi-disques sont suivis dans
[la feuille de route Linux Rond](https://github.com/softyoda/linux-rond/blob/main/docs/ROADMAP.md).
Ils ne sont pas annoncés comme déjà installés par ce module.

Après validation d’une nouvelle version : commiter/pousser dans `linux-rond`,
puis actualiser `LINUX_ROND_REVISION` ici et vérifier le module sur la machine cible.
