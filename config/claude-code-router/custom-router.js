// CCR custom router — maps incoming model name to "provider,model".
// Return a string to override the static Router rules; return null/undefined
// to fall through to default/background/think/longContext.
//
// Routing:
//   - claude-*    → poe-anthropic, with dash→dot version normalization
//                   (Claude Code sends `claude-opus-4-7`; Poe expects `claude-opus-4.7`)
//   - gemini-*    → poe-openai, with JSON-Schema scrub for tool params
//                   (Google rejects $schema, additionalProperties, exclusiveMin/Max)
//   - gpt/grok/llama/deepseek/mistral/o[1-9]-* → poe-openai
//
// We never fall through to the static Router; always returning here ensures
// /model selections in Claude Code (sonnet/haiku/opus) are honored instead of
// being clobbered by the `default` rule.

function scrubGeminiSchema(obj) {
  if (Array.isArray(obj)) {
    for (const v of obj) scrubGeminiSchema(v);
    return;
  }
  if (obj && typeof obj === "object") {
    delete obj.$schema;
    delete obj.additionalProperties;
    if (typeof obj.exclusiveMinimum === "number") {
      obj.minimum = obj.exclusiveMinimum + 1;
      delete obj.exclusiveMinimum;
    }
    if (typeof obj.exclusiveMaximum === "number") {
      obj.maximum = obj.exclusiveMaximum - 1;
      delete obj.exclusiveMaximum;
    }
    for (const k of Object.keys(obj)) scrubGeminiSchema(obj[k]);
  }
}

// "claude-opus-4-7" → "claude-opus-4.7"
// "claude-sonnet-4-6" → "claude-sonnet-4.6"
function normalizeClaudeVersion(model) {
  return model.replace(/(\d+)-(\d+)$/, "$1.$2");
}

const POE_OPENAI_PREFIXES = [
  /^gemini-/,
  /^gpt-/,
  /^grok-/,
  /^llama-/,
  /^deepseek-/,
  /^mistral-/,
  /^o[1-9]-/,
];

module.exports = async function router(req /*, config, opts */) {
  const model = req?.body?.model || "";

  // Alias claude-deepseek → DeepSeek V4 Pro via poe-openai
  if (model === "claude-deepseek") {
    return `poe-openai,deepseek-v4-pro-e`;
  }

  if (model.startsWith("claude-")) {
    return `poe-anthropic,${normalizeClaudeVersion(model)}`;
  }

  for (const re of POE_OPENAI_PREFIXES) {
    if (re.test(model)) {
      if (re.source === "^gemini-" && Array.isArray(req.body.tools)) {
        scrubGeminiSchema(req.body.tools);
      }
      return `poe-openai,${model}`;
    }
  }

  return undefined; // unknown model → static Router fallback
};
