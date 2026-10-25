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

**Providers (part 2).** docs/models.md documents three ways to run the narration, with the exact
environment lines: hosted open-weight models on DeepInfra or OpenRouter (gpt-oss-120b for the writer
and the client's layer, GLM-4.7 or Qwen3.6-35B-A3B for the checker; OpenRouter with its data policy in
every request and in the account), Ollama on one's own machine (gpt-oss:20b at 16 GB, qwen3.6:27b or
glm-4.7-flash at 32 GB, each given a context window by a Modelfile, since Ollama's OpenAI API cannot set
one), and Anthropic as before. For each: the licences (gpt-oss Apache 2.0, GLM-4.7 MIT, Qwen3.6 Apache
2.0), where the data goes and the provider's stated training and retention policy with its URL and the
date read (2026-10-25), the prices, and the cost per reading at astrologer and full depth from the
second comparison's token counts (astrologer depth 0.08 to 0.26 USD against Opus's 2.61, depending on
provider and checker; Opus's counts, so an estimate until a comparison runs on the model). The
benchmark section says it has not been run on an open checker yet. The message sizes are measured: on
the reference chart the writer's message is 42,224 o200k tokens at astrologer depth and 195,340 at depth
full, so depth full needs a writer whose window holds the whole chart: of the open models named only
Qwen3.6-35B-A3B (262,144) does; gpt-oss-120b (131,072) and GLM-4.7 (202,752) do not. The engine refuses
depth full before any call (`narrate.full_depth_guard`): on a local model unless JYOTISH_ALLOW_LOCAL_FULL
is set, naming the message's characters and estimated tokens (2.87 characters a token, measured); on a
hosted open model whose window is known (`narrate.CONTEXT_TOKENS`) and cannot hold the message and
32,000 tokens to think and write. A model not listed is not refused; its server answers for its window.
docs/deploy.md lists the variables and says the Fly deployment takes them as secrets, the checker staying
on Anthropic until an open one passes the rule.

**Measurement (part 3).** `scripts/checker_bench.py --checker-backend openai:<url>:<model>` runs the live
checker on that backend over every benchmark row the validator passes and writes
`docs/checker_scorecard_<model>.md` beside Opus's `docs/checker_scorecard.md` (never over it): the
validator's table, the checker's precision, recall and F1 per category, every miss with the checker's
reason, the tokens and the cost at jyotish.costs's prices, the structured-output mode the server took,
and a last section applying the rule against the gate in use. The rule, in docs/models.md: the
checker's backend changes for client readings only when its benchmark recall is not worse on any
category than the gate in use; the writer's may change whenever its pass rate and gaps are acceptable,
because every sentence is checked. The verdict says which categories are worse; and since Opus's last
live run (2026-10-22, 119 rows) predates rows the benchmark has since gained (147), a category Opus did
not run is named and the verdict waits for Opus to be run again on it. `scripts/compare_readings.py`
takes a backend in a setting ("openai:<url>:<model>,<effort>,<depth>", split at its last two commas)
and a checker per side (`--checker-a`, `--checker-b`) and the client's layer's (`--client-backend`), so
one command compares the Opus writer with an open one under the same checker; with `--live-checker`, a
replayed recording's drafts are checked live on each side's checker, so the open checker and Opus's are
compared on the same reading. Each role is priced by its own model and host in the report, and the
table names each role's host. `service.make_reading` passes the three backends to narrate.

**Tests, and what is owed (part 4).** `tests/test_openai_backend.py` drives the OpenAI-compatible backend
against a stub server on this machine whose base URL's path sets its behaviour: structured output by
json_schema with usage read into the engine's words (cached prompt tokens as cache reads); the JSON-mode
fallback (json_schema refused, json_object asked with the schema in the system prompt, an invalid reply
asked again once, the mode kept for later calls); a server taking neither, refused with an error naming
it and the model; a server refusing reasoning_effort, asked again without it and recorded; a writer call
above 16,000 tokens streamed and gathered; the checker's concurrent calls; one depth-full reading with the
writer, the checker and the client's layer on three backends, each recorded with its base URL and
structured mode, each role's usage apart, and the ledger's cost (nothing, the stub being local); and
depth full on a local model refused before any request, astrologer depth on it not.
`tests/test_backends.py` holds the spec parsing, the pricing per role and host, /health, the depth-full
guard, docs/models.md's prices against the engine's, the scorecard's name and the rule's verdicts. No
scorecard number moved. Owed under the definition of done: the live measurements (item 7 for the writer,
item 5 for a new checker), which spend tokens and are Ray's: the benchmark on DeepInfra's GLM-4.7 and
Qwen3.6-35B-A3B, Opus's benchmark run again on the 147 rows so the rule can be applied on every category,
the comparison of gpt-oss-120b as writer under the Opus checker, and both on Ollama; and the independent
review of this batch (item 9). Until a checker passes the rule, client readings keep Opus as the gate.

