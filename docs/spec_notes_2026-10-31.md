# Notes for the living doc, 2026-10-31

SPEC.md is the export of the living doc and is never edited directly (CLAUDE.md). These follow
docs/spec_notes_2026-10-26.md (the instant page, the live narration, the gate in use).

The first live reading on the deployed open stack (gpt-oss-120b writing at medium, GLM-5.3-Flash at
temperature 0 checking, depth curious, the reference chart, "How will my career go, and when is the best
time for a job change?") finished with no client paragraph for career or marriage, and the summary was the
engine's own. Four changes follow from it.

## Layer 7 — a lordship named in a list (2026-10-31)

The career paragraph was refused on all three attempts with "[rule:place.l5_h10] on a sentence that names
none of ['5th lord', 'lord of the 5th', 'ruler of the 5th']". The sentence said "it is the lord of the 2nd
and 5th houses". The validator matched each name as a substring, so a lordship named in a list did not
count.

`narrate._names_lordship` now also accepts a lordship named in a list joined by "and", "or" or commas:

- "lord(s) of the 2nd and 5th (houses)";
- "lord of the 2nd, 5th and 9th";
- "rules/ruling the 7th and 12th";
- "2nd and 5th house lord".

The house must be one of the list's ordinals. "Saturn rules the 10th and Mercury the 5th" lists the 10th
alone and is still refused.

The benchmark has the sentence as row `live-lord-of-the-2nd-and-5th`, a paragraph row labelled accept.
The reading's own text was not available locally, so the quoted clause is the reading's and the sentence
around it is rebuilt. That makes 149 rows. With the old check this row is the validator's one false reject;
with the new check there are none (`checker.validator.false_rejects` 0 in docs/scorecard.md). Tests:
`tests/test_narrate.py::test_a_lordship_is_named_in_a_list`, and
`tests/test_checker_bench.py::test_a_lordship_in_a_list_is_a_row_the_validator_passes`.

## Layer 7 — a paragraph held sentence by sentence (2026-10-31)

The marriage paragraph was refused on all three attempts because one sentence tagged
[rule:place.l12_h7] without naming Mars as the 12th lord. The whole paragraph was one unit, so each retry
rewrote it and the whole of it was lost each time.

A paragraph's sentences are now units, the way depth full's sections are (`live.HeldParagraph`). This
applies wherever units are held: the writer's paragraph at curious depth in the live narration, and the
client's layer's paragraph at depth full. With `JYOTISH_LIVE=0`, curious depth keeps the single call's
whole-draft retries.

- **Held.** A sentence that passes the validator and the checker is held.
- **Keys.** The first draft's sentences take the keys 1, 2, …. A retry's j-th sentence takes the j-th
  failed sentence's key, and any extra sentences follow the last one as "<key>.1", "<key>.2", …. A sentence
  the retry sends again verbatim beside the held ones is not placed twice.
- **The retry.** `retry_instruction` lists the held sentences as "the <area> paragraph's other sentences (k
  of n)". It asks for each failed sentence, quoted, with its position ("the marriage paragraph, sentence 2 of
  3 (…)") and its reasons, and adds `PARAGRAPH_RETRY_NOTE`: return only the rewritten sentences, in order.
- **The phrase to use.** A refusal for a rule tag on a sentence that does not name it now states the phrase
  to use (`narrate.name_hint`), for example "(name Mars as the 12th lord or the lord of the 12th)". The
  planet comes from the finding's placement.
- **After the last attempt.** The held sentences stand as the paragraph, in key order. If any sentence
  never passed, the paragraph keeps one gap, counted as a paragraph's gap always was. The page and the site
  show the held sentences and count the gap.
- **The live view.** Each sentence is the unit "paragraph:<area>:<key>". A refusal removes that sentence
  alone, and the site (`web/js/live.js`) shows the sentences inside one paragraph in key order, so a
  replacement lands where the refused sentence was.

Tests:

