#!/usr/bin/env bash
shell=$(getent passwd "$USER" | cut -d: -f7)
[[ "$shell" == */fish ]]
