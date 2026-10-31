# The narration's models: three ways to run it

The engine computes every figure itself; a model only writes the sentences, and every sentence passes
the code validator and the semantic checker before a reader sees it (SPEC Layer 7). Three roles make
model calls, and each runs on its own backend (`narrate.make_backend`):

| Role | Variable | What it does |
| --- | --- | --- |
| writer | `JYOTISH_WRITER_BACKEND` | drafts the claims and, at depth full, the analysis |
| checker | `JYOTISH_CHECKER_BACKEND` | checks every sentence against the data it cites: the gate |
| client's layer | `JYOTISH_CLIENT_BACKEND` | at depth full, writes the client's view from the accepted text |

Each is `anthropic` (the default) or `openai:<base url with its path>:<model>`, any server speaking the
OpenAI chat-completions API. The key is `JYOTISH_<ROLE>_KEY` (`JYOTISH_WRITER_KEY`, `JYOTISH_CHECKER_KEY`,
`JYOTISH_CLIENT_KEY`), else `JYOTISH_OPENAI_KEY`; a local server needs none. The base URL keeps its path
(`…/v1`), which is how a model id with a colon is told from a port: `openai:http://localhost:11434/v1:gpt-oss:20b`.
Every reading records each role's provider, host, model, effort and structured-output mode, and the
ledger prices each role by its own model and host (`jyotish.costs`; a model without a price is counted
with no cost, never guessed). `/health` shows each role's backend and whether it is ready (never a key).

Prices, policies and model facts below were read from the providers' own pages on **2026-10-25**; they
change, so read them again before you rely on them. The numbers the engine prices from are in
`src/jyotish/costs.py` (`OPEN_PRICES`, `PRICE_SOURCES`).

## The rule for changing a backend

- **The checker** is the gate. Its backend changes for client readings only when its benchmark recall
  (`scripts/checker_bench.py`, the share of bad sentences it refuses) is not worse **on any category**
  than the gate in use, per the scorecards `docs/checker_scorecard_<model>.md` (each backend) and
  `docs/checker_scorecard.md` (Opus, the earlier gate). A cheaper checker that misses one kind of error
  more often is not a cheaper gate; it is a weaker one.
- **The gate in use**, since 2026-10-31, is **GLM-5.3-Flash at temperature 0 on DeepInfra**
  (`docs/checker_scorecard_zai-org-glm-5.3-flash_temp-0.md`), Ray's decision after it passed the rule against GLM-4.7
  with recall 1.000 on every category (below, and "Timing"). `scripts/checker_bench.py` compares against it by default.
- **The gate before it**, from 2026-10-25, was **GLM-4.7 on DeepInfra** (`docs/checker_scorecard_zai-org-glm-4.7.md`):
  Ray's decision to run the narration without Anthropic. On the benchmark it caught every bad row (86 of
  86) and is not worse than Opus's last run on any of the 14 categories that run measured; the 8 the
  benchmark has gained since have no Opus run to compare with, and GLM-4.7 caught every row of them.
  `--gate docs/checker_scorecard_zai-org-glm-4.7.md` compares against it.
