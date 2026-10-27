#!/usr/bin/env bash
set -euo pipefail
source "$DOTFILES_LIB"
need_vars LLM_MODEL_DIR LLM_MODEL_FILE LLM_CUDA_ARCH

# 1. llama.cpp — commit épinglé = build identique à celui validé sur flystation
REF=${LLAMA_CPP_REF:-2115b73d8ebdbd659075cce66c609506863bc826}
SRC=~/.local/opt/llama.cpp
[[ -d $SRC/.git ]] || git clone https://github.com/ggml-org/llama.cpp "$SRC"
git -C "$SRC" fetch --quiet origin
stamp="$SRC/build/.stamp-$REF-$LLM_CUDA_ARCH"
if [[ ! -f $stamp ]]; then
    git -C "$SRC" checkout --quiet "$REF"
    export PATH="/opt/cuda/bin:$PATH"
    cmake -S "$SRC" -B "$SRC/build" -G Ninja \
        -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=ON \
        -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES="$LLM_CUDA_ARCH" \
        -DGGML_CUDA_FA=ON -DGGML_CUDA_GRAPHS=ON -DGGML_NATIVE=ON -DLLAMA_OPENSSL=ON
    cmake --build "$SRC/build" --target llama-server llama-cli -j"$(nproc)"
    rm -f "$SRC"/build/.stamp-*; touch "$stamp"
    success "llama.cpp compilé ($REF, sm $LLM_CUDA_ARCH)"
else
    info "llama.cpp déjà compilé ($REF)"
fi

# 2. Modèle : copié depuis le NAS s'il manque (évite de re-télécharger 18 Go)
if [[ ! -f $LLM_MODEL_DIR/$LLM_MODEL_FILE ]]; then
    if [[ -n ${LLM_MODEL_SOURCE:-} && -d $LLM_MODEL_SOURCE ]]; then
        info "copie du modèle depuis $LLM_MODEL_SOURCE…"
        rsync -a --info=progress2 --include='*.gguf' --exclude='*' "$LLM_MODEL_SOURCE/" "$LLM_MODEL_DIR/"
    else
        warn "modèle absent : $LLM_MODEL_DIR/$LLM_MODEL_FILE (définir LLM_MODEL_SOURCE ou le copier)"
    fi
fi
mkdir -p ~/logs
success "icône : menu « Serveur LLM local » (llm-tray) — API http://$(hostname).local:${LLM_PORT:-8081}/v1"
