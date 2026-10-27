# Laser Helios DAC

Chaîne : TouchDesigner (Wine) → paquets UDP `127.0.0.1:45457` → `helios_bridge.py`
(service utilisateur `helios-bridge`) → `libHeliosDacAPI.so` → DAC en USB
(1209:e500). La règle udev donne l'accès au groupe `users` (tag `uaccess`).

## Côté TouchDesigner

Les scripts sont déposés dans `~/.local/share/touchdesigner-linux/` :

- `helios_td_sender.py` : à coller dans le callback `onCook` d'un Script CHOP
  branché sur un Laser CHOP (canaux `tx ty r g b i`) ; les instructions de
  mise en place sont en tête du fichier.
- `helios_sender.py` : variante minimale avec paramètre `Pps` (30000 par défaut).

Format du protocole : voir l'en-tête de `helios_bridge.py`.

## Notes

- La bibliothèque est compilée depuis le SDK C++ (`Grix/helios_dac`, commit
  épinglé dans `apply.sh`) ; elle dépend de `libusb-1.0`.
- Le fichier `/usr/local/lib/.libHeliosDacAPI.commit` mémorise le commit
  compilé ; le supprimer force une recompilation.
- Débogage : `journalctl --user -u helios-bridge -f`.
