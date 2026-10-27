local wezterm = require 'wezterm'
local config = wezterm.config_builder()

-- Apparence
config.color_scheme = 'Tokyo Night'
config.font = wezterm.font('JetBrains Mono', { weight = 'Regular' })
config.font_size = 12.0
config.window_background_opacity = 0.92
config.macos_window_background_blur = 20

-- Fenêtre
config.window_padding = { left = 8, right = 8, top = 6, bottom = 6 }
config.enable_tab_bar = true
config.use_fancy_tab_bar = true
config.hide_tab_bar_if_only_one_tab = true
config.window_close_confirmation = 'NeverPrompt'

-- Comportement souris
config.mouse_bindings = {
  -- Clic droit = coller
  {
    event = { Down = { streak = 1, button = 'Right' } },
    mods = 'NONE',
    action = wezterm.action.PasteFrom 'Clipboard',
  },
  -- Sélection → clipboard automatique
  {
    event = { Up = { streak = 1, button = 'Left' } },
    mods = 'NONE',
    action = wezterm.action.CompleteSelectionOrOpenLinkAtMouseCursor 'Clipboard',
  },
}

-- Scroll
config.scrollback_lines = 10000

return config
