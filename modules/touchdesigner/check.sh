#!/usr/bin/env bash
[[ $(xdg-mime query default application/x-touchdesigner-toe) == touchdesigner-file.desktop ]] &&
[[ $(xdg-mime query default application/x-touchdesigner-tox) == touchdesigner-file.desktop ]]
