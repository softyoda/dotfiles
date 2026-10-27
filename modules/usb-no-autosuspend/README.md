# Pas de mise en veille USB

`/etc/udev/rules.d/50-usb-autosuspend.rules` :

```
ACTION=="add", SUBSYSTEM=="usb", ATTR{power/autosuspend}="-1"
```

À chaque branchement, la mise en veille automatique (*autosuspend*) du périphérique USB
est désactivée. Remède classique aux souris/claviers sans fil qui « s'endorment », aux DAC
audio qui craquent au réveil ou aux dongles qui se déconnectent.

Contrepartie : un peu plus de consommation, négligeable sur un PC fixe ; à éviter sur un
portable sur batterie. Vérifier : `cat /sys/bus/usb/devices/*/power/autosuspend` (→ `-1`).
