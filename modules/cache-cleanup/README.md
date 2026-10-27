# Nettoyage automatique des caches

Les caches de paquets ne sont **jamais** purgés automatiquement sur Arch/CachyOS :
`/var/cache/pacman/pkg` et `~/.cache/paru/clone` grossissent indéfiniment (facilement
plusieurs dizaines de Go, ex. les versions successives de `cuda` ou les nightlies Firefox).

Ce module installe un timer systemd qui supprime **chaque jour** les fichiers de cache
(`*.pkg.tar.*`, archives sources, AppImage, .deb…) de **plus de 7 jours**, côté pacman
comme côté paru (les clones paru de tous les utilisateurs).

| Fichier | Rôle |
|---|---|
| `/usr/local/bin/cache-cleanup.sh` | le nettoyage |
| `/etc/systemd/system/cache-cleanup.service` | oneshot, priorité basse (Nice 19, IO idle) |
| `/etc/systemd/system/cache-cleanup.timer` | quotidien, `Persistent=true` (rattrape un jour manqué) |

Vérifier / déclencher manuellement :

```bash
systemctl list-timers cache-cleanup.timer   # prochaine exécution
journalctl -u cache-cleanup.service          # ce qui a été supprimé
sudo /usr/local/bin/cache-cleanup.sh         # lancer maintenant
```
