# Dossiers des applications dans KDE

Deux actions sont ajoutées au clic droit des applications, dans le menu et les
lanceurs Plasma qui affichent les actions standard des fichiers `.desktop` :

- **Ouvrir le dossier du programme** : ouvre Dolphin en sélectionnant l’exécutable.
- **Ouvrir le dossier du raccourci** : sélectionne le fichier `.desktop` utilisé.

Le helper lit la commande sans l’exécuter. Les préfixes `env` et les chemins avec
espaces sont pris en charge. Pour Flatpak, les fichiers installés sont utilisés
lorsque leur emplacement est disponible ; un lanceur shell reste identifié comme
un lanceur shell, sans évaluer son contenu.

## Installation

```sh
dotctl info kde-app-locations --json
dotctl plan kde-app-locations --json
dotctl apply kde-app-locations
```

Le socle ajoute les actions une fois. La partie `auto-sync`, activée par défaut,
suit les nouvelles installations et les mises à jour toutes les deux minutes.
Les fichiers système ne sont pas modifiés. Les copies utilisateur générées sont
suivies dans `~/.local/state/kde-app-locations/managed.json` : leurs mises à jour
repartent du raccourci source, et une copie inchangée est retirée quand sa source
disparaît. Les modifications personnelles sont préservées. Les raccourcis
personnels déjà orphelins ne sont pas supprimés arbitrairement.

Cette personnalisation ne remplace pas Kickoff, ne change pas les favoris ni la
disposition du panneau. Elle fonctionne via les actions standard des raccourcis,
pas par modification du binaire ou des fichiers QML système de Plasma.

## Vérifier

```sh
~/.local/bin/kde-app-locations check --json
~/.local/bin/kde-app-locations open program /chemin/application.desktop --json
dotctl status kde-app-locations
```

Une seconde synchronisation ne doit produire aucun changement. Les chemins et
les sauvegardes réelles de la machine restent dans l’état local, jamais dans ce
module public. Le programme n’exécute jamais la commande `Exec` inspectée.

## Retirer / restaurer

```sh
~/.local/bin/kde-app-locations restore
```

Cette commande désactive la synchronisation, retire uniquement les copies
inchangées créées par le module et enlève ses actions des raccourcis personnels,
en conservant leurs autres propriétés et modifications. Les liens symboliques
personnels remplacés temporairement sont rétablis si leur copie est inchangée.
Réinstaller le module réactive les actions et le suivi.
