import type { Plugin } from '@opencode-ai/plugin'
import { pathToFileURL } from 'node:url'
import { createHash } from 'node:crypto'
import { mkdir, readFile, writeFile, rename } from 'node:fs/promises'
import { homedir } from 'node:os'
import { join } from 'node:path'

// Shared source lives on the NAS; runtime dependencies remain machine-local.
const sdkEntry = join(process.env.OPENCODE_CONFIG_DIR || join(homedir(), '.config', 'opencode'), 'node_modules', '@opencode-ai', 'plugin', 'dist', 'index.js')
const { tool } = await import(pathToFileURL(sdkEntry).href)

const LOCAL_URL = '${LLM_SERVER_URL}'
const MODELS: Record<string, string> = {
  'worker-deepseek': 'poe/deepseek-v4.1-flash',
  'worker-astra': 'openai/gpt-6-astra',
  'worker-opus': 'poe/anthropic/claude-opus-4.8',
  'worker-local': 'qwen-local/qwen38-uncensored',
}
const WORKER = `Execute the bounded task supplied by the lead. Do not delegate further.
Work only within assigned file ownership. Return a concise result with evidence, files changed,
checks actually run, and unresolved issues. Do not invent verification. Use explicit shell timeouts.
Avoid unrelated refactors and repeated unsuccessful attempts; report a blocker instead.`
const LEAD = `Handle conversation, small changes, and tightly coupled work directly.
Delegate only when independent work, expertise, or context separation justifies its overhead.
Before the first delegation in a project, explain the task breakdown, exact worker models,
whether they may edit, and maximum concurrency; call team_allowance to request ONE approval.
Reuse that project allowance; ask again only to expand it. An allowance is capacity, not a target.
For first-time selection or when the user requests team configuration, use the built-in question
tool for model multi-selection, priority and numeric concurrency choices BEFORE team_allowance.
Follow the /team command workflow. Never substitute a yes/no permission prompt for selection.
Never build or open an external selector. If question is unavailable, report that blocker.
The former worker-openai/gpt-5.4-mini is unavailable on this ChatGPT connection; never select it.
Prefer economical Mini (only if verified available) or DeepSeek. Follow the user's saved worker priority order.
Astra/Opus are expensive opt-in exceptions: explain why they are needed and obtain explicit model selection.
Never fall back to Astra/Opus automatically when a cheap worker fails.
Never silently expand to a costly model. Routine installs can run as monitored background commands without an AI worker.
Only use worker-local if it is available. Keep local work sequential and reuse a related local
worker session rather than rotating contexts. Never route memory maintenance to the local worker.
For parallel work use native background tasks when available, disjoint write ownership,
and completion events; do not duplicate a delegated task. Do not spawn agents just to fill slots.
Workers may not delegate. Keep prompts bounded and reports concise. All shell commands need
explicit timeouts. Do not retry unavailable providers in a loop. Call team_status to inspect allowance.
Never commit or push unless requested. Preserve user scenes, files, and conversation history.`
type Allowance = { version: 2; project: string; workers: string[]; models: Record<string,string>; limits: Record<string,number>; concurrency: number; approvedAt: string }

