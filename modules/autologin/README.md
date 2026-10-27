# Connexion automatique (Plasma Login Manager)

Écrit `/etc/plasmalogin.conf.d/autologin.conf` :

```ini
[Autologin]
User=<utilisateur courant>
Session=<AUTOLOGIN_SESSION, « plasma » par défaut>
```

Variable facultative dans le profil privé :

```toml
[vars]
AUTOLOGIN_SESSION = "plasma"   # ex. gamescope-session, plasmax11…
```

C'est le nom d'un fichier `.desktop` de `/usr/share/wayland-sessions/` ou
`/usr/share/xsessions/` (sans l'extension).

## Étapes manuelles / pièges

- Le module suppose que **Plasma Login Manager** (`plasmalogin.service`) est le
  gestionnaire de connexion actif. Sous SDDM, l'équivalent est `/etc/sddm.conf.d/autologin.conf`
  (même syntaxe) — à faire à la main.
- Les fichiers de `/etc/plasmalogin.conf.d/` sont lus par ordre alphabétique : un fichier
  trié après `autologin.conf` (ex. `zz-steamos-autologin.conf` installé par les paquets
  « mode jeu » / Steam Deck) **remplace** la session. `apply.sh` le signale ; le
  supprimer ou l'ajuster à la main si ce n'est pas voulu.
- Toute la sécurité repose sur le chiffrement du disque : avec l'autologin, quiconque
  allume la machine accède à la session.
