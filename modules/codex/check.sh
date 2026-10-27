#!/usr/bin/env bash
cfg="$HOME/.codex/config.toml"
grep -qE '^model_context_window[[:space:]]*=' "$cfg" 2>/dev/null &&
grep -qE '^model_auto_compact_token_limit[[:space:]]*=' "$cfg"
