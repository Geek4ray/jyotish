# Review of depth full on main, f59467f..6f49627 (2026-10-23)

Condition 9 of docs/definition_of_done.md: a session that did not build the work reviews it against
the spec at the highest effort, writes findings and fixes nothing. Scope: the nine commits from
f59467f through 6f49627 (`git log --oneline daa61c3..6f49627`), without Ray's SPEC and docs commits
(b890532, 1a42d1d, a5e91c0, ec95c9d), which are read as the spec and the evidence.

Method. Read CLAUDE.md, SPEC.md Layer 7 (Depth full, rev 118), docs/definition_of_done.md, both
depth-full headings of docs/spec_notes_2026-10-23.md, docs/comparison_2026-10-23.md and reading B's
gaps and recording. Read every commit's diff and message. Then probed the code offline on the
reference chart (mean node, as of 2026-10-21, the three areas of B): `narrate` with a replayed writer
and a recording stub checker, `validate`/`validate_summary`, `fullchart.payload` and `resolve`,
`scripts/section_retries.py`, `scripts/checker_bench.py`'s rows and validator, and the API's compare
endpoints. The probe scripts are not committed; each finding states how to reproduce what it
claims. Nothing here was run against the Anthropic API, so where a finding concerns what the live
checker does, it rests on the checker's prompt and on which rows reach it, not on a live verdict.
`pytest -q` on this checkout: 1,095 passed, 4 skipped. No code, test or other document was changed.

Part 1 ranks the findings, most serious first. Part 2 answers the six questions the review was asked
to look at hardest. Part 3 goes commit by commit against condition 10. Part 4 lists what was checked
and found sound, so a reader knows what was looked at.

## Part 1 — Findings, most serious first

**F1. A judgement sentence can carry an unchecked factual claim, and an unchecked dated outcome, to
the page.**
`src/jyotish/narrate.py:433` marks a sentence a judgement by its form alone ("I read … as …", "I give
… weight", "I weigh", "I resolve"), anywhere in the sentence. `src/jyotish/narrate.py:1121-1126` then
tells the checker to "list only the premises it takes from its cited findings and facts" and "do not
list the weighing itself (… how it reads a fact, which way it resolves a contradiction)". Two holes
follow, both by the prompt's own wording:
- *How it reads a fact is a fact.* "I read Saturn's place in Taurus as its exaltation, so career rises
  sharply after forty [fact:planets.Saturn.sign]." passes the validator (probe: no error; the
  reading lists it under `judgements`). The only premise taken from the cited field is "Saturn is in
  Taurus", which is true; "its exaltation" (false: `constants.exaltation.Saturn` is Libra) is
  exactly "how it reads a fact", which the checker is told not to list; and "career rises sharply
  after forty" is "which way it resolves", also not listed. The page shows the sentence under "the
  reading's weighing", but the reader still sees a false dignity and a forecast.
- *A clause cited by nothing is not a premise "taken from its cited findings".* "I give the lord
  family more weight, since Saturn is exalted in the 10th [fact:areas.career.contributions]" puts an
  uncited, false clause in a sentence whose instruction says to list only premises from the cited
  fact. The writer's prompt says "a judgement carries no fact its citations do not state"
  (`narrate.py:1008`), but that is a request to the writer; neither the validator
  (`narrate.py:496-502` checks only that a tag exists, and that a digit comes with a fact) nor the
  checker enforces it.
