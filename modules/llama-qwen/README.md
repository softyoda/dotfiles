# LLM local (llama.cpp + Qwen3.8-27B)

Réglages repris **à l'identique** de flystation (RTX 5090, 32 Go) :

- llama.cpp `2115b73` compilé CUDA `sm_120a`, FlashAttention, CUDA graphs, `GGML_NATIVE`
- modèle `Qwen3.8-27B-Uncensored-HauhauCS-Aggressive-Q4_K_P.gguf` (17,9 Go) + mmproj BF16 (vision)
- 229 376 tokens de contexte, cache KV `q8_0`, tout sur le GPU, `--parallel 1`
- décodage spéculatif MTP (`--spec-type draft-mtp --spec-draft-n-max 2`)
- batch 2048 / ubatch 512, template de chat « froggeric v22.4 » (`files/chat_template.jinja`),
  raisonnement au format deepseek conservé

API OpenAI-compatible : `http://<machine>.local:8081/v1` (utilisée par le provider
`qwen-local` d'OpenCode, variable `LLM_SERVER_URL`). Web UI llama.cpp à la racine.

## Watchdog d'affichage

Quand le GPU de calcul affiche aussi un écran, le pilote NVIDIA peut tuer les
noyaux CUDA trop longs (« launch timed out ») avec de gros batches à long contexte.
Sur Mint/X11 c'était réglé par `/etc/X11/xorg.conf.d/10-nvidia-notdr.conf`
(`Option "Interactive" "0"`), qui ne s'applique pas sous Plasma **Wayland**.
L'écran reste volontairement sur la 5090 (accès RustDesk sans dongle HDMI).
À tester après réinstallation : si l'erreur apparaît à long contexte, baisser
`--batch-size`/`--ubatch-size` (ex. 1024/256) dans `files/serve.sh`.

## Variables (profil)

| Variable | flystation |
|---|---|
| `LLM_MODEL_DIR` | `~/models/qwen38-27b` |
| `LLM_MODEL_FILE` | `Qwen3.8-27B-Uncensored-HauhauCS-Aggressive-Q4_K_P.gguf` |
| `LLM_MMPROJ_FILE` | `mmproj-Qwen3.8-27B-Uncensored-HauhauCS-Aggressive-BF16.gguf` |
| `LLM_MODEL_SOURCE` | copie sauvegardée sur le NAS |
| `LLM_ALIAS` / `LLM_PORT` | `qwen38-uncensored` / `8081` |
| `LLM_CUDA_ARCH` | `120a` (RTX 50xx) — `86` pour une RTX 30xx |

Mettre à jour llama.cpp : changer `LLAMA_CPP_REF` dans le profil puis `dotctl apply llama-qwen`.