**The OpenAI-compatible backend under load (2026-10-25, later).** The live checker benchmark against
DeepInfra's GLM-4.7 ended in httpx.ReadError every time, while one request to the same endpoint answered.
Reproducing with the stub server found a fault of ours: the backend kept one async client across batches,
and each batch of checker calls runs in an event loop of its own, so a pooled keep-alive connection made
in a closed loop failed the next batch ("Event loop is closed"; a server that closes every connection, as
the first stub did, never shows it). The Part 1 refactor had brought the same fault to the Anthropic
backend, whose checker had made a client per batch before. Now each batch opens its client in its own
loop and closes it at its end (`Backend.aclose`), and the sync client is kept and reused instead of one
per call. A request is sent again on a dropped connection (ReadError, WriteError, ConnectError,
RemoteProtocolError), a timeout, or HTTP 429, 500, 502, 503 or 529, up to five attempts with exponential
backoff from one second and as much again of jitter, capped at a minute, waiting what Retry-After asks;
each retry is logged (`backend.retry`: provider, host, model, attempt, reason, wait; never the key), and a
request that still fails is a NarrationError naming the server. A checker call that fails so fails its
sentence alone, marked unchecked (`(unchecked)`, the reason as its evidence), and the batch carries on;
a reading counts such sentences in `unchecked_sentences` (they failed and are not shown; the page's
"offline replay" notice is now a replay's only). Concurrency is per provider: JYOTISH_CHECKER_CONCURRENCY
overrides; else an OpenAI-compatible backend sends 4 at once to a hosted provider and 1 to a server on
this machine, and Anthropic keeps CONFIG.checker_concurrency (16). A reasoning model (GLM-4.7) writes
reasoning_content before its answer: the answer is parsed from content only (the reasoning is kept in the
call's record), and the checker's max_tokens on an OpenAI-compatible backend is 16,000
(`OPENAI_CHECKER_MAX_TOKENS`), room for the reasoning and the verdict. The benchmark checks in chunks and
appends each row to data/bench_partial/<model>.jsonl as it goes (gitignored); `--resume` carries over the
rows already checked and asks only the rest (unchecked rows are asked again), and unchecked rows are
listed in the scorecard and left out of its scores. The comparison writes each side's reading and
recording as it finishes; `--resume` loads a finished side instead of running it again. Both scripts read
ANTHROPIC_API_KEY and JYOTISH_* from the gitignored .env when the environment lacks them, printing the
names read and never a value (`jyotish.envfile`; the service never reads it). Tests with the stub server:
a dropped connection then an answer, a 429 with Retry-After, a request failing every retry, a sentence
failing every retry in a batch (sequential and concurrent), a reading counting it, a reply with
reasoning_content, the concurrency defaults, a keep-alive server across three batches, and the
benchmark's partial file and resume.

Reproduced live against DeepInfra after the fix (2026-10-25): one trivial call answered by json_schema
in 9.4 s with reasoning_content; two calls one at a time, four at once and sixteen at once, each with
the checker's real body (up to 23,759 bytes), all answered with no retry needed (213 s, 158 s, 253 s:
GLM-4.7 reasons for about 100 s a call at effort high). The fault reproduced was ours (the async client
across event loops); the original ReadError did not recur, and if DeepInfra drops a connection the
retries now carry the call. **The benchmarks** (8 calls at once, every one of the 124 checker rows
answered): GLM-4.7 recall 1.000 on every category (86 of 86), precision 0.896 (10 false rejects of 61
good sentences), 2,467 s, USD 1.15; Qwen3.6-35B-A3B recall 0.965 (83 of 86: it missed one
contradicts_its_fact, one judgement_premise and one unstated_claim row), precision 0.965 (3 false
rejects), 441 s, USD 0.53. Both are not worse than Opus's last live run on every category that run
measured (14); eight categories added since have no Opus run, so the rule is not decided for either
until Opus is run again on the 147 rows. docs/models.md carries the table.
