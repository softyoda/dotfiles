# Récupération du signal TV HDMI

Certaines TV (ici une Panasonic) restent en « pas de signal » quand on les rallume ou qu'on
revient sur l'entrée HDMI du PC : la carte graphique croit l'écran toujours actif et ne
renvoie pas l'image. Deux remèdes :

| Pièce | Rôle |
|---|---|
| `~/.local/share/hdmi-recovery/recover.py` + service utilisateur `hdmi-recovery.service` | écoute les événements hotplug DRM (pyudev) ; quand la TV revient et que l'état est stable (3 s), coupe puis rallume la sortie (`kscreen-doctor --dpms off/on`). Relance aussi `retro-screensaver.service` s'il tourne (son processus graphique peut planter à la perte de l'écran). |
| `/usr/local/bin/hdmi-redetect` (root) | force la re-détection de toutes les sorties HDMI (`status` = `detect`, puis `on` quelques secondes si la TV ne répond pas) |
| `/etc/sudoers.d/hdmi-redetect` | autorise **uniquement** ce script sans mot de passe : `<utilisateur> ALL=(root) NOPASSWD: /usr/local/bin/hdmi-redetect` (mode 440, validé par `visudo -cf` avant installation) |
| `~/.local/share/applications/hdmi-redetect.desktop` + raccourci **Alt+F9** | lance `sudo -n hdmi-redetect` depuis le clavier, même à l'aveugle |

## Variable (profil privé)

```toml
[vars]
HDMI_TV_EDID_MATCH = "Panasonic"   # texte présent dans l'EDID de la TV
```

Pour trouver la valeur : `strings /sys/class/drm/card*-HDMI-A-*/edid` (nom du fabricant
ou du modèle). Le service ne réagit qu'à la sortie HDMI dont l'EDID contient ce texte.

Journal : `journalctl --user -u hdmi-recovery -f` ; `journalctl -t hdmi-redetect`.
