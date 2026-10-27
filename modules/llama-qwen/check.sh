#!/usr/bin/env bash
ls ~/.local/opt/llama.cpp/build/.stamp-* &>/dev/null && [[ -x ~/.local/opt/llama.cpp/build/bin/llama-server ]]
