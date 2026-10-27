# Base CachyOS : alias, fastfetch, plugin « done », ajout de ~/.local/bin au PATH…
source /usr/share/cachyos-fish-config/cachyos-config.fish

# Remplacer le message d'accueil (et désactiver fastfetch) :
#function fish_greeting
#end

# ~/.local/bin en tête du PATH (une seule fois, sans doublon)
fish_add_path --global --move $HOME/.local/bin

# Clés API chargées depuis un fichier local non commité (voir secrets.fish.example)
source ~/.config/fish/secrets.fish 2>/dev/null || true

# WezTerm - contourne le bug Wayland DRM syncobj
alias wezterm 'WAYLAND_DISPLAY= /usr/bin/wezterm'

# Outils installés dans le dossier personnel (ignorés s'ils sont absents)
fish_add_path $HOME/.spicetify
fish_add_path $HOME/.opencode/bin
