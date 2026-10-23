# Notes for the living doc, 2026-10-23

SPEC.md is the export of the living doc and is never edited directly (CLAUDE.md). These are the
places where the code moved past it on 2026-10-23, after `docs/review_2026-10-23.md`, each with the
commit that did it, for Ray to port. Line numbers are SPEC.md's at rev 101.

## Layer 1 (lines 44, 480) — the cross-check

- `scripts/crosscheck.py` chooses PyJHora's varga method for each chart by PyJHora's own label (the
  lowest-numbered method its docstring calls "Traditional Parasara": 1 everywhere but the hora,
  whose 2 it is), never by agreement with the engine, and a control with the Raman hora must fail
  (0c417af). The gate still passes on 1,000 births. The independent ephemeris remains the jplephem
  track; both programs call Swiss Ephemeris.

## Layer 1b (line 54) — what the sampler stamps

- Every body's and the lagna's nakshatra now carry the three numbers too (`Uncertainty.nakshatras`),
  and a dispositor-chain finding's stability is the smallest share among what its steps state: D1
  signs, the D9 signs and D9 lagna of the navamsa chain, the nakshatras of the nakshatra chain. On
  the reference chart the career-lord chain is 0.78 stable, the D9 lagna's number, not 1.0 (add7b22).

## Layer 2 (lines 123, 125) — the nakshatra layer

- Line 125: the "88th-degree point" is gone. The 64th navamsa (63 navamsas on) and the 22nd drekkana
  (21 drekkanas on) are both 210° on, the eighth sign from the body: the texts' two Khara points.
  `nakpoints.py` computes the 22nd drekkana from the Moon and the lagna (span, sign, place in the
  sign, the lord of its D3 sign); the 88th pada, 290° on, matched nothing (add7b22). The sentence
  "which counted from a first pada is the last pada of the 22nd (Vainashika) nakshatra" should go
  with it: the engine's own table puts Vinasha at the 23rd (line 564 agrees).
- Line 123: "gender" is two things. The yoni koota's sex of the animal (`yoni_sex`: one male and one
  female per animal, the mongoose a male alone) and the modern compilations' nakshatra gender
  (`gender`: eight male, sixteen female, Mrigashira, Mula and Shatabhisha neuter), with no classical
  text located for the second (add7b22).

## Layer 3 (line 201; worked example lines 679, 681) — the placement drafts

- The 24 Rahu and Ketu sign rows name no text: Brihat Jataka 18 and Saravali treat the seven planets
  in the signs. The Moon's rows carry one phase modifier (Paksha bala under 30 of 60), not a second
  "waning" code stacked on it (9ed50af). `jyotish reference` shows 32 placement fires with the sign
  and nakshatra rows, where line 679 counts 21; the Moon's two rows fire at full scale.

## Layer 5 / worked example (lines 659, 683) — `jyotish reference`

- The command prints its Life areas from the true-time chart now, so the first tier table it prints
  is the worked example's (career moderate 0.70, health weak / mixed, top three career, marriage,
  longevity), not the positions-only chart's; line 683's sentence holds again.

## Layer 6 (lines 309–318, 345) — the outcome side

- Test 1: the split assigns by household (a household's charts land on one side; a subject joining
  an assigned household takes its side) and the salt's SHA-256 is registered in
  `docs/pre_registration.json`, which also logs every scoring of the sequestered cohort; a missing
  file or another salt is refused, never redrawn (854e816).
- Test 4: the activation covariate is the engine's own windows, the timing join's pieces over the
  life with the best third by joint active, a third of the person-years for everyone (b5727f3). The
  dasha gate alone covered nine years in ten.
- Test 8 is built: each school's vote sum per area, AUC with DeLong's interval on the development
  set, the winner estimated once on the sequestered cohort (854e816). "Tests 1–8 and 10" is now true.
