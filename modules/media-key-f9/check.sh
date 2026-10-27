#!/usr/bin/env bash
# Valeur : « raccourcis actifs,raccourcis par défaut,libellé » ; raccourcis séparés par une tabulation.
v=$(kreadconfig6 --file kglobalshortcutsrc --group mediacontrol --key playpausemedia)
tr '\t' '\n' <<<"${v%%,*}" | grep -qx F9