const setup: Plugin = async ({ project, directory, worktree, client }) => {
  const identity = `${project.id}:${worktree || directory}`
  const hash = createHash('sha256').update(identity).digest('hex').slice(0, 24)
  // Approval state stays outside the repository: repository files cannot grant permission.
  const stateRoot = join(process.env.XDG_STATE_HOME || join(homedir(), '.local', 'state'), 'opencode', 'team-allowances')
  const stateFile = join(stateRoot, `${hash}.json`)
  let allowance: Allowance | undefined
  try {
    const saved = JSON.parse(await readFile(stateFile, 'utf8'))
    if (saved.version === 2 && saved.project === identity && Number.isInteger(saved.concurrency)
      && saved.concurrency > 0 && saved.concurrency <= 10 && Array.isArray(saved.workers)
      && saved.workers.every((x: string) => x in MODELS && saved.models?.[x] === MODELS[x]
        && Number.isInteger(saved.limits?.[x]) && saved.limits[x] > 0 && saved.limits[x] <= saved.concurrency)) allowance = saved
  } catch {}
  let healthAt = 0, online = false
  async function health() {
    if (Date.now() - healthAt < 15000) return online
    healthAt = Date.now()
    try {
      const response = await fetch(`${LOCAL_URL}/models`, { signal: AbortSignal.timeout(1200) })
      const body = await response.json() as any
      online = response.ok && Array.isArray(body.data) && body.data.length > 0
    } catch { online = false }
    return online
  }
  const initialOnline = await health()
  const active = new Map<string, { worker: string; session?: string }>()
  const calls = new Map<string, string>()
  async function reconcile() {
    if (!active.size) return
    const response = await client.session.status({ query: { directory } })
    const statuses = response.data as Record<string, {type: string}> | undefined
    if (!statuses) return
    for (const [key, job] of active) {
      if (job.session && (!statuses[job.session] || statuses[job.session].type === 'idle')) active.delete(key)
    }
  }
  const noDelegate = { task: 'deny', team_allowance: 'deny', team_status: 'deny' } as const
  // Plan agents do not receive shell, custom, or MCP mutation capabilities.
  const planPermissions = {
    '*': 'deny', read: 'allow', glob: 'allow', grep: 'allow', list: 'allow',
    question: 'allow', webfetch: 'allow', websearch: 'allow', todowrite: 'allow',
    'ctx_search': 'allow', 'ctx_expand': 'allow',
    'context7_*': 'allow',
  } as const
  return {
    config: async (config) => {
      config.default_agent = 'build-astra'
      // Do not silently force a model rejected by the subscription backend.
      if (!config.small_model || config.small_model === 'openai/gpt-5.4-mini') config.small_model = MODELS['worker-deepseek']
      config.lsp = config.lsp ?? true
      config.permission = {
        ...(typeof config.permission === 'object' ? config.permission : {}),
        team_delegation: 'ask',
      }
      config.agent ??= {}
      config.command ??= {}
      config.command.team = {
        description: 'Select worker models, priority and counts in native terminal questions',
        template: `Configure the project worker team; do not launch workers. Call team_status first.
Use the BUILT-IN question tool, not an external dialog or plain-text questionnaire.
1. Ask a multiple:true, custom:false question listing available exact models. DeepSeek is economical;
Astra/Opus must be labeled EXPENSIVE explicit opt-in. Omit unavailable Mini and offline local Qwen.
2. For selected models, ask numeric priority (1 = preferred) and max concurrent workers using
single-select options 1 through 10, custom:false. Local max is fixed at 1. Ask total concurrency
with options 1 through 10. Batch these questions together. For a single model priority is simply 1.
3. Validate ranks are distinct and each per-model limit <= total. Re-ask only invalid answers.
4. Summarize exact selections, then call team_allowance with workers sorted by user priority,
explicit limits and total concurrency, reconfigure:true. Native permission is the final approval,
NOT the selection UI. Cancellation must not save changes. Do not enable unselected models.
If the question tool is unavailable, stop and explain; do not invent an interface or silently
replace selection with yes/no approval. User request: $ARGUMENTS`,
      }
      config.agent.build = { ...config.agent.build, disable: true }
      config.agent.plan = { ...config.agent.plan, disable: true }
      // Custom primary agents otherwise inherit OpenCode's question:deny default.
      // The server feature flag registers the tool but does not grant agents access.
      config.agent['build-astra'] = { mode: 'primary', model: MODELS['worker-astra'], description: 'Build / Astra', prompt: LEAD, permission: { question: 'allow' } }
      config.agent['build-opus'] = { mode: 'primary', model: MODELS['worker-opus'], description: 'Build / Opus', prompt: LEAD, permission: { question: 'allow' } }
      config.agent['plan-astra'] = { mode: 'primary', model: MODELS['worker-astra'], description: 'Plan / Astra (read-only)', prompt: 'Research and plan only. Never implement or delegate edits. Explain a practical plan. Do not modify state.', permission: planPermissions }
      config.agent['plan-opus'] = { mode: 'primary', model: MODELS['worker-opus'], description: 'Plan / Opus (read-only)', prompt: 'Research and plan only. Never implement or delegate edits. Explain a practical plan. Do not modify state.', permission: planPermissions }
      config.agent['cheap-deepseek'] = { mode: 'primary', model: MODELS['worker-deepseek'], description: 'Direct / economical DeepSeek', prompt: LEAD, permission: { question: 'allow' } }
      config.agent['local-qwen'] = { mode: 'primary', model: MODELS['worker-local'], description: 'Direct / local Qwen (online only)', prompt: WORKER, permission: noDelegate, disable: !initialOnline }
      config.agent.general = { ...config.agent.general, disable: true }
      config.agent.explore = { ...config.agent.explore, disable: true }
      config.agent['worker-openai'] = { ...config.agent['worker-openai'], disable: true }
      for (const [name, model] of Object.entries(MODELS)) {
        config.agent[name] = { mode: 'subagent', model, description: `Bounded specialist using ${model}; needs project allowance.`, prompt: WORKER, permission: noDelegate, disable: name === 'worker-local' && !initialOnline }
      }
    },
    tool: {
      team_status: tool({
        description: 'Inspect project delegation allowance and local availability. No model calls.',
        args: {},
        execute: async () => JSON.stringify({ allowance: allowance || null, models: MODELS, unavailable: { 'worker-openai': 'gpt-5.4-mini rejected by ChatGPT/Codex authentication' }, localOnline: await health(), active: [...active.values()], restartToExposeLocal: !initialOnline }),
      }),
      team_allowance: tool({
        description: 'Request project worker approval using the native OpenCode permission prompt. First agree models, priority (workers array order), per-model limits and total concurrency with the user in chat. No external dialog. Selection persists; reconfigure=true replaces it after approval.',
        args: {
          workers: tool.schema.array(tool.schema.enum(Object.keys(MODELS) as [string, ...string[]])).min(1),
          concurrency: tool.schema.number().int().min(1).max(10),
          limits: tool.schema.record(tool.schema.string(), tool.schema.number().int().min(1).max(10)).optional(),
          purpose: tool.schema.string().min(10),
          reconfigure: tool.schema.boolean().optional(),
        },
        execute: async (args, context) => {
          if (context.agent.startsWith('worker-') || context.agent.startsWith('plan-')) throw new Error('Only a primary build agent may request delegation.')
          context.abort.throwIfAborted()
          const workers = [...new Set(args.workers)]
          const concurrency = args.concurrency
          const limits: Record<string,number> = Object.fromEntries(workers.map(x => [x, args.limits?.[x] ?? (x === 'worker-local' ? 1 : concurrency)]))
          if (Object.keys(args.limits || {}).some(x => !workers.includes(x)) || workers.some(x => limits[x] > concurrency)) throw new Error('Worker limits must refer to selected workers and cannot exceed total concurrency.')
          if (!args.reconfigure && allowance && workers.every(x => allowance!.workers.includes(x) && limits[x] <= allowance!.limits[x]) && concurrency <= allowance.concurrency) return JSON.stringify(allowance)
          await context.ask({ permission: 'team_delegation', patterns: [JSON.stringify({ project: identity, priority: workers, models: workers.map(x => MODELS[x]), limits, concurrency, purpose: args.purpose })], always: [], metadata: { purpose: args.purpose, workers, models: workers.map(x => MODELS[x]), limits, concurrency } })
          if (workers.includes('worker-local') && (!await health() || limits['worker-local'] !== 1)) throw new Error('Local worker must be online and sequential; no allowance saved.')
          context.abort.throwIfAborted()
          const next: Allowance = { version: 2, project: identity, workers, models: Object.fromEntries(workers.map(x => [x, MODELS[x]])), limits, concurrency, approvedAt: new Date().toISOString() }
          await mkdir(stateRoot, { recursive: true })
          const temporary = `${stateFile}.${process.pid}.tmp`
          await writeFile(temporary, JSON.stringify(next, null, 2), { mode: 0o600 })
          await rename(temporary, stateFile)
          allowance = next
          return JSON.stringify(next)
        },
      }),
    },
    'tool.execute.before': async (input, output) => {
      if (input.tool !== 'task') return
      const worker = output.args.subagent_type
      if (!(worker in MODELS)) throw new Error('Use a configured worker covered by team_allowance.')
      if (!allowance || !allowance.workers.includes(worker)) throw new Error('Explain the delegation plan, then request team_allowance once for this project.')
      if (worker === 'worker-local' && !await health()) throw new Error('Local model offline; do not retry. Choose an approved API worker.')
      await reconcile()
      if (active.size >= allowance.concurrency) throw new Error('Project concurrency allowance reached; await completion of existing work.')
      if ([...active.values()].filter(x => x.worker === worker).length >= allowance.limits[worker]) throw new Error('Per-model concurrency limit reached; await completion.')
      if (worker === 'worker-local' && [...active.values()].some(x => x.worker === worker)) throw new Error('Local Qwen is already in use; await that task and reuse its session.')
      active.set(input.callID, { worker })
      calls.set(input.callID, input.sessionID)
    },
    'tool.execute.after': async (input, output) => {
      if (input.tool !== 'task') return
      const job = active.get(input.callID)
      const child = output.metadata?.sessionId || output.metadata?.sessionID
      if (job && input.args.background === true && child) job.session = child
      else active.delete(input.callID)
      calls.delete(input.callID)
    },
    event: async ({event}) => {
      const e = event as any
      if (e.type === 'session.idle' || e.type === 'session.error' || (e.type === 'session.status' && e.properties?.status?.type === 'idle')) {
        const id = e.properties?.sessionID || e.properties?.sessionId
        for (const [key, job] of active) if (job.session === id || calls.get(key) === id) { active.delete(key); calls.delete(key) }
      }
    },
  }
}

export default { id: 'nas-team-workflow', server: setup }
