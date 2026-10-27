# Firefox : second profil

Pour un colocataire ou un invité : un profil Firefox totalement séparé
(historique, marque-pages, mots de passe, extensions, comptes connectés).

- Nom du profil : variable `FIREFOX_EXTRA_PROFILE` du profil privé (ex. `Colloc`).
- Profil créé par `firefox -CreateProfile` dans `~/.config/mozilla/firefox`
  (emplacement XDG des Firefox récents ; `~/.mozilla/firefox` sur les anciennes
  installations). Rien n’est créé s’il existe déjà : relancer le module est sans risque.
- Lanceur `Firefox (<nom>)` : `firefox -P <nom> --no-remote --name firefox-<nom>`,
  avec sa propre icône et sa propre classe de fenêtre (entrée séparée dans la
  barre des tâches).

`--no-remote` : cette fenêtre est indépendante du Firefox principal ; un
deuxième clic sur le lanceur alors que le profil est déjà ouvert affiche
« Firefox est déjà ouvert » — utiliser Ctrl+N dans la fenêtre existante.

Supprimer le profil : `firefox -P` (gestionnaire de profils) → Supprimer, puis
effacer `~/.local/share/applications/firefox-<nom>.desktop`.
