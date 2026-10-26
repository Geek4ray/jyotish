# Notes for the living doc, 2026-10-26

SPEC.md is the export of the living doc and is never edited directly (CLAUDE.md). These follow
docs/spec_notes_2026-10-25.md (the model backends, the GLM-4.7 gate).

## Layer 7 — the checker with reasoning off (2026-10-26)

The checker's effort may now be `none` (`narrate.CHECKER_EFFORTS`): reasoning switched off, sent as
reasoning_effort none, which DeepInfra documents for its reasoning models; Anthropic has no such setting and
it is refused there. The service takes the checker's effort from JYOTISH_CHECKER_EFFORT when set
(`narrate.checker_effort`), else CONFIG.checker_effort (high), and the reading records the effort the
checker ran at. `scripts/checker_bench.py --checker-effort none` measured GLM-4.7 with reasoning off on
DeepInfra: every check answered, 313 s against 2,467 s at high (7.9 times faster), 44,016 output tokens
against 603,884, USD 0.17 against 1.15; recall 0.884 (76 of 86) against 1.000, 18 false rejects against 10.
Against the gate in use (GLM-4.7 at high) it is worse on eight categories (negated, house_changed,
dasha_lord_changed, cites_too_narrowly, judgement_premise, unstated_claim, synthesis_does_not_follow,
wrong_dignity) and does not pass the rule: the gate stays GLM-4.7 at high. With effort low already
measured (passes, 9% fewer tokens, no faster), the reasoning GLM-4.7 does at high is what catches these
errors; a faster gate needs another model, held to the same rule.

## Layer 7 — a faster checker model: GLM-5.3-Flash (2026-10-26)

Probed first on the benchmark's 32 hardest reject rows and 10 good sentences, five faster DeepInfra
models: GLM-5.3-Flash 32 of 32 caught, 1 false reject, 54,282 output tokens; DeepSeek-V4.1-Flash 31 of
32 (363 s, the quickest); gpt-oss-120b 31 (4 false rejects); Qwen3.8-Flash 30; GLM-5.3 29. GLM-5.3-Flash
on the full benchmark (`docs/checker_scorecard_zai-org-glm-5.3-flash.md`, effort high, 8 at once, every
check answered, no retry): 995 s against GLM-4.7's 2,467 s, 125,055 output tokens against 603,884, USD
0.10 against 1.15 (its price, USD 0.15 / 0.50 / 0.03 per million, read 2026-10-26 from its model page, is
in costs.OPEN_PRICES); recall 0.977 (84 of 86), precision 0.988 (one false reject against GLM-4.7's ten).
It missed b-arudha (cites_too_narrowly) and kind-judgement-premise (judgement_premise), both caught in the
probe minutes before: worse than the gate on those two categories, it does not pass the rule, and the gate
stays GLM-4.7 at high. The two runs disagreeing on the same rows show that a checker's verdicts vary run
to run (no temperature is sent); the rule compares single runs, which carry that noise on both sides.

## Layer 7 — the instant first page (2026-10-26)

POST /readings now stores the reading before any model call. `narrate.instant_reading` runs narration with no drafter. This gives every engine field: the chart header, the scores and tiers, the windows, the timing line, the technical sheet (`with_sheets`) and the engine's summary. Each area also gets `engine_lines`, the engine's own sentence for each finding offered:

- "The house vote is for career."
- the first three facts of a chain;
- for a draft placement, its planet, its lordship and its house, marked as weighing nothing.

These lines are engine wording, the same kind of text as the timing line, and they are not checked.

The stored reading has `narration_status: "pending"`, `attempts: 0` and no claims or gaps.

- **API:** the job stores the reading with status `running`, progress stage `narration` and `instant` in its log. GET /readings/{id} returns it.
- **Markdown page:** carries the notice "The written analysis is being prepared; …" and marks each area "The written analysis is being prepared.", followed by the engine's lines. It shows no "Narration incomplete" notice and no "No claims were drafted" line.
- **Site:** renders a running job's reading at once (`data-state="pending"`), with the same marks.
- **Review step:** opens a running reading (`_reading_for_review` accepts `running` when a document exists). It shows only what passed, which is nothing yet, and gives each area the same mark.

The finished reading replaces the pending one and records `usage.timeline.instant_s`.

Measured on the reference chart: 0.9 s at astrologer depth and 2.9 s at depth full for the instant reading. The chart and score stages come before it and are cached by birth data.

## Layer 7 — the narration as it is written and checked (2026-10-26)

`jyotish.live` and `CONFIG.live` (on by default) apply on a model backend. A recording's replay (a drafter passed in) keeps the single call per reading it was recorded with.

**The areas in parallel.** Each area is written by a writer call of its own, the areas in parallel (`narrate._narrate_parallel`, which runs `narrate` on one area with `write_summary=False`). The call is told to leave the summary empty (`AREA_ONLY_NOTE`).

**Checks.** Every area's checks run on one pool (`live.SharedChecker`) at the checker's concurrency. The provider's limit is the reading's, not each area's.

**Held units.** Every unit is held once it passes, at every depth: `section_retries`, which was depth full's alone. A retry asks only for the failed units, with their reasons. At curious depth this now covers the paragraph too.

**The client's layer.** At depth full it runs per area, as soon as its area is accepted (`client.write`, `want="areas"`).

**The summary, last.** At depth full it is the client's layer over every area's accepted text (`want="summary"`). At the other depths it is a writer call of its own (`SummaryDraft`) over the reading's payload and the accepted claims. It is validated and checked as the summary always was, and if it never passes, the engine's summary stands.

**Streaming.** `Backend.structured(on_text=)` streams the draft (Anthropic: text deltas; OpenAI-compatible: SSE). `live.JsonStrings` reads the partial JSON, and `Live.draft_stream` maps each string to its unit:

- `claim:<area>:<id>`
- `paragraph:<area>`
- `when:<area>`
- `analysis:<area>:<section>`
- `summary`

Each complete sentence is shown "being verified". A unit whose text closes is validated at once and, when it passes, its checks are started. The attempt's check step finds them in flight, with the same validator and the same check data; nothing decides differently. A verdict marks its sentence "verified", or removes the unit. The loop's own decision then emits `accepted` or `removed`, and the writer's replacement streams the same way.

**Events.** The events are `sentence`, `unit`, `verified`, `removed`, `accepted`, `area` and `done`. The service's `events` callback receives them. The API keeps them per reading in memory (`LiveLog`, numbered from 1) and serves them two ways:

- GET /readings/{id}/events: server-sent events, resumable by Last-Event-ID, ending at `done`.
- GET /readings/{id}/live?since=N: the polling fallback.

A reading in a comparison has no live view (409), since its sentences would show what the blind view withholds.

**The site.** `web/js/live.js` follows the events and falls back to polling (`?live=poll` forces it). A sentence the checker has not passed always carries the mark "being verified". When the reading is done, the page is drawn again from the stored reading, which holds only what passed. The Markdown page and the review page are rendered from the stored document, so they never show an unverified sentence.

**Timeline.** `usage.timeline` records `instant_s`, `first_sentence_s`, `first_verified_s`, `first_area_s` and `done_s`.

**Cost of the split.** Parallel areas send each area its own payload, and the summary call sends the whole one. At astrologer depth on the reference chart, the three area messages are 14,700 to 19,200 tokens each and the summary's about 50,000, against 49,600 for the single call. So the input tokens roughly double, and the time falls to the slowest area's.
