# DNS chiffré (DNS over TLS)

`/etc/systemd/resolved.conf.d/dot.conf` :

```ini
[Resolve]
DNS=1.1.1.1#cloudflare-dns.com 9.9.9.9#dns.quad9.net
DNSOverTLS=yes
DNSSEC=no
```

- Les requêtes partent chiffrées (TLS, port 853) vers Cloudflare puis Quad9 ; le suffixe
  `#nom` sert à vérifier le certificat du serveur.
- `DNSOverTLS=yes` est **strict** : pas de repli en clair. Un réseau qui bloque le port 853
  (certains Wi-Fi publics/portails captifs) n'aura plus de DNS → passer temporairement en
  `opportunistic`.
- Les DNS annoncés par le routeur (DHCP) restent connus de resolved ; pour forcer *toutes*
  les requêtes vers ces serveurs, ajouter `Domains=~.` dans `[Resolve]`.
- Prérequis : `/etc/resolv.conf` doit être le stub de resolved
  (`sudo ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf`), ce qui est le cas
  par défaut sur CachyOS avec NetworkManager.

Vérifier : `resolvectl status` (ligne `+DNSOverTLS`) et `resolvectl query archlinux.org`.

## Interaction avec Mullvad

Quand le tunnel Mullvad est connecté, l'application impose **ses** DNS (ceux du tunnel ou
ceux réglés dans Mullvad → Paramètres → VPN → DNS) via systemd-resolved, sur l'interface
`wg0-mullvad` avec la route `~.` : ce fichier n'est alors plus utilisé. Il reprend la main
dès que le VPN est coupé. C'est voulu : passer par les DNS de Mullvad évite les fuites DNS
hors tunnel. Ne pas régler un « DNS personnalisé » dans Mullvad vers Cloudflare/Quad9 sauf
besoin précis (les requêtes ressortiraient en clair depuis le serveur VPN).