- **The writer** (and the client's layer) may change whenever its pass rate and gaps are acceptable on
  the comparison (`scripts/compare_readings.py`), because every sentence it writes is checked: a weaker
  writer costs attempts and gaps, never an unchecked sentence.

## How big the messages are

Measured on the reference chart on 2026-10-25, in o200k tokens (the tokenizer family of gpt-oss; other
models count somewhat differently): the writer's message at **astrologer depth is 42,224 tokens**
(142,446 characters); at **depth full it is 195,340 tokens** (560,613 characters), the whole chart. A
checker call is a sentence and its data, a few thousand tokens; the client's layer reads only the
accepted text, a few thousand more. So depth full needs a writer whose context window holds about
195,000 tokens and room to think and write: of the open models here only Qwen3.6-35B-A3B (262,144) does.
The engine refuses depth full before any call on a hosted model whose window is known to be too small
(`narrate.CONTEXT_TOKENS`: gpt-oss-120b's 131,072, GLM-4.7's 202,752), and on a local model unless
`JYOTISH_ALLOW_LOCAL_FULL=1` is set.

## (a) Hosted open-weight models: DeepInfra or OpenRouter

gpt-oss-120b for the writer and the client's layer; GLM-4.7 or Qwen3.6-35B-A3B for the checker; at depth
full, Qwen3.6-35B-A3B for the writer too (gpt-oss-120b's window is too small for the whole chart).

**DeepInfra** (base URL `https://api.deepinfra.com/v1/openai`):

```bash
JYOTISH_OPENAI_KEY=<your DeepInfra key>
JYOTISH_WRITER_BACKEND=openai:https://api.deepinfra.com/v1/openai:openai/gpt-oss-120b
JYOTISH_CLIENT_BACKEND=openai:https://api.deepinfra.com/v1/openai:openai/gpt-oss-120b
JYOTISH_CHECKER_BACKEND=openai:https://api.deepinfra.com/v1/openai:zai-org/GLM-4.7
```

For the Qwen checker: `JYOTISH_CHECKER_BACKEND=openai:https://api.deepinfra.com/v1/openai:Qwen/Qwen3.6-35B-A3B`.
For depth full: `JYOTISH_WRITER_BACKEND=openai:https://api.deepinfra.com/v1/openai:Qwen/Qwen3.6-35B-A3B`.

**OpenRouter** (base URL `https://openrouter.ai/api/v1`):

```bash
JYOTISH_OPENAI_KEY=<your OpenRouter key>
JYOTISH_WRITER_BACKEND=openai:https://openrouter.ai/api/v1:openai/gpt-oss-120b
JYOTISH_CLIENT_BACKEND=openai:https://openrouter.ai/api/v1:openai/gpt-oss-120b
JYOTISH_CHECKER_BACKEND=openai:https://openrouter.ai/api/v1:z-ai/glm-4.7
```

(Qwen checker: `openai:https://openrouter.ai/api/v1:qwen/qwen3.6-35b-a3b`.) The engine sends OpenRouter its
data policy with every request: `"provider": {"data_collection": "deny", "zdr": true, "require_parameters": true}`
(only providers that do not collect data, only zero-data-retention endpoints, only endpoints that take
every parameter sent, so the JSON schema is never dropped). Set the same in the account as well, at
<https://openrouter.ai/settings/privacy>: training opt-out for paid and free models, and zero data
retention for all model groups.

| | DeepInfra | OpenRouter |
| --- | --- | --- |
| Licences | gpt-oss-120b and -20b: Apache 2.0 (<https://huggingface.co/openai/gpt-oss-20b>); GLM-4.7: MIT (<https://huggingface.co/zai-org/GLM-4.7>); Qwen3.6-35B-A3B: Apache 2.0 (<https://huggingface.co/Qwen/Qwen3.6-35B-A3B>) | the same models |
| Where the data goes | DeepInfra's servers (US) | OpenRouter, which forwards to a provider it routes to; with the policy above, only providers that neither collect nor retain |
| Training and retention, as stated | "We do not use data you submit to our APIs for training models"; inputs are not written to disk and are deleted from memory once inference is complete; "We do not log the content of your requests" (only metadata: request id, cost, sampling parameters). <https://docs.deepinfra.com/account/data-privacy>, read 2026-10-25 | "OpenRouter does not store your prompts or responses, unless you opt in"; request metadata (tokens, latency) is kept, its retention period not stated. <https://openrouter.ai/docs/guides/privacy/data-collection>, read 2026-10-25 |
| Structured output | json_object and json_schema (<https://docs.deepinfra.com/chat/structured-outputs>) | json_schema, per endpoint; `require_parameters` keeps to endpoints that support it (<https://openrouter.ai/docs/features/structured-outputs>) |
| Prices, $ per million tokens in / out / cached | gpt-oss-120b 0.037 / 0.17 / –; GLM-4.7 0.40 / 1.75 / 0.08; Qwen3.6-35B-A3B 0.10 / 0.95 / 0.10 (Standard tier, each model's page) | list prices: gpt-oss-120b 0.15 / 0.60 / 0.075; GLM-4.7 0.54 / 1.98 / 0.099; Qwen3.6-35B-A3B 0.10 / 0.95 / 0.05 (<https://openrouter.ai/api/v1/models>); a request may be routed to a cheaper endpoint, and the charge OpenRouter reports is kept as `provider_cost_usd` |

Not verified: whether DeepInfra accepts `reasoning_effort` as a parameter for gpt-oss (its model page
says the level is set in the system prompt). The engine sends it and, if a server refuses it, asks
again without it and records that it did (`effort_sent`).

## (a2) Fast providers: Cerebras and Groq, for the writer and the client's layer

Both serve gpt-oss-120b on their own hardware, several times faster than a GPU host, and both speak the
OpenAI API, so each is one more `openai:` spec. Each provider is sent **its own key only**:
`JYOTISH_CEREBRAS_KEY` for `api.cerebras.ai` and `JYOTISH_GROQ_KEY` for `api.groq.com` (`narrate.PROVIDER_KEYS`).
Neither the DeepInfra key (`JYOTISH_OPENAI_KEY`) nor a role key (`JYOTISH_<ROLE>_KEY`) is ever sent to them; the
host is matched by its name, a port or not. A role key applies to any other host. Both are writers here, not checkers: the checker stays on DeepInfra, behind the rule.

```bash
# Cerebras
JYOTISH_CEREBRAS_KEY=<your Cerebras key>
JYOTISH_WRITER_BACKEND=openai:https://api.cerebras.ai/v1:gpt-oss-120b
JYOTISH_CLIENT_BACKEND=openai:https://api.cerebras.ai/v1:gpt-oss-120b
# Groq
JYOTISH_GROQ_KEY=<your Groq key>
JYOTISH_WRITER_BACKEND=openai:https://api.groq.com/openai/v1:openai/gpt-oss-120b
JYOTISH_CLIENT_BACKEND=openai:https://api.groq.com/openai/v1:openai/gpt-oss-120b
```

Read on **2026-10-26** from each provider's own pages; neither dates its pages, so the date is the day they
were read. The engine prices from `OPEN_PRICES` in `src/jyotish/costs.py`.

| | Cerebras | Groq |
| --- | --- | --- |
| Base URL, model id | `https://api.cerebras.ai/v1`, `gpt-oss-120b` (<https://inference-docs.cerebras.ai/resources/openai>); gpt-oss-20b is not offered (<https://inference-docs.cerebras.ai/models/overview>) | `https://api.groq.com/openai/v1`, `openai/gpt-oss-120b` and `openai/gpt-oss-20b` (<https://console.groq.com/docs/openai>, <https://console.groq.com/docs/models>) |
| Price, $ per million in / out / cached | 0.35 / 0.75 / no cached price: the prompt cache is on by default with "no additional fee", so cached tokens are priced at input (<https://inference-docs.cerebras.ai/models/openai-oss>, <https://inference-docs.cerebras.ai/capabilities/prompt-caching>; the pricing page loads its table by script and could not be read) | 0.15 / 0.60 / 0.075 (<https://console.groq.com/docs/model/openai/gpt-oss-120b>) |
| Context, output | 131k context and 40k output on a paid key; 65k and 32k on the free tier (the model page) | 131,072 context, 65,536 output (the models page) |
| Structured output | json_object, json_schema and `strict: true` (constrained decoding) for gpt-oss-120b (<https://inference-docs.cerebras.ai/capabilities/structured-outputs>); `tools` and `response_format` together are refused; the engine sends json_schema without `strict` (the schema as a hint) and validates the reply itself | json_schema, `strict: true` constrained or best effort (<https://console.groq.com/docs/structured-outputs>); **streaming is not supported with structured output**, so the engine sends a json_schema call to Groq whole (`OpenAIBackend.streams_schema`), and the live page shows Groq's draft when it arrives rather than sentence by sentence |
| reasoning_effort | low, medium, high; medium by default; reasoning cannot be switched off (<https://inference-docs.cerebras.ai/capabilities/reasoning>) | low, medium, high for gpt-oss, no `none`; its default not stated (<https://console.groq.com/docs/reasoning>) |
| Temperature | taken | taken; a temperature of 0 is sent as 1e-8 (<https://console.groq.com/docs/openai>) |
| Speed, as claimed | about 3,000 tokens a second (the model page) | about 500 tokens a second for 120b (the models page) |
| Rate limits, as stated | free trial 5 requests a minute and 30k uncached tokens a minute on the rate-limits page, 30 a minute on the model page (the two disagree); pay as you go 1,000 a minute, 1M uncached tokens a minute (<https://inference-docs.cerebras.ai/support/rate-limits>) | 30 requests a minute, 1,000 a day, 8k tokens a minute, 200k a day for gpt-oss on the Developer plan's base limits (<https://console.groq.com/docs/rate-limits>); the free plan's are shown only in an account's settings |
| Training and retention, as stated | "We do not retain inputs and outputs associated with our training, inference and chatbot Services" (privacy policy, section 6, effective 2024-08-27, <https://www.cerebras.ai/privacy-policy>); training on API inputs is not addressed on either page read | "Groq is not permitted to use Inputs or Outputs for training or fine-tuning" unless the customer permits it (Services Agreement 4.2, last modified 2026-06-22, <https://console.groq.com/docs/legal/services-agreement>); "By default, Groq does not retain customer data for inference requests"; reliability and abuse logs up to 30 days, which zero data retention (Data Controls) turns off (<https://console.groq.com/docs/your-data>) |

Not verified: whether Cerebras streams a json_schema completion (its pages do not say; a live run shows
it), whether Cerebras trains on API inputs (not stated), and which Cerebras free-tier limit is current. Cerebras is
not used: it asks for payment before its key serves.

**Groq's free tier refuses every writer call** (measured 2026-10-31 with a free key).

- **The limit.** The account's limit for gpt-oss-120b is 8,000 tokens a minute (header `x-ratelimit-limit-tokens: 8000`).
- **The refusal.** The career area's message, 17,459 tokens, was answered HTTP 413 "Request too large … Limit 8000, Requested 17459 … Upgrade to Dev Tier". At astrologer depth every area's message is 14,700 to 19,200 tokens on the reference chart.
- **What does fit.** A small structured call (313 tokens in) was answered in 1.2 s.
- **What the engine does.** It treats a 413 as fatal (`FATAL_STATUS`): the reading stops at once, in 0.5 s, with the reason, and no attempt is spent.
- **What would change it.** Groq's paid Dev Tier would lift the limit.

**A checker's temperature.** `JYOTISH_<ROLE>_TEMPERATURE` sends `temperature` to an OpenAI-compatible
server (none is sent by default, so the server samples) and the reading records it with the backend;
`scripts/checker_bench.py --checker-temperature 0` runs the benchmark at it and names the scorecard
`…_temp-0.md`.

## (b) Locally, with Ollama

Ollama (<https://ollama.com>) serves an OpenAI-compatible API at `http://localhost:11434/v1` and takes
response_format json_schema (it becomes its native `format`). Nothing leaves the machine and nothing
is charged per token. At 16 GB of memory, gpt-oss:20b (a 14 GB download, Apache 2.0) for every role; at
32 GB, qwen3.6:27b (q4_K_M about 17 GB, Apache 2.0) or glm-4.7-flash (q4_K_M about 19 GB, MIT; it needs
Ollama 0.14.3 or later) for the checker. Ollama's default context is small and its OpenAI API cannot
set it, so give each model a window that holds astrologer depth's 42,224 tokens and room to write, with
a Modelfile:

```bash
ollama pull gpt-oss:20b
```

```bash
printf 'FROM gpt-oss:20b\nPARAMETER num_ctx 65536\n' > Modelfile.gpt-oss && ollama create gpt-oss-20b-64k -f Modelfile.gpt-oss
```

```bash
JYOTISH_WRITER_BACKEND=openai:http://localhost:11434/v1:gpt-oss-20b-64k
JYOTISH_CLIENT_BACKEND=openai:http://localhost:11434/v1:gpt-oss-20b-64k
JYOTISH_CHECKER_BACKEND=openai:http://localhost:11434/v1:gpt-oss-20b-64k
```

At 32 GB, the checker on Qwen: `ollama pull qwen3.6:27b`, a Modelfile with `FROM qwen3.6:27b` and
`PARAMETER num_ctx 32768` created as `qwen3.6-27b-32k`, and
`JYOTISH_CHECKER_BACKEND=openai:http://localhost:11434/v1:qwen3.6-27b-32k`. A longer context needs more
memory than the download size; the sizes above are the downloads (<https://ollama.com/library/gpt-oss/tags>,
<https://ollama.com/library/qwen3.6/tags>, <https://ollama.com/library/glm-4.7-flash/tags>).

Depth full on a local model is refused unless `JYOTISH_ALLOW_LOCAL_FULL=1` is set: its message is about
195,000 tokens, and the model's num_ctx and the machine's memory must hold that and room to write. On
16 or 32 GB they do not.

## In use: DeepInfra for all three roles

Since 2026-10-25 the narration runs on DeepInfra, with no Anthropic call: gpt-oss-120b writes and writes the
client's layer (the lines under (a)); depth full needs the Qwen writer. GLM-4.7 checked until 2026-10-31;
since then GLM-5.3-Flash at temperature 0 checks (`JYOTISH_CHECKER_BACKEND=openai:https://api.deepinfra.com/v1/openai:zai-org/GLM-5.3-Flash`,
`JYOTISH_CHECKER_TEMPERATURE=0`). The
repository's `.env` (gitignored) holds these lines and the key; the scripts read it, docker-compose passes
the variables to the service, and a shell running `jyotish read` or `uvicorn` loads them with
`set -a; . ./.env; set +a`.

**The writer, measured** (2026-10-25, docs/comparison_2026-10-25_open_writers.md): the reference chart at
astrologer depth, the career question, both writers at effort medium, both checked by GLM-4.7; Opus's
reading of the same question (docs/comparison_2026-10-23_r2.md, A) beside them.

| | gpt-oss-120b | Qwen3.6-35B-A3B | Opus 5.5 under Opus (2026-10-23) |
| --- | --- | --- | --- |
| Claims accepted of the 37 findings offered | 37 (100%) | 36; the one gap a checker call that failed all five tries, not the writer | 37 |
| Summary | refused every attempt (a framing clause the checker would not pass; then an untagged sentence and citations without their names): the engine's own | the writer's | the writer's |
| Attempts, validator errors | 3, 7 | 3, 8 | 2, 0 |
| Checker rejections | 2 | 8 | 1 |
| Cost, USD (writer + checker) | 0.42 (0.01 + 0.41) | 0.61 (0.05 + 0.56) | 2.61 (0.63 + 1.98) |
| Wall time | 1,950 s | 3,619 s | 176 s |

gpt-oss-120b writes every claim through the checks for a cent, but not the summary, which the engine
then writes from its fields; the checker is most of the cost and nearly all of the time: GLM-4.7 reasons
for 100 to 200 seconds a check at effort high, so a reading takes half an hour or more. This run sent 16
checks at once (JYOTISH_CHECKER_CONCURRENCY=16) and DeepInfra dropped connections under it: 30 retries,
and three checks failed all five tries (unchecked; one became Qwen's gap). The default was 4 then (8 since
2026-10-26: "Timing" below). A
faster gate was the next measurement.

**GLM-4.7 at checker effort low** (2026-10-25, `docs/checker_scorecard_zai-org-glm-4.7_effort-low.md`): it
passes the rule against the gate in use (GLM-4.7 at high): recall 1.000 on every category (86 of 86), the
same 10 false rejects. But it is barely cheaper and not faster on the benchmark's real checks: 547,803
output tokens against 603,884 (4,418 a check against 4,870, 9% fewer), USD 1.04 against 1.15. Its wall time
(7,359 s over three invocations, against 2,467 s) is not a fair comparison, since DeepInfra's balance ran
out midway and the resumed part met 33 retries under load; but the token count, which does not depend on
load, says the model thinks almost as long at low as at high on these sentences. So the gate stays GLM-4.7
at high.

**GLM-4.7 with reasoning off** (2026-10-26, checker effort `none`, sent as DeepInfra's reasoning_effort none;
`docs/checker_scorecard_zai-org-glm-4.7_effort-none.md`): every one of the 124 checks answered, no retry, in
313 s against 2,467 s (7.9 times faster), 44,016 output tokens against 603,884 (14 times fewer), USD 0.17
against 1.15. But recall falls to 0.884 (76 of 86) and false rejects rise to 18: it is worse than the gate
on eight categories (negated 6 of 9, house_changed 8 of 9, dasha_lord_changed 5 of 6, cites_too_narrowly,
judgement_premise and unstated_claim 1 of 2, synthesis_does_not_follow and wrong_dignity 0 of 1) and does
not pass the rule. Without its reasoning GLM-4.7 lets through a negation, a wrong house or a wrong period
lord, which is the gate's work. The gate stays GLM-4.7 at high; a checker effort is set for the service with
JYOTISH_CHECKER_EFFORT (`none` only on an OpenAI-compatible backend).

**A faster model: GLM-5.3-Flash** (2026-10-26, `docs/checker_scorecard_zai-org-glm-5.3-flash.md`). Five of
DeepInfra's faster models were first probed on the benchmark's 32 hardest reject rows (the semantic
categories reasoning-off GLM-4.7 failed) and 10 good sentences: GLM-5.3-Flash caught 32 of 32 with 1 false
reject and the fewest tokens; DeepSeek-V4.1-Flash 31 (the quickest, 363 s), gpt-oss-120b 31 (4 false
rejects), Qwen3.8-Flash 30, GLM-5.3 29. On the full benchmark, at effort high, GLM-5.3-Flash answered every
check with no retry in 995 s against GLM-4.7's 2,467 s (2.5 times faster), 125,055 output tokens against
603,884, USD 0.10 against 1.15 (USD 0.15 / 0.50 / 0.03 per million, its model page, read 2026-10-26), with
recall 0.977 (84 of 86) and one false reject against GLM-4.7's ten. It missed one cites_too_narrowly row
(b-arudha) and one judgement_premise row (kind-judgement-premise), each category 1 of 2 where the gate
caught both: it does not pass the rule, and the gate stays GLM-4.7. Both rows were caught in the probe run
minutes before: the checker samples (the backend sends no temperature), so a single benchmark run carries
run-to-run noise for every checker, the gate's 86 of 86 included.

## (c) Anthropic, as before

Leave the three variables unset (or set them to `anthropic`) and set `ANTHROPIC_API_KEY`. Claude Opus
5.5 writes and checks; it is the gate the open checkers are measured against. Prices: $4 per million
input tokens, $20 output, $0.20 cache read, $5 cache write (<https://platform.claude.com/docs/en/about-claude/pricing>).
Policy: inputs and outputs of the commercial API are not used for training by default, and are deleted
within 30 days of receipt or generation unless a longer retention is agreed
(<https://privacy.claude.com/en/articles/7996868-is-my-data-used-for-model-training>,
<https://privacy.claude.com/en/articles/7996866-how-long-do-you-store-my-organization-s-data>, read 2026-10-25).

## What a reading costs

From the second comparison's token counts (docs/comparison_2026-10-23_r2.md: astrologer depth, 128,806
writer prompt tokens and 14,265 output, 245,099 and 49,790 for the checker's 80 calls; depth full,
1,021,514 and 100,671 for the writer, 593,597 and 139,124 for the checker's 206 calls), priced at each
provider's rates. These are Opus's counts: an open model tokenises and reasons differently and may
need more or fewer attempts, so read them as an estimate until a comparison on that model is run. The
client's layer is not in them (that comparison predates it); it adds a few thousand tokens per area.

| Writer + checker | Astrologer depth, USD | Depth full, USD |
| --- | --- | --- |
| Claude Opus 5.5 + Opus 5.5 (measured) | 2.61 | 10.74 |
| DeepInfra gpt-oss-120b + GLM-4.7 | 0.19 | 0.54 (writer too small for the whole chart: priced as if it fit) |
| DeepInfra gpt-oss-120b + Qwen3.6-35B-A3B | 0.08 | 0.25 (same) |
| OpenRouter gpt-oss-120b + GLM-4.7 (list prices) | 0.26 | 0.81 (same) |
| OpenRouter gpt-oss-120b + Qwen3.6-35B-A3B (list prices) | 0.10 | 0.41 (same) |
| Ollama, any model | 0 per token | refused unless allowed |

## Measuring a backend

The checker, on the labelled benchmark (`tests/fixtures/checker_bench.jsonl`): every row the validator
passes is checked by the named backend, and the scorecard goes to `docs/checker_scorecard_<model>.md`,
per category, with a last section applying the rule against Opus's last live run (a category Opus's run
did not have is named, and the rule waits for it):

```bash
.venv/bin/python scripts/checker_bench.py --checker-backend openai:https://api.deepinfra.com/v1/openai:zai-org/GLM-4.7
```

The writer, on the reference chart, against Opus under the same checker (each setting's model is an
Anthropic writer or an `openai:` spec; `--checker-a` and `--checker-b` name each side's checker):

```bash
.venv/bin/python scripts/compare_readings.py --a claude-opus-5-5,medium,astrologer --b openai:https://api.deepinfra.com/v1/openai:openai/gpt-oss-120b,medium,astrologer --checker-a anthropic --checker-b anthropic --as-of 2026-10-21 --out docs/comparison_2026-10-25_gpt-oss.md
```

Two checkers on the same reading: one recording replayed on both sides, its drafts checked live by each
side's checker (`--live-checker`):

```bash
.venv/bin/python scripts/compare_readings.py --replay-a docs/comparison_2026-10-23_r2/a.recording.json --replay-b docs/comparison_2026-10-23_r2/a.recording.json --live-checker --checker-a anthropic --checker-b openai:https://api.deepinfra.com/v1/openai:zai-org/GLM-4.7 --as-of 2026-10-21 --out docs/comparison_2026-10-25_checkers.md
```

## What the benchmark says

Run on 2026-10-25 on DeepInfra, 147 rows (124 reaching the checker, every one answered; 8 calls at once):
`docs/checker_scorecard_zai-org-glm-4.7.md` and `docs/checker_scorecard_qwen-qwen3.6-35b-a3b.md`, beside
Opus's `docs/checker_scorecard.md` (its last live run, 2026-10-22, on the 119 rows the benchmark had then;
it could not be run again on the 147: the Anthropic account has no credit, and the narration now runs
without Anthropic).

| | Opus 5.5 (2026-10-22, 119 rows) | GLM-4.7 | Qwen3.6-35B-A3B |
| --- | --- | --- | --- |
| Recall, overall | 0.973 (72 of 74) | 1.000 (86 of 86) | 0.965 (83 of 86) |
| False rejects of 61 good sentences | 0 of 45 | 10 | 3 |
| Semantic categories missed | 2 rows | none | contradicts_its_fact (0 of 1), judgement_premise (1 of 2), unstated_claim (1 of 2) |
| Time, cost | 54 s | 2,467 s, USD 1.15 (603,884 output tokens: it reasons at length) | 441 s, USD 0.53 |

The wording and tag categories (tier_word, forbidden_word, tag_not_offered, refers_to_another_claim and
the rest) are the validator's to catch, before any checker, so they score the same for every checker;
the semantic ones are the checkers'. Against Opus's last run, both are not worse on every category it
measured (14); eight categories the benchmark has gained since (cites_too_narrowly, contradicts_its_fact,
judgement_premise, nth_sign, ranking_not_cited, synthesis_does_not_follow, unstated_claim,
untagged_unsupported) have no Opus run. GLM-4.7 caught every bad row, at the price of ten false rejects
(each costs a regeneration, not a wrong sentence), and was the gate in use until 2026-10-31 (above). Against it,
Qwen3.6-35B-A3B is worse on contradicts_its_fact, judgement_premise and unstated_claim and does not pass
the rule (its scorecard's last section); it is cheaper and faster, and stays a candidate for the writer. Until one
shows recall not worse than Opus's on every category, client readings keep the Opus checker (the rule
above).

**GLM-5.3-Flash at temperature 0** (2026-10-26, `docs/checker_scorecard_zai-org-glm-5.3-flash_temp-0.md`).

- **Why temperature 0.** The run above missed two rows that the probe minutes earlier had caught: the backend sent no temperature, so the checker sampled. With `JYOTISH_CHECKER_TEMPERATURE=0` it is asked for its most likely verdict.
- **Recall: 1.000 (86 of 86).** It is not worse than GLM-4.7 on any category, so **it passes the rule** and may gate client readings.
- **False rejects: 3, against GLM-4.7's 10.** Two vote sentences and the untagged framing row.
- **Cost: USD 0.10, against 1.15.** It wrote 123,126 output tokens against 603,884.
- **Time: 4,176 s for this run, 995 s for the run above.** The token count is the same in both, and three retries are logged, so the difference is DeepInfra's load that day, not the model.

## Timing: the instant page and the live narration

Each row below is one live reading of the reference chart: astrologer depth, the career question, as of
2026-10-26. It goes through the service's pipeline, with the instant page and the live view
(`scripts/live_timing.py`, which appends to `docs/live_timings.jsonl` and writes the reading to
`docs/live_2026-10-26/`). The seconds are measured from the start of the reading (the chart comes from the
cache). There are 37 findings offered across career, marriage and longevity, written as three areas in
parallel, then the summary.

| Stack: writer / checker (DeepInfra, concurrency 8 unless named) | Narration | Instant page | First sentence | First verified | First area done | Done | Cost, USD | Claims of 37, gaps | Summary | Retries | Run |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gpt-oss-120b / GLM-4.7 high | live | 3.0 s | 36 s | 67 s | 1,063 s | 2,549 s | 0.40 | 31, 6 | engine's | 5 | 2026-10-26 |
| gpt-oss-120b / GLM-4.7 high, concurrency 16 | live | 2.9 s | 39 s | 71 s | 607 s | 1,215 s | 0.37 | 33, 4 | writer's | 0 | 2026-10-26 |
| gpt-oss-120b / GLM-4.7 high | live | 0.9 s | 30 s | 81 s | 733 s | 1,256 s | 0.33 | 32, 5 | engine's | 1 (writer) | 2026-10-27, comparison |
| gpt-oss-120b / GLM-5.3-Flash high, temperature 0 | live | 2.9 s | 32 s | 35 s | 74 s | 309 s | 0.04 | 35, 2 | engine's | 0 | 2026-10-27, comparison |
| gpt-oss-120b / GLM-5.3-Flash high, temperature 0 | one call | 2.9 s | 85 s | – | 510 s | 510 s | 0.03 | 33, 4 | engine's | 0 | 2026-10-27, after 0937ff8 |
| gpt-oss-120b / GLM-5.3-Flash high, temperature 0 | live | 0.9 s | 19 s | 23 s | 70 s | 311 s | 0.03 | 35, 2 | engine's | 0 | 2026-10-27, after 0937ff8 |
| gpt-oss-120b / GLM-5.3-Flash high, temperature 0 | live | 0.9 s | 51 s | 53 s | 148 s | 493 s | 0.04 | 36, 1 | engine's | 1 (writer) | 2026-10-31, comparison |
| gpt-oss-120b / GLM-5.3-Flash high, temperature 0, **on Fly** | live | 14.7 s | 55 s | 58 s | 99 s | 409 s | 0.03 | 35, 2 | writer's | – | 2026-10-31, fly-1 |
| gpt-oss-120b / GLM-5.3-Flash high, temperature 0, **on Fly** | live | 3.2 s | 36 s | 38 s | 64 s | 322 s | 0.03 | 37, 0 | writer's | – | 2026-10-31, fly-2 |
| gpt-oss-120b / GLM-5.3-Flash high, temperature 0, **on Fly** | live | 3.3 s | 45 s | 49 s | 78 s | 330 s | 0.02 | 37, 0 | engine's | – | 2026-10-31, fly-3 |

**The deployed service beside the local runs** (2026-10-31). `scripts/live_timing.py --url https://jyotish-ray.fly.dev`
asked the service for three readings in a row (the rows marked `"where": "fly"` in `docs/live_timings.jsonl`). The
service used its own keys and backends: gpt-oss-120b writing, GLM-5.3-Flash at temperature 0 checking, both on
DeepInfra, at engine hash c00c519e. That is the code deployed before the three fixes of 2026-10-31
(docs/spec_notes_2026-10-31.md), which reach Fly only when it is deployed again. The local medians are the three
live runs of the same stack at astrologer depth above (2026-10-27 twice, 2026-10-31 once). The seconds are the
service's own timeline (`usage.timeline`); the Fly row in brackets is what this script saw arrive, network included.

| Median of three, same stack, astrologer depth | Instant page | First sentence | First verified | First area done | Done | Cost, USD | Gaps |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Local (this machine) | 0.9 s | 32 s | 35 s | 74 s | 311 s | 0.036 | 2 |
| Fly, the service's timeline | 3.3 s | 45 s | 49 s | 78 s | 330 s | 0.030 | 0 |
| Fly, as seen by the client | (3.9 s) | (46 s) | (49 s) | (78 s) | (332 s) | | |

- **The instant page.** On Fly it was 14.7 s on the first reading (the machine cold, the chart and its sheets not yet
  cached) and 3.2 to 3.3 s after. Two of the three local runs were second readings of a cached chart, hence 0.9 s.
- **The rest.** Fly is within about 15 seconds of local at every step once the first sentence is out. The
  writer's and the checker's calls go to DeepInfra from either place, so they set the time.
- **One run each on a shared provider.** Gaps of 0 against 2 are within run-to-run noise.

Not timed: Cerebras (it asks for payment before its key serves) and Groq (its free tier answered 413 to a writer
call, 17,459 tokens against its 8,000 a minute, on 2026-10-31). In the one-call row there is no "first verified": the single call checks after the whole draft,
with no live view of the checks, and its "first sentence" is the first sentence the validator passed. An instant
page of 0.9 s is a second reading of the same chart, whose technical sheets were cached.

What the rows say (one live run each, so differences of a gap or two are within run-to-run noise):

- **The instant page is about 3 seconds:** every engine field, the technical sheet and the engine's lines.
- **The live narration shows a sentence in 20 to 40 seconds,** against 85 for the single call.
- **The checker sets the rest.** Under GLM-4.7, which thinks for minutes over some sentences, the first area takes 10 to 18 minutes and the reading 20 to 40. Under GLM-5.3-Flash at temperature 0, which passes the rule, the first sentence is verified in about 25 to 35 seconds, the first area in about 70, and the reading in about five minutes for USD 0.03 to 0.04.
- **Split or single call.** Under one checker, the live split was done in 311 s against 510 s for the single call, with 35 claims and 2 gaps against 33 and 4.
- **The gaps.** Before 0937ff8 the split's gaps were mostly the validator's: a lordship stated as "rules the 2nd" was refused on every attempt. The rest are a vote naming a family it does not cite, or a sentence the checker refuses.
- **Concurrency.** DeepInfra took 16 checks at once with no retry on 2026-10-26, but drew 30 retries at 16 the day before. 8 met 5 retries once, all answered, and none since.
- **The hosted default is now 8** (`OpenAIBackend.concurrency`). Set `JYOTISH_CHECKER_CONCURRENCY=16` where a run shows the provider takes it.
- **Cost.** Each area's message is 14,700 to 19,200 tokens at astrologer depth. The summary's call now carries only the accepted claims, so the split's writer input is about 1.1 times the single call's on the first attempt. At depth full it is about 2.6 times (spec note, 2026-10-26).

**The fastest writer under the two checkers** (2026-10-27, `docs/comparison_2026-10-27_checkers.md`).

**Which writer.** Cerebras and Groq were not timed:

- Cerebras asks for payment before its key serves, and that money was not spent.
- Groq's free tier answers HTTP 413 to every writer call: 8,000 tokens a minute against an area's 14,700 to 19,200 (measured 2026-10-31).

So the fastest writer available is gpt-oss-120b on DeepInfra, run in the live narration at effort medium, checker concurrency 8.

| | GLM-5.3-Flash, temperature 0 (the gate in use since 2026-10-31) | GLM-4.7 (the gate until then) |
| --- | --- | --- |
| Instant page / first sentence / first verified / first area / done | 2.9 / 31.7 / 35.2 / 74.3 / 308.7 s | 0.9 / 29.7 / 81.3 / 733.1 / 1,255.7 s |
| Claims of 37, gaps | 35, 2 | 32, 5 |
| Summary | the engine's | the engine's |
| Checker calls, output tokens | 43, 31,644 | 41, 168,162 |
| Cost, USD (writer + checker) | 0.04 (0.01 + 0.03) | 0.33 (0.01 + 0.32) |

- **Speed and cost.** Under GLM-5.3-Flash at temperature 0, the reading is done in about five minutes against twenty, for a ninth of the cost.
- **The rule.** It passes the rule against the gate on the full benchmark.
- **The gaps.** Four of the gaps in these runs were the validator's, not the writer's: a lordship stated as "rules the 2nd". The validator takes that wording since 0937ff8.
- **The other instant page.** The instant page's 0.9 s on the GLM-4.7 side is the second reading of the same chart: its technical sheets were cached.

## On the Fly deployment

The same variables are Fly secrets (docs/deploy.md): `fly secrets set JYOTISH_OPENAI_KEY=<key>
JYOTISH_WRITER_BACKEND=openai:… JYOTISH_CHECKER_BACKEND=openai:… JYOTISH_CLIENT_BACKEND=openai:… -a "$APP"`.
A local model is not reachable from Fly; use a hosted provider there.

**The fastest stack that passed** (2026-10-27): gpt-oss-120b on DeepInfra writes and writes the client's layer; GLM-5.3-Flash at
temperature 0 checks, and passes the rule against GLM-4.7. On the reference chart the reading was done in 309 s for USD 0.04,
against 1,256 s and USD 0.33 under GLM-4.7. Its Fly secrets:

```bash
fly secrets set -a "$APP" JYOTISH_OPENAI_KEY=<your DeepInfra key> \
  JYOTISH_WRITER_BACKEND=openai:https://api.deepinfra.com/v1/openai:openai/gpt-oss-120b \
  JYOTISH_CLIENT_BACKEND=openai:https://api.deepinfra.com/v1/openai:openai/gpt-oss-120b \
  JYOTISH_CHECKER_BACKEND=openai:https://api.deepinfra.com/v1/openai:zai-org/GLM-5.3-Flash \
  JYOTISH_CHECKER_TEMPERATURE=0
```

Depth full needs a writer with a larger window than gpt-oss-120b's (Qwen3.6-35B-A3B, under (a)).
