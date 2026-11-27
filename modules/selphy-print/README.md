# Selphy Print

Appli Qt (PySide6) pour imprimer des cartes postales 100 × 148 mm sur une
Canon SELPHY CP1500. La même source tourne sous Windows ; là-bas elle est
compilée en un seul `.exe` avec PyInstaller.

- Photo glissée, ouverte (Ctrl+O) ou collée (Ctrl+V) ; déplacement à la souris,
  zoom à la molette, double-clic = remplir / photo entière.
- Mise en page : 1 photo, 2 côte à côte, 2 superposées, 4 (gouttière blanche 2 mm).
- File d'impression à gauche (CUPS : `lpstat` / `cancel`) avec annulation.
- Impression : `lp -o print-scaling=fill` avec la taille carte postale sans
  bordure du PPD généré par CUPS (`*100x148*`/`hagaki`/`postcard` + `Borderless`).

## Calibration sans bordure

En sans bordure, la Selphy agrandit l'image d'environ 7 % ; les languettes
perforées coupent en plus de façon asymétrique. Mesures d'une mire imprimée
depuis Windows (mm coupés sur une image paysage, languettes détachées) :
haut 3,45 · droite 5,7 · bas 3,0 · gauche 4,0. L'appli réduit et décale le
rendu pour que le cadre affiché corresponde à la carte finie, et prolonge les
bords de la photo dans la zone coupée.

Ces valeurs viennent du pilote Windows (IPP Class Driver). Sous CUPS, imprimer
une mire et la comparer : si le recadrage ou la rotation diffèrent, ajuster
dans **Calibration** (enregistré dans `~/.config/SelphyPrint/SelphyPrint.conf`).

## Imprimante

La partie `printer-queue` crée la file `Canon_SELPHY` en IPP Everywhere
(`lpadmin -m everywhere`) à partir de l'adresse trouvée par mDNS ; elle
active `avahi-daemon` et `cups` si besoin. Imprimante allumée et sur le Wi-Fi
au moment de l'application. Adresse fixe possible via `SELPHY_URI`
(ex. `ipp://selphy.local/ipp/print`).

## Compiler l'exe Windows

```powershell
py -m venv .venv; .venv\Scripts\pip install PySide6 pyinstaller
.venv\Scripts\pyinstaller --onefile --windowed --name SelphyPrint selphy_print.py
```