A date passes too once any fact is cited: "I resolve the contradiction toward a job change in 2031
[fact:vimshottari.periods.Jupiter-Venus]" meets the validator's only figure rule (a digit with a
fact tag) and the `timing` filter is skipped for every sentence citing a fact (`narrate.py:555-556`);
the date is the resolution, so it is not listed. SPEC item 11 keeps timing the engine's, and the
depth-full text says "a judgement … states no date, period, figure or tier word except by citing the
fact" — citing *a* fact, here not one that states 2031. What it breaks: SPEC Layer 7 item 10 (every
proposition of a shown sentence checked), the depth-full paragraph on judgements ("its premises
checked … the weighing shown as such": a factual reading is not a weighing), DoD 5. The test that
covers the kind (`tests/test_full_depth.py:398-419`) uses a stub that never sees an unlisted clause,
so nothing in the suite can catch this.

**F2. An untagged sentence in an analysis section is never sent to the checker; it reaches the page
when it has none of the validator's listed verbs.**
`_summary_checks` (`narrate.py:1512-1531`) skips every sentence without a tag (`narrate.py:1520`), and
the analysis sections are checked through it (`narrate.py:1750-1753`). The validator refuses an
untagged sentence only when it matches `CLAIM_VERBS` (`narrate.py:337-341, 493-494`), a fixed list.
Probe: an assessment with three added sentences — "Saturn exalted in Libra, Venus debilitated in
Virgo." "Marriage comes late and career peaks after forty." "Saturn owns the tenth and governs the
career outright." — passed the validator, none was sent to the checker, and all three stand in
`areas[0].analysis.assessment` of the reading (Saturn is in Taurus and Venus exalted in Pisces on this
chart; "after forty" escapes the timing filter, which knows "years" but not ages). The same hole is
older in the summary and the curious paragraph, but depth full asks for three long prose sections per
area, which multiplies its surface, and SPEC rev 118 says each section is "checked sentence by
sentence". Reading B happened to tag every sentence (no untagged sentence in A's or B's shown text or
in B's drafts), so this is latent, not observed. What it breaks: SPEC Layer 7 depth full ("each
section … checked sentence by sentence"), DoD 5 ("every sentence is gated"). The benchmark has no
row of this shape.

**F3. The payload's `rules` section cannot be cited: every one of its 38 keys contains a dot.**
`fullchart._rules` (`src/jyotish/fullchart.py:317-326`) keys each fire `id@basis`, and rule ids are
dotted (`place.l7_h7@lagna`, `yoga.ruchaka@lagna`); `resolve` splits the path on every dot
(`fullchart.py:478-490`). So `[fact:rules.place.l7_h7@lagna]`, `[fact:rules.yoga.ruchaka@lagna.status]`
and every other path under `rules` are refused as "no field at path" (probe: all 38 keys unresolvable;
every other key in the payload resolves). SPEC rev 117 lists "every rule fire and placement with its
status" among what the writer may cite, the prompt says "Cite any field as [fact:<path>]"
(`narrate.py:964-966`), and f59467f's message says both. The writer either loses an attempt to the
refusal or cites the whole `rules` object (11,814 characters, the checker then hunting through it).
B never tried, so it cost nothing yet. `tests/test_fullchart.py` resolves a dozen chosen paths and
never walks the payload, which is how it got through. What it breaks: SPEC Layer 7 depth full ("cites
any field"), condition 10 for f59467f.

**F4. "The strongest support" and "the weakest point" now cite a ranking that the area score does
not contain, and on the reference chart's asked area it names a different weakest family than the
score does.**
`fullchart.contributions` (`fullchart.py:358-387`) ranks each family by its term in S *times its
confluence weight* (1 − rho), and its `basis` string and the prompt (`narrate.py:983`: "ranks them by
what each adds") present that as what each family adds. But S is the plain sum of the terms
(`src/jyotish/scoring.py:486-487`); the confluence weights enter only the tier's agreement weight
(`families_agree_w`), never S. The product is therefore neither a family's share of S nor of the tier.
On career, by the terms in S the weakest is panchanga (0.288 against varga's 0.321); after the weight
it is varga (0.27 against 0.282), so the field the writer is forced to cite for "the weakest point"
(`narrate.py:516-519` refuses the phrase otherwise) states a family S does not rank last. (Probe over
all eighteen scored areas: career is the only one where the two orders disagree at either end.) A
second, structural point the payload hides: the terms are on different scales (the lord term sums
fifteen rows at `WEIGHTS["lord"]` 3.0 plus the dispositor term), so "lord" is the strongest in 15 of
18 areas on this chart and will be on most charts; "the strongest support is the lords" is then a
property of S's construction, not of the chart, and the reading presents it as a finding. What it
breaks: the depth-full rule that the payload "states what the engine knows" (a ranking the engine
does not use is stated as the engine's), and the posture in CLAUDE.md that the engine never claims
more than it computes. The commit (9cc2d41) and the spec notes describe the product accurately as
term × weight, so this is a design finding rather than a condition-10 one; the docstring's "what each
adds" is not accurate.

**F5. The benchmark does not exercise either new checker rule: no judgement row and no rejected
synthesis reaches the live checker.**
`run_live` sends a row to the checker only if the validator passes it (`scripts/checker_bench.py:493-497`).
Of the 139 rows, the one judgement row, `b-judgement-marriage`, is refused by the validator for its
uncited "7th" (probe; the spec notes say so too), and both rejected syntheses (`b-ranking-career`,
`b-nth-sign`) are refused by the validator. Counted by what reaches the checker: 50 plain accepts, 59
plain rejects, 7 synthesis accepts, and no synthesis reject and no judgement of either label. So the
live benchmark cannot measure whether the checker rejects a synthesis whose conclusion does not
follow (SPEC rev 117) or whether it lets a judgement through with a false or uncited premise (F1),
and it has no accepted judgement to show it does not over-refuse the kind. DoD 5 asks that each new
sentence kind be "represented in tests/fixtures/checker_bench.jsonl"; represented by rows the checker
never sees, it is not measured. 6f49627's message says "too-narrow citations, a false judgement
premise and an unstated clause left to the checker": the judgement row is not left to the checker
(condition 10).

**F6. A [tradition:] sentence may describe this chart's own configuration and forecast from it, and
"strength" is not among the words it may not use.**
`TRADITION_LIMITS` (`narrate.py:287-301`) refuses digits, dates, periods, engine figures and the
deictic words "this chart", "your", "here". Probes that pass `tradition_errors` with no error:
"Saturn and Jupiter together in Taurus rising, with Mars in Scorpio in the seventh, deny marriage until
late [tradition:BPHS 18]." (the reference chart's own placements, and a marriage forecast); "A native
with Venus exalted in Pisces in the eleventh becomes very wealthy [tradition:Phaladeepika 8]." (also
this chart); "Exaltation gives a planet great strength [tradition:BPHS 3]." The heading on the page
says "From the texts, not computed on this chart", but a sentence naming exactly this chart's
placements is about this chart in everything but the deictic word, is never checked, and is the
place the reading can now forecast without any gate. The verse-attribution risk is the triage's job
by design; this is not that. What it breaks: SPEC rev 118's limits ("no … strength …, and nothing
about this chart"); a4fd25d's message says the validator refuses "anything about this chart".

**F7. The blind comparison's settings are one unauthenticated request away, and the view still
carries `depth`.**
The page's URL names both reading ids (`/compare/{a}/{b}`), and `GET /readings/{id}`
(`src/jyotish/api.py:824-833`) needs no token and returns the stored document unredacted (`writer`,
`usage`, `model`, `attempts`) and the rendered `page`, whose header carries the reproduce command with
`--writer-model`/`--writer-effort`. A reviewer who opens `/readings/<a>` sees which settings made the
reading whose text matches A. `compare_order`'s docstring (`api.py:326-332`) says "the URL says
nothing"; it says which two readings, and the readings say the rest. Separately, `blind`
(`api.py:310-316`) strips `chart.depth` but not the top-level `depth` of the Reading, so
`readings.A.depth` is in the view JSON; between depths the analysis sections reveal the depth anyway,
but between two settings at one depth this is a needless field, and the test
(`tests/test_compare.py:55-64`, both readings at astrologer depth, `tests/test_compare.py:21`) could
not see it. What it breaks: SPEC rev 117 ("with their settings withheld … only the answer reveals
the settings").

**F8. Three benchmark labels disagree with each other or with what the checker already passed.**
(a) `b-hyphen` is labelled accept although its last clause, "the facts leave the net quality of that
placement open", is stated by no field it cites (its audit says "which is so"); `b-votes-fact` is
labelled reject (`unstated_claim`) for a last clause of the same kind, "this reading draws no medical
statement from them" (`scripts/checker_bench.py:356-363`). One of the two labels is wrong, and the
benchmark rewards whichever way the checker happens to go on one of them. (b) `b-judgement-marriage`
is rejected because "the lord and KP votes both rest on the 7th lord's own-sign placement" is read as
"rest on … alone" (`checker_bench.py:345-348`); B's shown summary, which the live checker passed,
says "the lord vote rests on Venus, the exalted lord of the 6th, and Mercury, lord of the 2nd" for a
vote over fifteen rows. Either that summary sentence is a checker miss in an audited reading, which
DoD 5 says becomes a benchmark row, or the judgement row's reason is wrong. (Its other premise, "the
arudha vote rests on Rahu alone in the Upapada", is false on the facts it now carries — the marriage
arudha vote `rests_on` UL, UL2 and A7 — and would be the sounder reason.) (c) The three `b-stability-*`
accept rows rest partly on `stability.lagna_sign_by_varga.D10` = 0.795 and `.D9` = 0.78, bare numbers:
the "label every stability" fix (63d2bde) did not reach this field (nor `areas.<a>.votes.<f>.stability_time`),
so "holds in 0.795 of the birth-time samples" passes only if the checker reads the meaning from the
path name, which is the B-style unlabelled fact the fix set out to remove. 63d2bde's message and the
spec notes say "a stability is an object everywhere in the payload" (condition 10).

**F9. The payload carries 24 absolute longitudes, which the depth-full departure from item 9 does not
allow.**
`bhava_bala.whole_sign.H<n>.madhya` and `bhava_bala.sripati.H<n>.madhya` are sidereal longitudes in
degrees (36.3 for H1, the lagna to a tenth of a degree; 6.3 for H12), dumped from the model at
`fullchart.py:423`. SPEC rev 117 departs from item 9 "only as the chart table does: a position is its
sign and degree within the sign"; the KP cusps and Sripati madhyas elsewhere in the payload are
written that way. `tests/test_fullchart.py:97-98` looks for the lagna as `f"{asc:.3f}"` ("36.292"), so
a value rounded to one place passes it.

**F10. `not_computed.retrieval` is false on a depth-full reading, and a sentence citing it passes.**
`fullchart.py:128`: "no corpus of the classical texts is searched: the only verses cited are those
checked on rules". The [text:] tags are indeed only checked verses (`narrate.py:736`), but at depth
full the same page shows [tradition:] citations whose chapters nobody has checked. A not_said
sentence "The only verses this reading cites are those checked on the engine's rules
[fact:not_computed.retrieval]" is supported by its fact and shown beside "From the texts … unverified".

**F11. The comparison counts judgement sentences as checked and does not report them.**
`scripts/compare_readings.py:96-100` counts every tagged sentence of the summary, paragraphs and
analysis as "Checked sentences shown" (`compare_readings.py:142`), which after 1d55b41 includes
judgements, whose weighing is not checked; the report has rows for synthesis and tradition sentences
and none for judgements. The re-run Ray is to make (DoD 7) will report a checked count that mixes the
two and no judgement count.

**F12. `houses.<basis>.<n>` is whole-sign whatever `Meta.house_system` says, and does not say so.**
`fullchart._houses` (`fullchart.py:103-117`) counts houses by whole signs; `planets.<p>.house` is the
chart's own house, which is the Sripati bhava when `Meta.house_system` is `sripati`
(`src/jyotish/chart.py:74`). Under that setting `houses.lagna.1.occupants` and `planets.Saturn.house`
can disagree, and both are citable facts. Default whole-sign charts are unaffected. CLAUDE.md rule 1
(a convention is a setting, stated).

**F13 (low). Smaller points.**
- `_cites_family_fact` (`narrate.py:451-457`) lets any sub-path of `contributions` stand for every
  family's vote tag: "The KP vote is against career [fact:areas.career.contributions.strongest]"
  satisfies the family rule although the field states only "lord". The checker should refuse the
  sentence, so this costs a check rather than a wrong page; the spec notes' wording ("for the families
  it states") is narrower than the code.
- Two "lord terms": `areas.career.votes.lord.term` is 6.66 (the lord term alone) and
  `areas.career.contributions.ranked.0.term` is 8.702 (lord plus dispositor, `fullchart.py:343, 354`).
  A sentence citing one for the other is refused for the engine's inconsistency, the B pattern again.
- `vimshottari.first_maha_starts_before_birth` is the literal `True` (`fullchart.py:209`), a value no
  layer computes (CLAUDE.md rule 2), true by construction except when the Moon sits on a nakshatra's
  first degree.
- Under section retries, "two claims for X" goes into `errors` but not `unit_errors`
  (`narrate.py:1677-1679`), so the retry instruction does not tell the writer about it.

**F14 (process). The batch is not done by the definition it was built under.**
DoD 7: 63d2bde, 9cc2d41, 1d55b41 and 87fec27 each change the writer's prompt, payload or settings, and
the comparison has not been re-run (it needs the API key; the command is in the spec notes for Ray).
Until it runs, the pass rate, gaps, cost and time in SPEC rev 118 describe the engine before these
five commits. DoD 4: at the time of this review CI for 87fec27 and 6f49627 was still in progress
(`gh run list`); 63d2bde, 9cc2d41 and 1d55b41 passed. DoD 5 and 10: see F5 and F8, and Part 3.

## Part 2 — The questions asked

**Can any sentence reach the reader unchecked other than a [tradition:] sentence?** Yes, two ways.
An untagged sentence without a listed verb, in a section or the summary (F2); and the parts of a
judgement sentence the checker is told not to list, which can carry a fact or a date (F1). Section
retries add none: a held unit was validated and checked in full in the attempt it passed
(`narrate.py:1656-1660, 1671-1672, 1707-1708, 1784-1803`), is never re-validated, and is what the reading shows. The one
change of guarantee is that a held unit is final after one pass of the checker, where SPEC item 10
notes the checker is a sample; but the old policy also kept a claim from any attempt that passed, so
this is the same exposure for claims and somewhat less for sections (now checked in each attempt
rather than only when the whole draft passed). Engine-written text (the summary fallback, timing
line, notes) is the engine's and not in question. Tradition sentences are out of the checked text as
designed (`split_traditions`, `narrate.py:1534-1550`).

**Can the judgement form carry an unchecked factual claim past the checker?** Yes (F1): by the
checker prompt's own exclusion of "how it reads a fact" and "which way it resolves", and because an
uncited clause is not a premise "taken from its cited findings". The validator's limits (a tag, a
digit only with a fact, no tier word) do not reach either.

**Does `fullchart.payload` state anything the engine does not compute, or leave out something the
prompt tells the writer to cite?** States: the contributions ranking as "what each adds" (F4); a
retrieval claim that the depth-full page itself contradicts (F10); a hard-coded period flag (F13);
whole-sign houses unlabelled under a Sripati setting (F12). Leaves out (as citable): every rule fire
(F3); stability labels on the varga lagnas and vote stabilities (F8c). Also states absolute
longitudes the spec does not allow (F9). Everything else the prompt names resolves: `chart.constants`,
`houses.<basis>.<n>`, `not_computed`, `transits.range`, `timing.<area>`, `vimshottari.current`,
`yogini.periods.<i>`/`chara.periods.<i>` (whose `current` is an index into the list, which B used
correctly), `areas.<area>.contributions`, the arudha `rests_on` and `why`, `varga_dignity_label`.

**Does the blind comparison leak settings before the answer?** Through the page's own JSON, only
`depth` (F7). Through the open `GET /readings/{id}` with the ids in the URL, everything (F7). The
reveal itself is correct: only after an answer, once per reviewer and pair, A fixed per reviewer by
the hash, both roles taken across reviewers (tests/test_compare.py exercises these).

**Are the benchmark rows' labels and audits right against the facts they carry?** Checked by hand
against each row's `facts`: the three varga claims (every planet, sign, label and score against the
D10, D9 and D30 rows), the three stability sentences (2 of 3 ayanamsas for every placement cited;
0.795 and 0.78), the ranking fix (Venus 6th lord exalted in the 11th at 1.33; Mars 7th lord and 10th
from the Sun, own, 1.3; Mercury 2nd lord in the 10th, 1.19; lord ranked first), the 10th-house fix
(Aquarius, targets Aquarius and Taurus, A10 Taurus), the arudha fix (rests_on A10; Jupiter and Saturn;
balance), the synastry fix, the navamsa chain (Capricorn, own, 12th from the D9 lagna, own final
dispositor, empty activation), b-ranking-longevity's audit (longevity's engine weakest is varga):
all right. Wrong or inconsistent: F8 (a), (b) and (c). The varga labels themselves were also checked
against the natural relationships (Mercury in Libra friend, in Aquarius neutral; Jupiter in Virgo
enemy; the Moon in Aries neutral; and the rest): right.

**Does each commit message claim only what a test or committed report shows?** Part 3.

## Part 3 — Commit by commit (condition 10)

- **f59467f** (part 1). "every rule fire and placement with its status … under stable paths" and
  "[fact:<path>] cites any field": the rule fires are in the payload but not citable (F3). The two
  sizes (356,177 and 456,098) are in the spec notes of the same commit and the first is held by
  `test_payload_size_is_recorded`. Otherwise as claimed.
- **d10a057** (part 2). Claims match the code and tests (thinking, effort, writer override, usage,
  three sections, synthesis rule in the checker prompt, gaps per section). "checked sentence by
  sentence" holds only for tagged sentences (F2).
- **a4fd25d** (part 3). "refuses … anything about this chart": it refuses three deictic phrases (F6).
  The rest (placement, one citation, no other tag, numerals, dates, periods, engine figures, the
  triage file, never checked) is as claimed and tested.
- **6b7adf8** (part 4). "with their settings withheld": withheld from the page's JSON except `depth`,
  not from the reading endpoint (F7). The cache and insert races: fixed and tested
  (`tests/test_cache.py`, `tests/test_compare.py`).
- **63d2bde**. "A stability in the payload is an object": not `stability.lagna_sign_by_varga` or the
  votes' `stability_time` (F8c). The 402,380 characters are in the spec notes and held by the size
  test. Labels, constants, houses, not_computed, renamed fields, `rank_of_12`, `main_karaka`: present
  and tested.
- **9cc2d41**. Accurate as written ("its term times its confluence weight"; "the lord family is the
  strongest in all three areas read" holds). The design problem is F4.
- **1d55b41**. "the checker lists only its premises, each true and stated as the fact states it,
  never the weighing" describes the prompt; it is the gap of F1. "The validator keeps a judgement in
  the analysis, citing what it weighs, stating no figure, date, period or tier word except by citing
  the fact": any fact satisfies it, including one that does not state the figure (F1).
- **87fec27**. Every number (18 of 47 units, 29,338 against 36,702 characters, 37 checker calls in
  attempt 2, 35 units held, 12 gaps either way) reproduces exactly from `scripts/section_retries.py`
  on this checkout and is recorded in the spec notes of the same commit; the test holds their
  direction. As claimed.
- **6f49627**. "139 rows", "the validator alone catches every wording row with no false reject":
  reproduced (139 rows, 58 accept / 81 reject; docs/scorecard.md: precision 1.000, recall 0.272, 20 of
  20 wording rows, 0 false rejects). "a false judgement premise … left to the checker": the validator
  refuses that row first (F5).

## Part 4 — What was checked and found sound

- Section retries: held units skip validation and checking and are ignored when resent
  (`narrate.py:1656-1660, 1671-1672, 1707-1708`); a held summary may come back empty and an unheld one
  may not; every unit that passes the validator is checked in its attempt; the retry instruction
  lists held units and quotes each failed unit's validator errors and checker refusals; the other
  depths keep whole-draft retries. `scripts/section_retries.py` reproduces the spec notes' table.
- The tradition path: taken out of the checked text before the page is built, refused outside the
  analysis and with any other tag, citation form and text list enforced, never sent to the live
  checker by the benchmark, appended to the candidate file only on a live reading.
- The validator's new refusals: "the nth sign" at depth full, an uncited ranking, a judgement outside
  the analysis or without a tag, the navamsa-chain and hyphen fixes, the family rule satisfied by an
  area's votes or contributions fact.
- The blind page's reveal, its one-answer rule, its per-reviewer order and both-roles property, and
  the exclusion logged on opening.
- The varga labels against the natural relationships; the arudha derivation's `rests_on` and `why`;
  the constants and houses tables on the reference chart (whole-sign default).
- `pytest -q` on this checkout at 6f49627: 1,095 passed, 4 skipped (the live tests), 4 min 55 s. The
  suite is green; none of the findings above is caught by it.
