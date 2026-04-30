source /usr/share/cachyos-fish-config/cachyos-config.fish

# overwrite greeting
# potentially disabling fastfetch
#function fish_greeting
#    # smth smth
#end
export PATH="$HOME/.local/bin:$PATH"
set -gx PATH $HOME/.local/bin $PATH
set -gx ANTHROPIC_BASE_URL "https://api.poe.com"
# Clés API chargées depuis un fichier local non commité
source ~/.config/fish/secrets.fish 2>/dev/null || true

# WezTerm - contourne le bug Wayland DRM syncobj
alias wezterm 'WAYLAND_DISPLAY= /usr/bin/wezterm'

fish_add_path /home/ryzen/.spicetify