- `tests/test_live.py::test_curious_paragraph_is_held_sentence_by_sentence_and_the_retry_names_the_lordship`
  (the Fly case: sentences 1 and 3 held, the retry asks for sentence 2 with "name Mars as the 12th lord or the
  lord of the 12th", and the replacement takes its place);
- four tests in `tests/test_client_layer.py` (a retry rewrites only the failed sentence; a sentence that never
  passes leaves the others and one gap; held sentences sent again are not placed twice; extra sentences
  follow the failed one);
- `tests/test_web.py::test_the_site_replaces_one_paragraph_sentence_in_its_place`.

**The replay** (`scripts/replay_accepted.py docs/comparison_2026-10-23_r2`, written to
docs/replay_2026-10-31.md): 0 differences in accepted text on either side, and the gaps are the same as a
replay at 1ec91cd, the commit before this change. The policy cannot show there:

- A is at astrologer depth, which has no paragraph.
- B is at depth full but was recorded before the client's layer, so it has no client drafts to replay.
  Every paragraph and every When is a gap on replay, now as before. The three When gaps that docs/replay_2026-10-24.md
  did not list are there at 1ec91cd too, so they predate this change.

No recording in the repository holds a paragraph: those of 2026-10-23 to 2026-10-27 and docs/live_2026-10-26
are at astrologer depth or full. The policy is measured live in the comparison at curious depth below.

## Layer 7 — the client's fallback summary in the client's words (2026-10-31)

When no drafted summary passes, the summary is the engine's. Its text spoke the engine's language:

> Career: tier moderate (time-stability 1.00, stable). … Best window for career by the engine's timing
> score: 2029-10-23 to 2032-06-23 (Vimshottari Jupiter–Venus, score 0.84) …

The client's page now shows it in the client's words. `ReadingSummary.client_text` comes from
`narrate.client_summary` whenever the summary's source is the engine, the instant page included; it is set
in both narration paths, and `upgrade_reading` fills it for an older reading. On the reference chart:

> For career, the chart's indication is moderate. The areas this chart emphasises most are career, marriage
> and longevity. The strongest period for career runs from October 2029 to June 2032; the period to avoid runs
> from November 2028 to August 2029. These are periods the engine scores as favourable for career; it does
> not predict when you will act.

It says:

- **Each asked area's tier.** A tier that is not a degree is said plainly (`TIER_PLAIN`, for example "that it
  cannot be judged from this chart").
- **How far the tier depends on the birth time.** A sensitive or unstable area gets one sentence
  (`STABILITY_PLAIN`); a stable one gets none.
- **The top areas.**
- **Each timed area's windows.** The best window and the window to avoid are given as months.
- **The timing note**, unchanged.

It has no tier label, score, period lord, stability figure or driver. `text`, with every figure, stays in the
JSON. The page and the site show it under the summary's "For the astrologer" toggle as "The engine's summary,
with its figures" (`page.ENGINE_FIGURES`, strings.js `summary.engine_figures`), together with the summary's
chips (driver, current period, top areas, birth-time window, fired rules, abstained areas). A model-written
summary keeps its face as before (its text, the When (engine) line, the timing note); only its chips moved
under the toggle.

**Each area's figures.** The classical score, the probability, the families agreeing and the polarity move
under "For the astrologer" at every depth, on the page and on the site (`dl.figures`). The tier line (the tier
and its stability) stays on the client's face.

Tests: `tests/test_client_summary.py`:

- `client.CLIENT_WORDS` and `client_errors` find nothing in the client's words, and neither "tier",
  "time-stability", "score <n>" nor "Vimshottari" appears;
- the windows read as months and the note is kept;
- the plain tier and stability sentences;
- the upgrade of an older reading;
- the page's face and its toggle.

`tests/test_web.py` covers the same on the site.

## Layer 7 — measured: the deployed service, and the writer after these changes (2026-10-31)

**The deployed service.** `scripts/live_timing.py --url <base>` times a reading asked of a deployed service.
It sends POST /readings, polls GET /readings/{id}/live, and reads the finished reading from GET
/readings/{id}. No key is read: the service uses its own.

The row it writes has:

- the service's timeline;
- `client_timeline`, the seconds the script saw each first event arrive;
- `where` ("fly" for a fly.dev host).

Three readings ran against https://jyotish-ray.fly.dev at astrologer depth. They used the code deployed before
these changes (engine hash c00c519e): gpt-oss-120b writing, GLM-5.3-Flash at temperature 0 checking. The rows
are `fly-1` to `fly-3` in docs/live_timings.jsonl.

| Median of three, astrologer depth | Instant page | First sentence | First verified | First area | Done | USD | Gaps |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Local | 0.9 s | 32 s | 35 s | 74 s | 311 s | 0.036 | 2 |
| Fly | 3.3 s | 45 s | 49 s | 78 s | 330 s | 0.030 | 0 |

The first Fly reading's instant page took 14.7 s (a cold machine); the next two took 3.2 and 3.3 s. The table is
in docs/models.md ("Timing"), and the scorecard reports the medians (`live.fly_median.*`, not gated).

**The writer re-measured** (definition of done, condition 7: the writer's prompt changed, with the paragraph's
retry instruction and the field descriptions). `scripts/compare_readings.py` ran on the reference chart with
the .env settings: gpt-oss-120b at medium writing and GLM-5.3-Flash at temperature 0 checking, both on
DeepInfra, in the live narration, as of 2026-10-31. A was at curious depth (the Fly reading's setting) and B at
astrologer depth. The report is `docs/comparison_2026-10-31.md`.

| | A, curious | B, astrologer |
| --- | --- | --- |
| Claims shown, of 37 offered (pass rate) | 37 (100%) | 36 (97%) |
| Paragraphs shown, of 3 | 3 | – |
| Narration gaps | 0 | 1 |
| Summary written by | the writer | the engine |
| Checker rejections, validator errors (all attempts) | 9, 7 | 12, 9 |
| Cost, USD | 0.05 | 0.04 |
| Seconds: instant page / first sentence / first verified / first area / done | 3.4 / 83 / 84 / 173 / 440 | 0.9 / 51 / 53 / 148 / 493 |

The paragraph policy ran in A:

- **Marriage.** In the first draft the validator refused sentences 1 to 3 of four and held sentence 4. One
  refusal was the Fly reading's fault, [rule:place.l12_h7] with Mars not named as the 12th lord; the other
  two were tier words. The retry rewrote those three: 2 and 3 passed. Sentence 1, now "Mars, the lord of the
  7th and also the lord of the 12th", passed the validator, but the checker refused it. The third attempt
  wrote "Mars, the lord of the 12th and the 7th", a list the validator now takes, and it passed.
- **Career.** The checker refused sentences 2 and 3 of four. Sentences 1 and 4 were held, and the retry
  replaced only 2 and 3.
- **Longevity.** All four sentences passed at once.

The career paragraph keeps "the lord of the 2nd and 5th houses", the wording the validator refused on Fly.

B's one gap is the marriage lord's chain claim, refused by the checker on its last attempt ("the 7th house is
the area's first house"; the data's area_houses is empty for a chain). Under the same stack on 2026-10-27, B's
setting gave 35 claims and 2 gaps in 311 s (docs/comparison_2026-10-27_split_r2.md). Each figure is one run
on a shared provider; the 2026-10-31 run met 1 and 2 writer retries.

**Not done here.** The curious paragraphs that passed still use engine words: "Bhava Bala", "tests",
"arudha", "KP". At curious depth the writer's paragraph is held to the validator and the checker, not to
`client.CLIENT_WORDS`, which binds only the client's layer at depth full. The client sees those words at
curious depth.

## Layer 7 — the curious paragraph in the client's words (2026-10-31)

At curious depth the paragraph is the client's: the claims behind it are under "For the astrologer". The
paragraphs that passed in the comparison above still used engine words: "Bhava Bala", "tests" and "votes",
"arudha", "KP". The validator now holds each curious paragraph sentence to `client.client_errors`, as the
client's layer's paragraph at depth full is held:

- none of the engine's words (`client.CLIENT_WORDS`);
- a Sanskrit word with a plain phrase refused for it (`client.CLIENT_PLAIN`: the rising sign, not lagna;
  significator, not karaka; and the rest);
- a Sanskrit term without one (`client.SANSKRIT_TERMS`) glossed in the same sentence, right after it;
- no "I", and a weighing marked "in the reading's view".

The claims, the astrologer's, are not held to it. `CURIOUS_PROMPT` says the same: it replaces "glossed once,
the first time" with a gloss in every sentence that names the term, and says not to weigh or rank the
evidence.

**The benchmark** (149 rows). Its paragraph rows are now validated with `client_errors` as the pipeline
does. Three paragraph sentences the reading had accepted break the new rule: unglossed "Ruchaka yoga" and
"Budhaditya yoga" (accept-18, accept-19) and "the Jaimini one, the school that …" (accept-44). They are now
wording rejects in the new category `client_words`, part of `WORDING`, each with its reason in `origin`. With
that, the validator has 0 false rejects and catches 23 of 23 wording rows (docs/scorecard.md).

**The recording.** `tests/fixtures/narration_curious.json`, the one curious recording, had 12 of its 21
paragraph sentences refused under the rule. Seven phrases in it were rewritten in the client's words, each
replaced verbatim wherever it appears in the file, with the tags and the meaning unchanged. The fixture's
`note` lists them, and says that the checker's recorded verdicts were given to the wording before the edit.

Tests:

- `tests/test_narrate.py::test_the_curious_paragraph_is_held_to_the_clients_words` (Bhava Bala, votes,
  lagna, karaka, an unglossed yoga and "I" refused);
- `test_a_glossed_term_and_plain_phrases_pass_the_curious_paragraph`;
- the live and site tests' paragraphs, now written in the client's words.
