# Reprise du diagnostic Xbox — état au 7 novembre 2026

## Objectif et limites de la conclusion

L’utilisateur veut jouer avec quatre, deux ou une manette, laisser les autres
s’éteindre, puis les rallumer normalement, sans changer le dongle de port, refaire
les synchronisations ni solliciter un agent. Il a demandé d’arrêter les essais
manuels prolongés ; continuer grâce aux traces si un incident revient.

**État final : pilote local installé durablement ; quatre vrais périphériques et
leurs boutons fonctionnent. Transitions 4 → 2 → 1 → 4 vérifiées sans changement
de port et sans resynchronisation pour le retour à quatre.** Le prochain démarrage
après arrêt nocturne et une longue session à quatre n’ont PAS encore été validés.
Ne pas annoncer une garantie définitive : le correctif amont n’est pas fusionné.

## Matériel et logiciels pertinents

- CachyOS ; noyau courant lors des tests : `7.3.1-1-cachyos`.
- Récepteur USB `045e:02e6`, affiché « XBOX ACC », puce MT7612 ; manettes Xbox Series.
- Le pilote signale une adresse MAC fréquemment vue sur les copies de récepteurs.
  Cela ne prouve ni panne matérielle ni conflit MAC ; ne pas modifier l’adresse au hasard.
- Paquets d’origine : `xone-dkms 0.5.8-2`, `xone-dongle-firmware 2.0.0-1`.
- `xpadneo` concerne Bluetooth ; la liaison utilisée ici passe par `xone` et le dongle.
- La veille USB est déjà désactivée : `power/control=on`, autosuspend `-1`.
  La règle globale existante relève du module `usb-no-autosuspend`.

Aucun numéro de série de manette, adresse MAC, rapport brut ou profil personnel
n’est nécessaire dans Git. Le pilote journalise parfois ces identifiants localement.

## Historique retrouvé et preuves

L’agent Paseo `5b06937a-f4c6-4b65-a5ba-3d988d09cc34` correspond à la session Codex
`01a1846a-9ef5-7783-8923-960150e73770` du 28 octobre. Il avait retrouvé des pertes
simultanées de plusieurs manettes le 24 octobre à 22 h 38 et 23 h 20, sans journal
noyau assez ancien pour conclure. Il avait installé la collecte utilisateur actuelle.
Il n’avait pas corrigé le pilote. Les sources originales de son utilitaire se
trouvaient dans un ancien dossier `tmp_retroarch`, depuis déplacé dans la corbeille.
Les sources effectivement actives sont maintenant sauvegardées dans ce module.

Le 7 novembre, après l’arrêt nocturne : dongle visible/alimenté, pilote chargé,
aucun périphérique manette. Recherche de synchronisation activée via `pairing` :
aucun succès. Rebind du pilote : initialization annoncée réussie puis délais
`-110` dans le balayage radio. Première erreur observée après le canal 161, vers
165 ; **cela ne démontre pas que 165 est la cause**, car l’initialisation le visite aussi.

Rebranchement physique : chargement complet du firmware puis vraie manette connectée.
Réinitialisations logicielles avec le pilote d’origine : compteur `active_clients=1`,
mais aucun périphérique input, avec des événements `ADD_CLIENT` répétés.
L’agent a annoncé trop tôt un succès en se fiant à ce compteur ; il l’a corrigé.
**Toujours vérifier les enfants GIP/input et des boutons, pas le compteur seul.**

Les messages USB `-121` ne permettent pas de qualifier précisément l’erreur :
les helpers d’origine écrasent les codes de retour négatifs par `-EREMOTEIO`.
Ce défaut diagnostique n’a pas été modifié dans le correctif installé.

## Corrections retenues

### 1. Recharger le firmware en RAM après un démarrage à chaud

