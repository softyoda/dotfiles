#!/usr/bin/env bash
# Serveur llama.cpp (API OpenAI-compatible) sur le LAN : http://<machine>.local:${LLM_PORT}/v1
# Réglages repris à l'identique de flystation (RTX 5090, Qwen3.8-27B Q4_K_P, 224k de contexte).
set -euo pipefail
export PATH="/opt/cuda/bin:$PATH"

BIN=${HOME}/.local/opt/llama.cpp/build/bin/llama-server
DIR=${LLM_MODEL_DIR}
MODEL="$DIR/${LLM_MODEL_FILE}"
MMPROJ="$DIR/${LLM_MMPROJ_FILE}"

ARGS=(
  --model "$MODEL"
  --alias ${LLM_ALIAS}
  --host 0.0.0.0 --port ${LLM_PORT}
  --ctx-size 229376 --parallel 1
  --gpu-layers all --flash-attn on
  --cache-type-k q8_0 --cache-type-v q8_0
  # Gros batches = prefill rapide. Nécessite que le GPU ne soit pas tué par le
  # watchdog d'affichage (voir README : écran sur l'iGPU ou option X11).
  --batch-size 2048 --ubatch-size 512
  --spec-type draft-mtp --spec-draft-n-max 2 --spec-draft-p-min 0
  --jinja --no-warmup
  --chat-template-file "$DIR/chat_template.jinja"
  --reasoning-format deepseek
  --reasoning-preserve
)
[ -f "$MMPROJ" ] && ARGS+=(--mmproj "$MMPROJ")   # vision si le mmproj est présent

exec "$BIN" "${ARGS[@]}"
