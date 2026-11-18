# Récupération du signal TV HDMI

Certaines TV (ici une Panasonic) restent en « pas de signal » quand on les rallume ou qu'on
revient sur l'entrée HDMI du PC : la carte graphique croit l'écran toujours actif et ne
renvoie pas l'image. Deux remèdes :

| Pièce | Rôle |
|---|---|
| `~/.local/share/hdmi-recovery/recover.py` + service utilisateur `hdmi-recovery.service` | écoute les événements hotplug DRM (pyudev) ; quand la TV revient et que l'état est stable (3 s), coupe puis rallume la sortie (`kscreen-doctor --dpms off/on`). Relance aussi `retro-screensaver.service` s'il tourne (son processus graphique peut planter à la perte de l'écran). |
| `/usr/local/bin/hdmi-redetect` (root) | force la re-détection de toutes les sorties HDMI (`status` = `detect`, puis `on` quelques secondes si la TV ne répond pas) |
| `/etc/sudoers.d/hdmi-redetect` | autorise **uniquement** ce script sans mot de passe : `<utilisateur> ALL=(root) NOPASSWD: /usr/local/bin/hdmi-redetect` (mode 440, validé par `visudo -cf` avant installation) |
| `~/.local/share/applications/hdmi-redetect.desktop` + raccourci **Alt+F9** | lance la récupération manuelle par changement de mode, même à l'aveugle |

## Variable (profil privé)

```toml
[vars]
HDMI_TV_EDID_MATCH = "Panasonic"   # texte présent dans l'EDID de la TV
```

Pour trouver la valeur : `strings /sys/class/drm/card*-HDMI-A-*/edid` (nom du fabricant
ou du modèle). Le service ne réagit qu'à la sortie HDMI dont l'EDID contient ce texte.

Journal : `journalctl --user -u hdmi-recovery -f` ; `journalctl -t hdmi-redetect`.

## Retour d’expérience : TV sans signal le 16 novembre 2026

La récupération initiale a été mise en place dans la conversation Paseo/Codex du 16 octobre 2026, puis intégrée au module dans le commit `374bb6d` du 27 octobre. Le script installé à cette date avait encore le constructeur TV en dur ; le module utilise depuis la variable privée `HDMI_TV_EDID_MATCH`. Cette différence ne prouve pas une cause de panne.

Le 16 novembre, la TV physique affichait « aucun signal » alors que KScreen indiquait la sortie HDMI connectée, activée et en 4K 60 Hz HDR. Le service de récupération avait exécuté OFF/ON ; le noyau avait signalé `Flip event timeout on head 0` pendant la récupération. Une simple redétection par le helper root n’a pas rétabli l’image. Un passage temporaire en 1080p 60 Hz pendant cinq secondes, suivi du retour en 4K 60 Hz, l’a rétablie : confirmation visuelle de l’utilisateur. Cela établit une méthode de récupération, sans démontrer la cause du défaut NVIDIA/HDMI.

Le raccourci Alt+F9 et l’application **Récupérer le signal HDMI** lancent maintenant `manual.py`. Ce script choisit un autre mode standard (1080p proche de 60 Hz en priorité), puis restaure **le mode initial exact**, y compris en cas d’échec intermédiaire. Il ne change ni HDR, ni échelle, ni position, ne coupe pas la seule sortie et ne redémarre ni session graphique ni traitement GPU. Il refuse d’agir si plusieurs sorties HDMI actives rendent la cible ambiguë. État avant intervention : `~/.local/state/hdmi-recovery/before-manual.json`.

Le changement de résolution reste **manuel** : l’automatisme de hotplug conserve sa récupération DPMS et ne change pas la résolution à chaque retour de la TV. Un message logiciel « signal réactivé » ne garantit pas que la TV reçoive effectivement une image.

## 4K limitée à 30 Hz : EDID de la Panasonic TX-55MZ800E

Le modèle a été retrouvé dans l’historique Paseo du 16 octobre : **Panasonic
TX-55MZ800E, Google TV 11, plateforme MB185**. Les libellés génériques
« HDMI Auto Setting / Mode 1 / Mode 2 » d’autres Panasonic ne correspondent pas
au menu de ce modèle.

Le 18 novembre 2026, après une baisse rapportée en 1080p, le retour manuel en 4K
ne proposait plus 60 Hz, même après redémarrage. Le pilote NVIDIA fonctionnait.
L’EDID transmis par la TV annonçait un mode préféré 3840×2160 à 30 Hz (297 MHz),
sans VIC 97 ni bloc HDMI Forum proposant les capacités à 600 MHz.

**Solution confirmée par l’utilisateur : forcer « EDID 2.0 » sur l’entrée HDMI du PC.**
En restant sur cette entrée, ouvrir :

**MENU → Options TV → Paramètres → Chaînes et entrées → Entrées → HDMI EDID Version**
(« Version EDID HDMI » suivant la traduction), puis sélectionner **EDID 2.0**.
Le réglage est sur la TV et doit être vérifié manuellement lors d’une restauration ;
les dotfiles ne peuvent pas le déployer. Aucun menu usine, changement de câble,
mode vidéo forcé non annoncé ou modification du pilote n’a été nécessaire.

Après le changement, contrôle côté PC : **3840×2160 à 60,00 Hz réellement actif**,
EDID préféré à 60 Hz / 594 MHz, VIC 97 et bloc HDMI Forum à 600 MHz présents.
Cela confirme le rôle des capacités EDID présentées par la TV. L’ancienne valeur
(1.4 ou Auto) n’a pas été relevée : ne pas affirmer laquelle était sélectionnée.
Le déclencheur initial de la régression n’est pas établi.

Pour distinguer ce cas d’une simple perte de signal :

```sh
kscreen-doctor -o
# Adapter le chemin au connecteur réellement connecté :
edid-decode /sys/class/drm/card1-HDMI-A-1/edid
```

Si la TV n’annonce plus 60 Hz, vérifier d’abord son réglage EDID plutôt que
relancer le helper qui alterne des modes vidéo. Les EDID avant/après et les
constats bruts sont conservés localement dans
`~/Documents/tmp/diagnostic-hdmi-20261118/`, sans les publier dans Git.

Référence : [manuel officiel TX-55MZ800E / TX-65MZ800E, section HDR/HLG, français p. 6](https://tda.panasonic-europe-service.com/docs/1524930969-6011-3C6A1174128470471F7279CE9A877DBCAA5D2426/pgrp001/pcat033/tx55mz800e/997958/TX-55MZ800E_TX-65MZ800E.pdf).
