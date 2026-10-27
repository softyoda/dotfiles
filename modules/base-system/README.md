# Système de base

Socle commun à toutes les machines, à appliquer en premier.

| Réglage | Où | Comment |
|---|---|---|
| paru (assistant AUR) | `/usr/bin/paru` | dépôt CachyOS si dispo, sinon `paru-bin` compilé depuis l'AUR |
| Flathub | remote flatpak système | `flatpak remote-add --if-not-exists` |
| `Color`, `ILoveCandy`, `DisableDownloadTimeout`, `ParallelDownloads = 10` | `/etc/pacman.conf` | édition ligne par ligne avec `sed` (le fichier n'est jamais écrasé) |
| `SkipReview` | `/etc/paru.conf` | idem |
| `SUDO_ASKPASS=/usr/bin/ksshaskpass` | `/etc/environment` | les outils lancés hors terminal (interface dotctl, raccourcis…) demandent le mot de passe sudo dans une fenêtre KDE |
| groupe `wheel` | `/etc/group` | `ensure_groups` ; les autres groupes (docker…) sont ajoutés par les modules qui en ont besoin |

Notes :

- `SUDO_ASKPASS` et l'ajout à un groupe ne prennent effet qu'après reconnexion.
- `SkipReview` désactive l'affichage des PKGBUILD avant compilation AUR : plus rapide,
  mais on fait confiance aux mainteneurs AUR.
- L'autologin, autrefois dans `scripts/setup-system.sh`, est désormais le module `autologin`.