[PR amont #225](https://github.com/dlundqvist/xone/pull/225), commit
`a0271a53aa66568204fc42abd7cae544eb96c4c9` : remplacer le redémarrage du MCU en place
par un reset vers la ROM (`MT_VEND_DEV_MODE 0x01`) puis passer par le chargement
complet du firmware (DMA/FCE compris). Le dongle peut conserver son alimentation
après arrêt ou reboot de l’hôte. Les retours publiés concernent notamment MT7612/02e6 ;
certains autres modèles ont des retours négatifs. La proposition reste non fusionnée.

[Issue #210](https://github.com/dlundqvist/xone/issues/210) : client fantôme sans input.
[Issue #227](https://github.com/dlundqvist/xone/issues/227) : CachyOS/02e6, problèmes
au redémarrage. Aucun binaire de firmware n’a été modifié : on recharge le fichier
fourni par le paquet dans la RAM du récepteur.

### 2. Nettoyer les états hôte lors d’un reset USB ordinaire

`pre_reset`/`post_reset` conservaient les clients, le compteur et l’état `pairing`,
alors que le firmware repartait sans ces associations. La garde contre les doublons
pouvait alors ignorer une nouvelle association de la même manette. Le reset de reprise
après suspension possédait déjà un nettoyage, contrairement au reset ordinaire.

Le correctif local partage ce nettoyage : arrêt des travaux/URB, destruction des
adaptateurs GIP, remise à zéro des clients, du compteur et de la recherche, puis
réinitialisation. Les annulations de travaux sont ordonnées pour éviter de libérer
un client encore utilisé. Pas de modification du balayage radio ou de la politique
d’extinction individuelle. Sources et licence GPL sont conservées dans `driver/`.

### Installation réellement en place

- Sources : `/usr/src/xone-0.5.8.1` ; version module `0.5.8.1` **locale**, non officielle.
- DKMS `xone/0.5.8.1` installé pour `7.3.1-1-cachyos`, `6.18.55-2-cachyos-lts`
  et l’arbre avec en-têtes `7.2.14-arch1-1` présent sur la machine.
- Ancien `xone/0.5.8` conservé comme « built » pour retour arrière.
- Modules signés avec la clé locale DKMS ; aucune clé privée copiée dans le dépôt.
- `AUTOINSTALL=yes`. Choix du compilateur par `.config` du noyau : Clang pour
  le noyau courant, GCC pour le LTS. Les deux compilations ont été vérifiées.
- Sauvegarde initiale des modules : `/var/lib/xone-reconnect-backup-20261107`.
  Le script portable du dépôt utilise `/var/lib/xone-reconnect/backups/`.
- Sources chargées et installées : même `srcversion`, contrôlée lors de l’installation.
- Pas de reset forcé à chaque déconnexion ; pas de service de réparation automatique actif.

## Essais effectués, sans extrapolation

1. Chargement temporaire du correctif. Une première tentative `insmod` a échoué
   car `cfg80211` n’était pas rechargé après `modprobe -r` ; dépendance rétablie.
2. Le dongle était encore dans un état USB en erreur ; un `USBDEVFS_RESET`
   (`usbreset 045e:02e6`) avec le nouveau pilote a permis le cycle reset → full
   firmware load → vrai input Xbox. Une synchronisation explicite initiale a été
   effectuée pour cette récupération ; elle ne prouve pas encore le prochain cold boot.
3. Quatre manettes distinctes, trois appuis A capturés séparément sur chacune.
4. Extinction manuelle de deux : les deux autres inputs restent présents.
5. Extinction d’une troisième : la dernière répond toujours à A.
6. Retour des trois par le bouton Xbox normal, sans bouton de synchronisation :
   quatre vrais inputs et de nouveaux appuis A reçus séparément sur chacune.
7. Installation DKMS persistante, vérification de la signature/version/srcversion.

Les extinctions manuelles ne remplacent pas un essai long d’auto-extinction.
Un script d’essai de trois resets successifs a été préparé localement mais **pas exécuté**.
Ni ces trois cycles, ni une partie prolongée, ni le reboot nocturne ne sont validés.
Ne pas relancer des essais perturbateurs sans contexte : l’utilisateur a demandé de jouer.

## Essais écartés et retirés

Une désactivation/réactivation de port via l’attribut `disable` avait produit un
compteur fantôme et avait été prise à tort pour une réussite. Sur ce matériel, elle
ne prouve pas une vraie coupure d’alimentation VBUS. Elle ne constituait pas une solution.

Un timer `xbox-dongle-recovery` qui réagissait à `-110` avec zéro client a été créé,
puis désactivé et **supprimé** : son critère échouait sur les clients fantômes et
ne couvrait pas une manette bloquée avec d’autres joueurs actifs. Son service,
script et raccourci « Réparer le dongle Xbox » ont été retirés. Ne pas les réintroduire.

Les changements de canal, modification MAC, achat de matériel et le fork expérimental
plus large cité dans PR225 n’ont pas été appliqués. Pas de boucle USB reset à chaque
extinction normale et pas de règle sudo sans mot de passe ajoutée.

## Journaux : actifs, automatiques, locaux

- `diagnostic-manettes.service` utilisateur, activé au démarrage de session ;
  continue même avec la fenêtre graphique fermée, redémarre après erreur.
- Script `~/.local/share/diagnostic-manettes/diagnostic-manettes.py`, raccourci
  `~/.local/bin/diagnostic-manettes`, application « Diagnostic manettes Xbox ».
- Archives JSONL dans `~/.local/state/diagnostic-manettes/` : jusqu’à **30 jours**,
  plafond global **256 Mio**, rotation par fichiers de 8 Mio.
- États toutes les deux secondes, écrits uniquement lorsqu’ils changent ; heartbeat
  toutes les cinq minutes. Événements noyau USB/xone/GIP filtrés ; pas de boutons
  ni de frappes clavier enregistrés par la collecte permanente.
- Métadonnées ajoutées : version/srcversion du pilote chargé, liste des périphériques
  GIP, état de recherche `pairing`, clients, vrais inputs, alimentation USB, batterie.
- Export inclut DKMS et `modinfo`, journal récent et archives dédiées. Les rapports
  locaux peuvent contenir identifiants matériels, chemins et noms de jeux : les
  relire et anonymiser avant toute publication.
- « Marquer une coupure » est facultatif. L’heure approximative suffit pour enquêter.
- Rapports GUI dans `~/Documents/Diagnostic-manettes/`. Les rapports de cette
  intervention sont dans `~/Documents/tmp/diagnostic-xbox-20261107/`.

Le collecteur rejoue cinq minutes du journal à son démarrage et collecte pendant
la session utilisateur ; aucune promesse de collecte avant login, pendant arrêt,
ou au-delà des plafonds. La réserve journald globale n’a PAS été agrandie à 1 Go :
la proposition de l’agent précédent n’avait pas été appliquée. L’archive dédiée,
elle, était et reste fonctionnelle.

### Reprise si cela récidive

```sh
systemctl --user status diagnostic-manettes.service
~/.local/bin/diagnostic-manettes snapshot
~/.local/bin/diagnostic-manettes report
dkms status -m xone
cat /sys/module/xone_dongle/version
modinfo xone_dongle
journalctl -b -k --since '-20min' --no-pager
```

Examiner les traces **avant** de réinitialiser : comparer compteur, inputs, GIP,
version chargée et version installée, erreurs de transport, heure d’extinction et
réapparition. Distinguer extinction normale, handshake incomplet et perte USB.
Ne pas se contenter d’un voyant fixe. Si une récupération doit être testée, tenir
compte des autres joueurs actifs et du coût d’une coupure du récepteur.

## Distance : problème distinct, résolu la veille

Steam créait deux manettes virtuelles Xbox 360 en plus des deux Xbox physiques,
donc quatre contrôleurs et deux joueurs répondant au même bouton. **Steam Input
a été désactivé uniquement pour Distance** ; le nombre a été corrigé.

Des profils de commandes différaient ensuite. Huit XML UTF-16 ont été modifiés dans
`~/.config/refract/Distance/` : `Settings/ControlsSettings.xml` et les sept profils
existants. L’association du nom `Microsoft Xbox Controller` a été fixée à
`Xbox 360 Default`, globalement et dans chaque profil. Les schémas personnalisés,
la progression et les autres réglages n’ont pas été effacés. Sauvegarde préalable :
`~/Documents/tmp/distance-controls-backup-20261106-231837/`.

Résultat visé : A valide, B revient ; l’utilisateur avait confirmé la correction.
Ces réglages du jeu n’expliquent pas les pertes radio et ne doivent pas être
réinitialisés pour diagnostiquer le dongle. Les profils privés ne sont pas publiés.
