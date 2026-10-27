# Mullvad VPN

- Paquet AUR `mullvad-vpn-bin` (interface) + `mullvad-vpn-daemon-bin` (démon,
  `mullvad`, `mullvad-exclude`), services `mullvad-daemon` et
  `mullvad-early-boot-blocking` activés.
- Réglages appliqués par la CLI dans `apply.sh` :
  sortie en **Belgique** (`MULLVAD_LOCATION=xx dotctl apply mullvad` pour un
  autre pays), pas de multihop, connexion automatique, **LAN autorisé**
  (NAS, imprimante, KDE Connect…), mode verrouillage désactivé, **IPv6 coupé**
  dans le tunnel, **échange de clés post-quantique**, **DAITA** (multihop auto
  si nécessaire), anti-censure auto, DNS Mullvad sans filtrage.
- Interface : démarrage automatique réduit dans la barre système, fenêtre
  détachable, notifications système.
- Exclure une appli du tunnel : `mullvad-exclude <commande>` (utilisé par le
  module `vesktop`).

## Étape manuelle : connexion au compte

Le numéro de compte est un secret : il n’est jamais stocké dans le dépôt.

```sh
mullvad account login        # demande le numéro de compte
mullvad connect
```

Si le nombre maximal d’appareils est atteint, en retirer un depuis
https://mullvad.net/account ou `mullvad account list-devices` / `revoke-device`.
