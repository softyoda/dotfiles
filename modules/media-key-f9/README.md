# F9 = lecture/pause

Pour les claviers sans touches multimédia : **F9** déclenche « Démarrer / Mettre en pause
la lecture du média » (MPRIS : Spotify, navigateur, VLC…), en plus de la touche
*Media Play* habituelle.

Réglé dans `~/.config/kglobalshortcutsrc` :

```ini
[mediacontrol]
playpausemedia=F9\tMedia Play,Media Play,Démarrer / Mettre en pause la lecture du média
```

Effectif après reconnexion (KWin relit ses raccourcis au démarrage de session). Équivalent
graphique : Paramètres → Clavier → Raccourcis → Contrôleur de média.

Conséquence : F9 n'arrive plus aux applications (ex. « Exécuter » dans certains IDE).
