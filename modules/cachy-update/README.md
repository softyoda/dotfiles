# Mode automatique pour Cachy-Update

Au premier choix de mise à jour (`Proceed with update? [Y/A/n]`) :
- `A` ou `a` : confirmations automatiques pour pacman, paru et Flatpak ;
- `Y` : mode interactif habituel ;
- `n` : annulation.

Le mode A applique aussi les nettoyages des paquets orphelins, runtimes Flatpak inutilisés
et caches prévus par ces scripts, et sélectionne tous les services proposés au redémarrage.
L'authentification administrateur, la gestion des `.pacnew` et le redémarrage du PC peuvent
encore demander une intervention.

`--skipreview` est transmis à paru uniquement en mode A : aucun changement de
`/etc/paru.conf` n'est nécessaire.

## Fonctionnement

Cachy-Update charge ses bibliothèques depuis `~/.local/share/arch-update/lib` si ce dossier
existe (sinon `/usr/share/arch-update/lib`). `apply.sh` y construit :

- une **copie** des bibliothèques patchées (`files/lib/*.sh`) ;
- un **lien symbolique** vers `/usr/share/arch-update/lib/<fichier>` pour toutes les autres,
  afin qu'elles suivent les mises à jour du paquet (pas de copies figées qui vieillissent).

Le dossier est reconstruit à côté puis échangé d'un coup ; l'ancien est conservé en
`lib.backup-AAAAMMJJ-HHMMSS`. Les bibliothèques système ne sont jamais modifiées.
`~/.config/arch-update/arch-update.conf` désactive l'affichage des news (`NewsNum=0`).

`check.sh` signale le module comme non installé si une lib patchée diffère, si une lib non
patchée n'est pas un lien vers la version système, ou s'il reste un fichier périmé.

## Après une mise à jour de cachy-update

Compatible avec Cachy-Update / Arch-Update 4.4.x. Après une évolution de l'application,
comparer les libs patchées avec la nouvelle version :

```sh
for f in modules/cachy-update/files/lib/*.sh; do diff -u /usr/share/arch-update/lib/$(basename $f) $f; done
```

Tests hors ligne, sans exécuter de mise à jour :

```sh
python modules/cachy-update/test-auto-mode.py
```
