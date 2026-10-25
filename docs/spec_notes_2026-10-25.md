# Notes for the living doc, 2026-10-25

SPEC.md is the export of the living doc and is never edited directly (CLAUDE.md). These are the
places where the code moved past it from 2026-10-25 on, for Ray to port. They follow
docs/spec_notes_2026-10-24.md (the two-audience page).

## Layer 7 — the narration's model as a backend, not a vendor (2026-10-25)

The writer, the checker and the client's layer made their calls to Anthropic's API directly. They now
make them through a backend, so each role can run on a hosted open-weight model at a fraction of the
cost, or on a machine of one's own, and every sentence still passes the same validator and checker.

**The interface (part 1).** One call (`narrate.Backend.structured`, and `astructured` for the
checker's concurrent calls): a structured completion against a pydantic schema, with an effort or
thinking setting where the backend has one, streamed where a long writer call needs it, returning the
parsed object, the message to keep in the conversation, why it stopped and the usage. `ModelDrafter`
(the writer and the client's layer) and `ModelChecker` hold the conversation and the checks and name
no vendor; `AnthropicDrafter` and `AnthropicChecker` are the same on the Anthropic backend, which
makes the very calls it made before (structured output, effort, adaptive thinking, the refusal
fallback, a stream above 16,000 tokens, the payload marked for the prompt cache). Each role is
configured from the environment on its own: JYOTISH_WRITER_BACKEND, JYOTISH_CHECKER_BACKEND,
JYOTISH_CLIENT_BACKEND, each "anthropic" (the default) or "openai:<base url with its path>:<model>" for
any server speaking the OpenAI chat-completions API (the base URL keeps its path, …/v1, which is how
a model id with a colon, Ollama's gpt-oss:20b, is told from a port). The key is JYOTISH_<ROLE>_KEY,
else JYOTISH_OPENAI_KEY; a local server needs none. The OpenAI-compatible backend (`OpenAIBackend`,
over httpx) asks for structured output with response_format json_schema; a server that refuses it is
asked in JSON mode (json_object) with the schema in the system prompt, the reply validated against
the schema by us and asked again once when it does not match; a server that takes neither is a
NarrationError naming the server and the model. The mode a server took is found on its first call and
kept. The engine's efforts go as reasoning_effort (xhigh and max as high, both recorded); a server
that refuses reasoning_effort is asked again without it. OpenRouter is sent its data policy with every
request: providers that collect data excluded (`provider.data_collection: deny`), zero-data-retention
endpoints only (`zdr`), every parameter honoured (`require_parameters`), so the schema is never
dropped silently. The reading records each role's model, effort and backend (provider, host, base URL,
the structured mode it took), under `writer`, `checker` and, at depth full, the new `client`; the
client's layer's usage is no longer folded into the writer's, since it may run elsewhere. The ledger
prices each role by its own model and host (`costs.price`): Anthropic's by model as before, an open
provider's by host and model from `costs.OPEN_PRICES`, each provider's page and the date it was read
in `costs.PRICE_SOURCES` (DeepInfra and OpenRouter, read 2026-10-25), a local server at nothing per
token; a model without a price is counted with its tokens and no cost, and a reading with such a role
has no total. Ledger revision 0003 keeps the client's layer's model, tokens and calls apart and the
three backends; GET /costs/daily and /costs/readings show them. /health reports each role's provider,
host, model and whether it has what it needs to run (never a key), and says "live" only when all
three do. httpx (BSD-3-Clause, already brought by the Anthropic SDK) is now a declared dependency; the
licensing picture of SPEC's Tech stack does not change.
