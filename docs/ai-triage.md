# AI triage

`FailureTriageAgent` owns a fixed, auditable pipeline: sanitize and normalize
evidence, run deterministic diagnostics, add current history/change context,
request a Pydantic-shaped provider result, validate claims, calculate transparent
confidence, and require review when appropriate.

The mock provider is intentionally deterministic. Azure OpenAI and
OpenAI-compatible implementations read credentials from the environment and
use the versioned prompt in `prompts/triage-agent/v1.md`. Malformed output is
repaired to a safe `UNKNOWN` once for the compatible provider; a second failure
raises `TRIAGE_MODEL_OUTPUT_INVALID`. No provider may change test/source state.

