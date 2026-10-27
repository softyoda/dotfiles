/**
 * reasoning-effort plugin
 *
 * Drives the Qwen local LLM (llama.cpp) "reasoning effort" per agent.
 *
 * The local model runs the froggeric Qwen-Fixed chat template, which accepts a
 * `reasoning_effort` chat-template kwarg: 'low' | 'medium' | 'xhigh'
 * (plus 'none'/'off' to disable thinking). llama.cpp only reads it from
 * `chat_template_kwargs` in the request body, so this plugin injects that.
 *
 * Effort levels the template supports (reasoning_effort kwarg):
 *   xhigh  - deep reasoning ("think carefully", validate assumptions)
 *   high   - real but proportionate: thinks through non-trivial tasks, skips trivial ones
 *   low    - brief thinking
 *   medium - natural baseline, no instruction injected
 *   none   - thinking fully disabled
 *
 * Mapping (edit here to taste):
 *   plan   -> xhigh (deep reasoning, always)
 *   build  -> high  (thinks on the tasks that need it, not on every prompt)
 *   other  -> none  (no thinking - fast)
 *
 * Guarded to the qwen-local provider so it never touches other backends.
 */

import type { Plugin } from "@opencode-ai/plugin"

const PROVIDER = "qwen-local"

const EFFORT_BY_AGENT: Record<string, string> = {
  plan: "xhigh",
  build: "high",
  general: "none",
  explore: "none",
  'local-qwen': 'medium',
  'worker-local': 'medium',
}
const DEFAULT_EFFORT = "none"

export default (async () => {
  return {
    "chat.params": async (
      input: { agent?: string; model?: { providerID?: string; modelID?: string } },
      output: { options: Record<string, any> },
    ) => {
      const providerID = input.model?.providerID
      if (providerID !== PROVIDER) return

      const effort = EFFORT_BY_AGENT[input.agent ?? ""] ?? DEFAULT_EFFORT
      output.options = {
        ...output.options,
        chat_template_kwargs: {
          ...(output.options?.chat_template_kwargs ?? {}),
          reasoning_effort: effort,
        },
      }
    },
  }
}) satisfies Plugin