- Subjects, charts, readings and exclusions carry a birth key (the UTC instant and the place, nothing
  of the engine), by which rows are matched at import and erased, across engine versions and
  accuracy classes; twins keep their shared chart (1d624cf).
- The synthetic planted run counts the unplanted areas (father, gains, reputation) that survive BH:
  all three at 20,000, lift inherited through the shared outcome map, reported and not gated
  (0cdb2a4). The nested-model table marks a DeLong p whose AUC fell.
- The harness gates verdicts only; sampled statistics are reported with their direction (a90f712).

## Layer 6b (line 345, the review step) — judgements

- The review view shows a reviewer their own answers, verdicts and words only; another reviewer's
  appear nowhere on the page, the export is where judgements meet (4022662). Note, whole-reading and
  edit texts are bounded.

## Layer 7 (line 370, item 10) — the validator

- The rule that a claim stands alone is enforced now, narrowly: a claim with "again", "likewise",
  "aforementioned", "as above/noted/said/mentioned/before" or opening "The/This/That same" is refused
  before checking; summaries and paragraphs are exempt (4699460). The two benchmark rows the checker
  could never catch are caught; the validator's recall on the benchmark is 0.243.

## Two differences decided on 2026-10-23

- Line 564 (the Sun in PurvaBhadra "the 12th (Desha)", "27th (Jati)") against the engine's Jati 26 and
  Desha 27: the special taras are now a setting, `Meta.special_taras`. The default, `desha_27`, is the
  common modern list (Jagannatha Hora's among them: Jati 26, Desha 27); the SPEC's reading is kept as
  `desha_12` (Desha 12, Jati 27), so nothing the doc says is lost. Neither is read in a named edition.
  The doc should say the Sun's 12th is a special tara only under the second scheme, or name a text
  for the 12th. (SPECIAL_TARAS predates the review's range: 2228f41.)
- Line 558 ("the Venus–Jupiter loop"): one name everywhere now, the loop read from the planet
  earliest in graha order, in the chart object, the chain findings and the chart page: Jupiter–Venus.
  The `houses` beside it read in the same order (Jupiter in the 1st, Venus in the 11th: [1, 11]).

## Still standing

- Abstention (test 5) now follows the engine's gate when `--stability-samples` runs the sampler
  (200 by default on a real cohort); the synthetic harness keeps the accuracy class as the gate's
  stand-in, and every report says which gate it used.
- The facts shown beside a sentence are stored with the edit (`reviews.facts`) and the export reads
  them, recomputing (and saying so) only for rows from before.

## Layer 7 (Depth, after line 373 at rev 116) — a fourth depth, full

A fourth depth whose aim is the best analysis the engine's facts allow: the depth of a frontier
model reasoning at its highest effort, with every sentence still tied to an exact fact and checked.
Proposed text for the living doc, by part; part 1 is f59467f, the others follow it on main.

**The whole chart to the writer.** At depth full the user message carries, besides the findings,
`chart`: everything the engine computes, serialised compactly under stable paths
(`fullchart.payload`): the planet and nakshatra tables, the lagna, the KP cusps and the Sripati
madhyas, the special points (the 64th navamsa and 22nd drekkana, Abhijit, the nakshatra lagnesha),
the sixteen vargas and D1, dignities and avasthas, the sensitive-degree flags, aspects, lordship
and roles, the three dispositor chains with their loops and final dispositors, karakas (7 and 8)
and arudhas, Ashtakavarga (BAV, SAV, the Trikona and Ekadhipatya reductions, Sodhya Pinda,
Kakshya), Shadbala with every bala, Bhava Bala under both house systems, Vimsopaka, Ishta/Kashta,
Argala, Sudarshana, the panchanga, every rule fire and every placement with its status
(experimental and draft included), every area's family votes with their derivations, terms,
weights and vote stability, the driver, Vimshottari to the pratyantar with the current period,
Yogini and Chara with theirs, each lord's period quality and Nadi activation, the tagged transit
timeline and the named transit windows for the range, the timing join's windows per area for the
same range, and the sampler's stamps. A path is the keys from the root joined by dots, a list item
by its index (`planets.Mars.dignity`, `vimshottari.periods.Rahu-Saturn-Venus`, `yogini.periods.12`).
The range is the reading date and `timing_years` (ten) after it, for every question at this depth.

This departs from item 9 ("never a longitude") at this depth only, and only so far as the chart
table does: a position is its sign and its degree within the sign (d°m′s″), never an absolute
longitude. Also left out, because each would cite nothing the rest does not: the Moon's transit
rows, daily tara rows and vedha spans (thousands over ten years), and the Kakshya spans of the Sun
and Mars (under four days each). Dates are YYYY-MM-DD; stability is [time, ayanamsa, house].

A new tag, `[fact:<path>]`, cites any field. The validator accepts it when the path exists in the
payload (and refuses it at the other depths, where nothing is offered by path); the checker
receives the value of each cited field beside the sentence (`facts`: path -> value), and the
checker's prompt says a proposition a cited fact states is supported and a date, period or figure
no cited fact or finding states is not. At this depth a sentence citing a fact may name dates,
periods and transits (item 11's timing rule applies to sentences citing none). The existing
`[rule:]`, `[text:]`, `[vote:]` and `[chain:]` tags work as before, and the family-name rule of
item 11 holds at this depth. The reading carries `facts_cited` (path -> value for every fact its
shown sentences cite), so the page and the website footnote a fact with its value from the reading
alone. The writer's `max_tokens` at this depth is 128,000 (`CONFIG.full_max_tokens`), sent as a
stream; the payload message is marked for the prompt cache, so a regeneration rereads it at the
cache rate.

Measured on the reference chart (as of 2026-10-21, three areas: career, marriage, longevity; ten
years of transits): the `chart` section is **356,177 characters** of compact JSON (356,402 bytes:
the degree marks are the only non-ASCII), built in 2.0 s; the whole user message, the findings
included, is 456,098 characters, against 137,637 for the same three areas at astrologer depth
(indented). By section, the largest: areas 115,479 (nineteen areas' votes with derivations),
transits 89,876, Vimshottari 49,300 (772 periods), Chara 24,463, Yogini 20,244, rules 11,814; every
other section is under 5,000. No API key was available when it was measured, so tokens are an
estimate, about 130,000 for the whole message at 3.5 characters a token; the live comparison
(part 4) records the exact input tokens from the API's usage. `tests/test_fullchart.py` holds the
measured size and fails when the payload moves by more than a tenth, so this number is kept true.

**Reasoning before writing.** At depth full the writer runs with extended thinking on
(`CONFIG.full_thinking`, adaptive: the only thinking mode the current models take; a thinking
budget is refused) and at the highest effort the API offers (`CONFIG.full_effort`, max; the
efforts are low, medium, high, xhigh, max). `jyotish read --writer-model --writer-effort` and the
`writer_model` and `writer_effort` fields of POST /readings override the writer at any depth, from
the models that take these settings (`narrate.WRITER_MODELS`: Opus 5.5, Fable 5.1, Opus 5, Sonnet
5.5); the checker's model and effort (`checker_model`, `checker_effort`, high) never change with
the writer's, so a comparison between writers is judged by one gate. The reading records both
(`writer`: model, effort, thinking, max_tokens; `checker`: model, effort), the token usage of each
side and the narration's wall time (`usage`); the reproduce command carries the two flags. The
writer's summarised reasoning is kept in the recording only, never in the reading.

The prompt asks, per area, besides the claims, for an `analysis` in three sections. The
assessment weighs the evidence for and against, names the strongest and the weakest support,
resolves each contradiction between families or schools explicitly (which side weighs more and on
which fact, or that the facts leave it open) and ranks what matters most. The timing covers the
running periods, the timing join's windows for the area and the transit windows over the range,
every date and period cited to its fact; the engine sets and states each window's score and
confidence, the writer argues which reasons weigh. The third, what the chart does not say: what the
engine does not compute, the families that abstain or do not apply, what depends on the exact birth
time, what no fact decides. Each section is validated like the summary (the area's tags and any
fact, item 11's family rule, no tier word) and checked sentence by sentence, and is accepted whole,
the latest version in which every sentence passed; a section that never passed is a narration gap
(`analysis.<section>`), the other sections standing.

A synthesis sentence combines several findings and facts and carries every tag it rests on. The
checker's data marks it (`synthesis: true`) whenever it rests on two or more findings or facts, and
the checker's prompt says: list each premise and the conclusion; the synthesis is supported when
each cited fact is true and the conclusion follows from them together; reject the conclusion when
it does not, and always when none of its cited findings or facts supports it. A claim citing a fact
beside its finding is a synthesis too. The reading counts the synthesis sentences it shows. The
tier stays the engine's: the analysis may not use the tier words either, and the engine places the
tier beside it, as now. The page and the website show the three sections under the area's tier,
then "The findings, one by one".

**Knowledge beyond the engine.** At depth full a sentence of the analysis may say what a classical
text holds that no finding or fact holds, ending `[tradition:<text> <chapter>]` (chapter, optionally
`.verse`), from the classical texts of the retrieval corpus only (BPHS, Phaladeepika, Saravali,
Brihat Jataka, Jataka Parijata, Uttara Kalamrita, Jaimini Sutras, Tajaka Neelakanthi). Such a
sentence is never sent to the checker and never counted as checked or as a synthesis. It is taken
out of its section into the area's `traditions` (section, sentence, citation, text, chapter, verse,
`checked: false`) and shown on the page and the website under "From the texts, not computed on this
chart", set apart from the checked text, with the engine's line: "Unverified: the engine has not
checked this against the chart or against the verse, and it weighs nothing in any score." A live
reading appends each to `data/candidate_rules.jsonl` (JYOTISH_CANDIDATE_RULES; gitignored) with the
chart hash (the chart id, as the export's), the area, the sentence and the citation, no birth data,
for the astrologer to triage into a draft rule (docs/triage.md); a replay appends nothing.

The validator holds such a sentence to its limits: in the analysis at depth full only (in a claim or
the summary it is refused); one citation in the form `<text> <chapter>` naming one of the texts
above; no other tag (a fact it rests on goes in a sentence of its own, which is checked); and nothing
the engine computes: no numeral (so "the tenth", not "the 10th"), no degree, no date, no dasha,
period or transit, no strength, score, vote, cusp or sub-lord, and nothing about this chart ("this
chart", "your", "here"). Item 6's forbidden content and the tier words apply to it as to any
sentence. "May" is not read as the month: as a verb it is far commoner in a paraphrase. What the
validator cannot do is know whether the chapter says it; that is what the triage is for, and the
prompt tells the writer to leave out a sentence whose chapter it is not sure of.

**The comparison.** `scripts/compare_readings.py` runs the same birth data and question (the
reference chart and its career question by default) at two (model, effort, depth) settings through
the one pipeline (`service.make_reading`: the validator, then the checker at its own fixed model and
effort), and writes `docs/comparison_<date>.md`: per setting the writer and checker as run, the
attempts, the checked sentences and claims shown, the checker's rejections and the rejected claims
over all attempts, the validator's errors, the narration gaps, the synthesis and tradition
sentences, the tokens of each side (input, cache read, cache write, output), the cost from a price
table in the script (USD per million tokens as cached on 2026-10-06; thinking bills as output) and
the narration's wall time; then the two pages side by side, a row per section. The readings and
their recordings go to `docs/comparison_<date>/`; a recording replays offline (`--replay-a`,
`--replay-b`), which is how the suite runs it. With `--database` both readings are stored and the
script names the blind page.

`/compare/{id_a}/{id_b}` (a reviewer token) shows two readings of one chart and question as A and B
with their settings withheld: the writer, the checker, the usage, the model, the attempts, the
replay source and the header's command and depth are left out of what the page is sent. Which
reading is A is fixed per reviewer and pair by a hash of the two ids and the reviewer, so it is the
same on every visit and for either order of the URL, and across reviewers each reading takes both
roles. One question, "which reading would you give the client, and why", answered once (A or B and
the reviewer's own words): it is logged in `reviews` (action `compare`: both readings, which was
shown as A, the choice, each one's settings, the why) and exported with the judgements (kind
`compare`). Only the answer reveals the settings, and since it does, a second answer is refused.
Opening the page logs the reviewer and excludes the chart from the blind learning set, as the
review step does.

The live comparison on the reference chart needs an API key, which was not available when this was
built. The command (writes `docs/comparison_<date>.md` and stores both readings for the blind page):

    .venv/bin/python scripts/compare_readings.py --a claude-opus-5-5,medium,astrologer \
        --b claude-opus-5-5,max,full --as-of 2026-10-21 --database sqlite:///jyotish.db

Its numbers belong here once it has run: the measured input tokens of the full payload, both
settings' checked, rejected and gap counts, synthesis and tradition sentences, cost and wall time.

Two races the comparison exposed, both older than this work and both fixed with it: two jobs for one
chart at once (the comparison posts two) shared the chart cache's temporary file, so the second
`replace` found it gone; and both inserted the chart row, so the second failed on its key. Each
writer now has a temporary file of its own, and a lost insert leaves the stored row, which has the
same key and so the same document (`tests/test_cache.py`, `tests/test_compare.py`).

## Layer 7 (Depth full, after the first live comparison) — what the engine knows, stated

The first live comparison (docs/comparison_2026-10-23.md; SPEC rev 118 records it) left all nine of
reading B's analysis sections and three of its varga claims as gaps, and most refusals were the
engine's fault: it knew the fact and did not state it where the checker could see it. What changed,
by part, each with its commit; the replay numbers and the re-run command close the heading.

**Label what the engine knows.** Every varga row of a vote's derivation carries
`varga_dignity_label` (exalted, own, friend, neutral, enemy, debilitated; a varga has no degree, so
no moolatrikona) beside the number it adds (`varga_dignity`, DIGNITY_SCORE of the label), and the
review step's fact line says it; the D1 dignities were labels already, and each lord's period
quality and each timing window's dignity term now names the lord and its label beside the number.
A stability is an object everywhere in the payload: `{time, ayanamsa, house, label, ayanamsas:
"holds under 2 of 3 ayanamsas", house_systems: "holds under 1 of 2 house systems"}`. The arudha
derivation names what it rests on (`rests_on`: A10 for career, UL, UL2, A7 for marriage) and why it
came out as it did (`why`: "the benefics and malefics in A10 balance: the vote abstains" on the
reference chart; A10 is Taurus with Jupiter and Saturn). The payload gains `constants` (the sign
order, the sign lords, each planet's exaltation, debilitation, moolatrikona and own signs),
`houses.<lagna|moon|sun>.<n>` (sign, lord, occupants: "Aquarius, the 10th house from the lagna"
cites houses.lagna.10, and so does "Saturn, lord of the 10th"), and `not_computed` (synastry without
a second chart, rectification, calibrated probabilities, learned scores, the special lagnas, the
retrieval corpus, model routing of questions, scored transit taras, draft placement effects, and
what the engine never states). Beyond the five refusal kinds the comparison named, the recording
showed three more fields that were opaque: the tara is now `tara_from_moon`, a transit row's grade
`bav_grade` (from the planet's own bindus) and its good house `good_from_moon`, each Bhava Bala row
has `rank_of_12` (the 10th is 12th of 12 under whole signs on the reference chart), and each area
names its `main_karaka`. The payload measures 402,380 characters on the reference chart (from
356,177), the stability objects most of the growth.
