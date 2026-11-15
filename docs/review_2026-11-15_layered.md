# Independent review: the layered answer (2026-11-15)

Definition of done, item 9. Reviewed: the eight commits "Layered answer 1" to "Layered answer 8" on main (37f27b1
through 3e4c023), against SPEC.md Layer 8 rev 134 ("The layered answer"), docs/definition_of_done.md,
docs/spec_notes_2026-11-15.md and CLAUDE.md. The reviewer did not build this work and fixed nothing. No model was
called and no key was read.

What was done:
- Read `plan.py`, `bank.py`, the composer, polisher, worksheet and stored-answer code in `conversation.py`, the
  worksheet endpoints in `api.py`, `BankReviewRow`, `AnswerRow` and `AnswerStore` in `db.py`, Alembic 0007 and 0008,
  both erasures in `outcomes.py`, `export.py`, `costs.py`, `scripts/draft_bank.py`, the `layered` step of
  `scripts/evaluate.py`, `tests/test_layered.py`, the frozen seven turns and `docs/layered_2026-11-15/`.
- Read all 126 bank rows (378 variants) as a client would.
- Composed the reference chart's answers for five questions under two session keys.
- Composed every area of 200 random synthetic charts (`synthetic_cohort.births(200, 7)`) under three session keys
  with draft meanings on, plus one weakest-areas turn per chart, and scanned every sentence for faults. "The scan"
  below means this run.
- Reproduced the worksheet, rewrite, follow-up and erasure faults in small scripts. The commands are under each
  finding.

Findings are listed most severe first. H = high (the client is told something the chart does not state, an
unapproved meaning can reach a client, or an erasure fails). M = medium. L = low.

---

## H1. A fact row says several planets sit in one sign when they do not (Rahu and Ketu included)

**Where.** `data/bank/families.yaml:3` (`family.arudha.against.many.hard.alone`) and
`family.arudha.against.many.hard.helped`. The slot comes from `plan.py:197-216`. The check that let the row through
is `scripts/draft_bank.py:113` and `:286-303`.

**What is wrong.** On a "many" arudha item the plan's `{planets}` holds every hard occupant of every pada sign
(`occ` over all padas, `plan.py:200-202`). The row says
"`{planets} {sits} in one of these signs`", which states that they share one sign. Each fact row was checked once,
on the first chart where its signature appeared (`found.setdefault`). That sample evidently had one hard planet,
so the sentence was true there. The spec's promise for a fact row ("says only what the chart object states;
verified once against its signature") holds only if the variant is true for every value the slot can take. No
check covers that.

**Failure scenario.** The scan found 501 such sentences, for example:

> The signs that show how others see marriage, Sagittarius, Capricorn and Gemini, lean unfavourably, and Ketu, Saturn
> and Rahu sit in one of these signs with no helpful planet in any of them.

Rahu and Ketu are always six signs apart. The client is told a placement no chart can have. The "helped" row's "with
{helpers} beside to help" makes the same claim about the helpers.

**Fix.**
- Rewrite these rows to say that the planets sit among these signs, or plan one item per pada with the planets in it.
- Make the check cover slot shapes, not one chart. In `draft_bank.py`, check each fact variant on several samples
  per signature: one value and several, an empty `dignity`, a node, the Sun or Moon, one house and several. Record
  the samples on the row.
- Add a property test that composes every area of N random charts and refuses known-false shapes (H1, H2, M6).

## H2. "Raja yoga (… joined)" is told for a yoga formed by aspect or exchange

**Where.** `plan.py:65-67` (`RULE_PLAIN` for both Kendra-Trikona rules) and `data/bank/rules.yaml:460`
(`rule.yoga.kendra_trikona_raja.full`, every variant: "formed by {planets} in your {houses} house"). The engine's
fallback sentence (`plan.py:242-245`) carries the same gloss.

**What is wrong.** The rule fires on `related_by: [conjunction, mutual_aspect, exchange]`
(`rules/yoga.kendra_trikona_raja.yaml`), but the gloss tells every client the two rulers are "joined". The row
then puts both planets in a joined list of houses with a singular "house".

**Failure scenario.** In the scan, 324 sentences took the shape:

> Your chart holds raja yoga (the rulers of an angular house and of a trine house joined), formed by Mercury and
> Jupiter in your 1st and 7th house, and it bears on your career.

Planets in the 1st and 7th houses are opposite each other, not joined. The client is told a conjunction the chart
does not have.

**Fix.** Plan the relation as a slot (`{relation}`: "together in one sign", "facing each other", "each in the other's
sign"), filled from the fire's derivation. Give the row one house per planet ("Mercury in your 1st house and Jupiter
in your 7th"), and drop "joined" from `RULE_PLAIN`. The same check applies to every `RULE_PLAIN` entry whose rule has
several `related_by` or `basis` values. Gaja Kesari's BPHS form (lagna or Moon) is the next one; see M9.

## H3. "Right" on one variant approves all three, and the worksheet shows only one

**Where.** `bank.py:347-349` (`apply_reviews`, verdict "right"); `bank.py:350-356` ("change" also sets the whole
row `approved`); `web/js/review-session.js` (the worksheet shows the told sentence and the line "variant {variant} ·
{status}", never the other variants); `conversation.py:849` (a meaning row is shown when `status == "approved"`).

**What is wrong.** The astrologer judges the one sentence the client read. Approval is per row, so his "Right"
approves two variants he was never shown, and so does "Change" on one variant. For a meaning row this breaks the
spec's line "no public client sees an unapproved meaning": after `jyotish bank apply-reviews`, every client whose
session hashes to another variant reads a meaning sentence nobody approved. Some of those sentences are wrong (M9).

**Failure scenario.** The astrologer opens the worksheet for `rule.yoga.gaja_kesari_bphs.reduced@career` and approves
the variant he read. A public client whose session reads variant 0 is then told "a pairing of Jupiter in an angular
house from the Moon", although their yoga fired from the rising sign.

**Fix.** Make approval per variant: an `approved: [i, …]` list, or a status per variant. Let the composer use only
approved variants of a meaning row, falling back to an approved sibling variant. Alternatively, have the worksheet
show all three variants with "Right" stating that it approves all three. Test that one verdict on variant `i`
leaves the other two unapproved.

## H4. An astrologer's rewrite can become one chart's values for every chart

**Where.** `bank.py:304-311` (`template`); `conversation.py:1549` (the worksheet's items keyed by `(signature,
area)`); `api.py:1083-1086` (the verdict stores `sent["looked_at"]["slots"]`); `outcomes.py:308-310` (erasure sets
the verdict's `slots` to None); `bank.py:352` (`template(v.words or v.sentence, v.slots or {})`).

**What is wrong.** A "change" turns the chart's values in his words back into slots by literal, case-sensitive
matching, and three things defeat it:
1. **Capitals.** The slot is "the Sun"; his sentence starts "The Sun". `template("The Sun, the main planet of your
   career, is in a feeble state by its degree in Aquarius.", slots)` returns "The Sun, {role}, is in a feeble state by
   its degree in {sign}." (reproduced). Every later chart's main significator in a Mrita state is then called the Sun.
2. **The wrong item's slots.** Two items of one signature in one area overwrite each other in the worksheet's
   `items` dict. On the reference chart's career turn, `weakness.mrita` holds Saturn (the 10th lord) and the Sun
   (the main significator). Saturn's sentence shows the Sun's facts and slots on the worksheet (reproduced: told
   "The ruler of your 10th house, Saturn, is in a feeble state by its degree in Taurus.", slots planet "the Sun",
   sign "Aquarius"). A verdict on it stores the Sun's slots, so "Saturn" and "Taurus" stay literal in his rewrite.
   The astrologer is also shown the wrong facts for the sentence he is judging.
3. **Erasure first.** If the conversation is erased before `apply-reviews`, the slots are None and the whole
   rewrite is written as a literal: the erased client's planets, signs and houses, shown to every later client.

`row_errors` passes all three outcomes. The rewritten variant's check is dropped (`bank.py:355`), and `_usable`
treats a row with no failed check as usable (`conversation.py:812`), so nothing re-verifies it.

**Fix.**
- Key the worksheet items by the item's index in the plan, kept on each composed sentence, not by `(signature,
  area)`.
- Template case-insensitively, with the capitalised form of each value.
- Refuse (report, do not write) a rewrite whose slot set differs from the variant it replaces.
- Keep the verdict's slots through erasure, without the turn: the planet and sign names are not the birth. Or apply a
  pending "change" before erasing.
- Have the gate checker check the rewritten variant once against the item's facts, as the drafted variants were.

## H5. A subject's erasure fails on Postgres once a bank verdict exists, and leaves the stored answers

**Where.** `outcomes.py:262-267` (`erase`, the subject's erasure). It deletes `ReviewRow`s with the turns, then the
turns, but never touches `bank_reviews` (FK `turn_id → turns.id`, Alembic 0007, no ON DELETE) or `answers`.
`erase_sessions` (`outcomes.py:306-316`) handles both; `erase` does not.

**Failure scenario.** Reproduced on SQLite with `PRAGMA foreign_keys=ON`, which is what Postgres enforces. A
subject, a conversation with one turn, one bank verdict on that turn and one stored answer, then
`outcomes.erase(s, "subj1", …)`:

> IntegrityError (sqlite3.IntegrityError) FOREIGN KEY constraint failed [SQL: DELETE FROM turns WHERE
> turns.session_id IN (?)]

The subject's erasure, a legal right, fails entirely once the astrologer has given a verdict on any of their turns.
Without foreign keys (SQLite's default, which the suite runs) it succeeds but leaves the `answers` row, whose
document holds the plan, including the client's own question (`plan.question`), under their birth key.

**Fix.** In `erase`, treat `BankReviewRow` as `erase_sessions` does (take the turn off, or delete it). Delete
`AnswerRow` by the birth key unless a twin keeps the chart. Add a test that runs `erase` with foreign keys on, with a
bank verdict and a stored answer present.

## M1. The polisher's check misses omissions and invented causes, and the committed run shows one shown

**Where.** `conversation.py:652-658` (one checker call: is every proposition of the polished text in the composed
text?); `POLISH_SYSTEM` (`conversation.py:566-604`).

**What is wrong.** The check runs one way only. A polished text that drops the hard paragraph, a reduction, the
"no amount, no promise" opening or the "Neither stretch is a prediction" caveat passes, because every proposition
left is in the composed text. The prompt asks for these to be kept, but nothing verifies it. A connective can also
add a proposition that the checker, reading 25 sentences as one "sentence", let through.

**Failure scenario.** `docs/layered_2026-11-15/layered-polished-1.turn.json`, where the polished text was shown
(`used: true`). The composed text has three separate facts: Saturn in a draining house, Saturn in a feeble state, and
Saturn below its needed strength. The polished text makes the strength a consequence:

> …the degree Saturn holds in Taurus puts it, as that ruler, in a feeble state, so it has less strength than it
> needs to give fully what it promises for your father.

The engine never derives the Shadbala ratio from the Mrita state. The client is told a cause the chart does not
state.

**Fix.**
- Run the check both ways: every composed proposition must be in the polished text, and the reverse.
- Before any call, check in code that every date range, planet, sign, house and lean word of the composed text is in
  the polished text, and that the opening and caveat sentences keep their places.
- Refuse added causal connectives ("so", "because", "therefore", "which is why") that the composed text lacks.
- Add the polished-1 text as a `where: "polish"` benchmark row marked unsupported.

## M2. The polisher is hard-wired to Anthropic, and its failure fails the turn

**Where.** `conversation.py:629` (`AnthropicBackend(POLISH_MODEL, CONFIG)`), `:634-639` (only `NarrationError` is
caught).

**What is wrong.** The spec notes say "Either call failing also shows the composed text". With no Anthropic key the
SDK raises a `TypeError` on the call, not a `NarrationError` (reproduced: `polish(...)` with `ANTHROPIC_API_KEY`
unset raises "Could not resolve authentication method"). So `JYOTISH_POLISH=1` on a service with no Anthropic key
fails every placed turn instead of showing the composed text. Every other role picks its backend from
`JYOTISH_<ROLE>_BACKEND` (CLAUDE.md, "Model backends"), but the polisher does not.

**Fix.** Make the polisher a role (`make_backend(None, "polisher", CONFIG)` with `JYOTISH_POLISHER_BACKEND`, a
DeepInfra model allowed). Catch every exception from both calls and record it in `refusals`. `/health` should report
the polisher's readiness when `JYOTISH_POLISH` is on.

## M3. A stored answer crosses conversations: wrong variants, repeated follow-ups, and another client's question

**Where.** `conversation.py:672-691` (`answer_key` leaves out the session), `:704-714` (a hit is merged into the
turn: `doc | hit`), `:851-854` (a follow-up drops only sentences found verbatim in the earlier answers).

**What is wrong.** The notes read "same chart, same routed question" literally. Three faults follow:
1. **Wrong variants.** Conversation B's first turn is A's text, A's variants. The spec says the variant is "chosen by
   a hash of the session so one client's answers vary and stay stable", and B gets A's.
2. **Repeated follow-ups.** B's follow-up is composed with B's own variants, so none of its sentences is found in
   what B was shown, and the whole answer repeats in other words. Reproduced on the reference chart: "how is my
   career" then "why?". With the same session key the second turn is one sentence ("the chart has no further reason
   to add"). With turn 1 from another session it is nine sentences, every reason restated.
3. **Another client's question.** `hit["plan"]["question"]` is A's message, now stored in B's turn document. It
   survives A's erasure, which deletes the `answers` row but not B's turn. Two clients can share a birth key (twins;
   `cache.birth_key` says so). The second one's records then hold the first one's words.

**Fix.** Put the session key in `answer_key`. Within a session the store still saves the polisher call on a repeated
question, and across sessions it saves nothing that matters at USD 0 a composed turn. Failing that, store the plan
and composed items without the message, and re-fill the variants from the session. In either case, drop
`plan.question` from what is stored.

## M4. A follow-up after a polished turn repeats everything

**Where.** `conversation.py:851-854` and `:1325` (`said` is the earlier turns' `shown`).

**What is wrong.** The repeat filter is a substring test of composed sentences against what the client read. After
a polished turn the client read the polished text, so no composed sentence matches and nothing is left out. This
breaks the 2026-11-02 rule that a carried-area follow-up repeats nothing.

**Fix.** Filter on what the earlier turns composed (the signatures and slots of `composed.sentences`), not on text.
The turn document already holds them.

## M5. The ".nohouse" rule rows are never used, and the coverage figure counts them as found

**Where.** `conversation.py:809-813` (`_usable` requires every declared slot but `dignity` to be non-empty);
`data/bank/rules.yaml` (every `.nohouse` row declares `houses`, which no variant uses); `bank.py:286` (coverage
checks slot names only); the `layered` step of `scripts/evaluate.py`; `docs/scorecard.md` (`bank.coverage.rule`).

**What is wrong.** A `.nohouse` item has `houses: ""` by construction. Every `.nohouse` row therefore fails
`_usable`, and the engine's sentence is shown instead. Coverage counts the item as found. On 60 random charts ×
career, wealth and marriage, all 80 `.nohouse` rule items that had a row fell back to the engine's sentence. 127 of
the 220 rule items came from the bank. The scorecard's 96% for rules is not what clients read: 13 rows and their
checks are dead. This also breaks DoD 4: the number in the scorecard is wrong.

**Fix.** Declare in a row only the slots its variants use (`row_errors` can refuse an unused declared slot). Make
`coverage` apply `_usable` itself, slot values included, so the figure is the composer's rule. Re-run the scorecard.

## M6. Grammar faults the composer puts in front of clients

**Where.** `bank.py:113-130` (`agree`, `tidy`) and the rows named.

**What is wrong.** Each of these is reproduced:
- **",, and"** after an empty dignity, for Rahu and Ketu as significators: 478 sentences in the scan.
  `families.yaml:425` `family.karaka.for` v3 "…in your 12th house,, and together these planets lean favourably."
  `tidy` removes ", ." but not ", ,".
- **"sit … and forms"**: `rules.yaml:460` v3 "The Sun and Mercury sit in your 10th house and forms raja yoga…". Shown
  to a third of sessions on the reference chart's career, and frozen into `tests/fixtures/layered_seven_turns.json`
  (M10). This is the spec notes' open item, still live.
- **"are the Sun"**: `weaknesses.yaml:3` `weakness.low_strength` v2 with a lord-and-significator role: "the ruler of
  your 9th house and the main planet of your father are the Sun, and it holds less strength…". `agree` makes a verb
  plural when `{role}` contains "and", but a role is always one planet. The same rule turns `weakness.mks@marriage`
  and `@wealth` v1 into "When the ruler of your 2nd house and the main planet of money sit…" (6 in the scan).
- **"The planet the Sun"**: `families.yaml:638` `family.panchanga.against.one` v1: "The planet the Sun, a ruler of
  the day you were born, leans unfavourably for yourself and your temperament."
- **"in your 1st and 7th house"**: see H2. The same singular "house" follows a joined `{houses}` in most rule rows.

**Fix.**
- `tidy`: collapse ", ," and ",," to ",".
- Never pluralise after `{role}` (add it to the exclusions in `agree`).
- Have `agree` mend a coordinated second verb ("and forms" after a plural subject), or rewrite the variants to have
  one verb.
- Use "{houses} house" only when `houses` is one value, else "{houses} houses" (an `{house_word}` slot).
- Rewrite panchanga v1.
- Add each of these shapes to the property test in H1.

## M7. Merging several areas into one item overstates what each area has

**Where.** `plan.py:484-501` (the period merged across areas), `:469-475` (a rule merged across areas), and
`conversation.py:848-850` (the merged rule's meaning row for its first area, filled with every area).

**What is wrong.** The merged period sentence pairs the union of lords with the union of areas. On the reference
chart's weakest-areas turn the client reads "Jupiter and Mercury have a hand in your father, your reputation and
brothers, sisters and courage". Mercury touches father and siblings but not reputation (`_period_item` for
reputation gives `touching: ['Jupiter']`). Likewise, a rule merged over career and wealth is followed by its
`@career` meaning row filled with "your career and money". The career reading is then told as the tradition's
reading for money, though the row's citation and the astrologer's approval were for career only.

**Fix.**
- Period: name each lord with its own areas ("Jupiter has a hand in all three, Mercury in your father and brothers,
  sisters and courage"), or keep one period sentence per touched set.
- Merged rule: show the meaning row of each area with its own area's label, or none when the areas differ.
- Keep `facts.touching` the union, so the worksheet says what was told.

## M8. A withdrawal cannot be undone, and an older verdict can override a newer one

**Where.** `bank.py:336-369`.

**What is wrong.** Two faults:
1. **No way back.** "Right" and "change" never clear `withdrawn_by`, and `Bank.fact`/`meaning` return None for a
   withdrawn row. If the astrologer marks a row wrong and later rewrites or approves it, the report says "rewritten"
   or "approved", but no client ever sees the row again.
2. **Order.** Verdicts are applied newest first, deduplicated by (row, variant). A newer "right" on variant 1 is
   applied, then an older "wrong" on variant 0 withdraws the row. The older judgement wins.

**Fix.**
- Apply verdicts oldest first, so the latest per row decides the row's state, and the latest per variant decides
  that variant's words.
- Make "right" and "change" clear the withdrawal, or report that the row stays withdrawn.
- Test a wrong-then-change sequence.

## M9. Meaning rows that are wrong in substance (drafts, to fix before anyone approves them)

**Where.** `data/bank/meanings.yaml`.

**What is wrong.**
- **Gaja Kesari called a lion.** `rule.yoga.gaja_kesari.*` (from `meanings.yaml:187`): "the lion combination", "whose
  name means a lion". Gaja Kesari is elephant and lion; the BPHS rows say so correctly.
- **The BPHS form told from the Moon.** `rule.yoga.gaja_kesari_bphs.reduced@career` (`:360`) and `@wealth` v1 and v3,
  and `.reduced.nohouse` v3 (`:322`): "in an angular house from the Moon", "With Jupiter at an angle from the Moon".
  The BPHS form fires from the rising sign as well (`basis: [lagna, moon]`). This is the same disagreement the notes
  set aside for Gaja Kesari's fact rows, still present in its meaning rows.
- **Sasa's name.** `rule.yoga.sasa.*` (from `:752`): "the Saturn combination named for discipline and authority".
  Sasa means hare.
- **Ruchaka's name.** `rule.yoga.ruchaka.reduced.nohouse@career` (`:697`) v1: "named for courage and command". The
  other Ruchaka rows say "radiant".
- **Two weaknesses run together.** `weakness.mks@career` (`:864`) v2 says a planet in a draining house is "a planet
  short of the strength it needs". That is the low-strength weakness, a different finding.
- **No planet named.** `weakness.mks@marriage` and `@wealth` (`:883`) v2 and v3 speak of "a planet" in general and
  never name it. The client cannot tell which planet the sentence is about.

**Fix.** Redraft these with the rule's glossary entry and its `basis` given to the drafter. Add a load-time check
that a meaning row for a rule with `basis` beyond `moon` does not say "from the Moon". The astrologer then reads them
as part of the first hour (DoD 8).

## M10. The frozen texts and the tests would not catch these regressions

**Where.** `tests/test_layered.py:408-422` (seven turns, one chart, one session key "seven"), `:295-296`,
`tests/fixtures/layered_seven_turns.json`.

**What is wrong.**
- **The fixture freezes a fault.** It holds "The Sun and Mercury sit in your 10th house and forms raja yoga…" as the
  expected text, so the fix for M6 shows up as a test failure, and recording the fixture again is how such a failure
  gets cleared. The frozen text is compared, never judged.
- **One chart, one key.** Every fault in H1, H2 and M6 depends on slot values (several planets, empty dignities,
  nodes, aspects) or on the variant. The reference chart under key "seven" shows almost none of them.
- **No property test.** No test composes over random charts and asserts anything about the sentences.
- **A weakened assert.** `:295-296` is `assert … endswith(…) or "[rule:yoga.ruchaka]" in r["tagged"]`, so its first
  half asserts nothing.
- **No cross-session test.** No test serves a stored answer to a second session (M3), polishes a turn and then asks
  a follow-up (M4), runs the subject's erasure with a verdict present (H5), or rewrites a capitalised slot (H4).

**Fix.**
- Add a property test: every area of 200 synthetic charts, every variant (loop the session key over the three
  residues), asserting no literal "{", no ", ,", subject-verb agreement on the slots `agree` knows, and that
  `family.arudha.*.many` never names two planets as sharing one sign.
- Freeze all three variants of the seven turns, not one.
- Drop the `or` at `:295-296`.
- Add the tests listed in each finding above.

## M11. Any reviewer can approve bank rows

**Where.** `api.py:1066-1090` (`post_worksheet_verdict` takes `reviewer(request)`, any reviewer token); `bank.py`
`apply_reviews` writes every reviewer's verdict.

**What is wrong.** The spec gives the verdict to the astrologer ("his verdict … stored against the bank row, so one
correction reaches every later client"). Reviewer tokens also go to blind-comparison judges and guided-review
reviewers (`JYOTISH_REVIEWERS="judge-1:…"`). Any of them can approve a meaning row for every public client.

**Fix.** Add a role to `credentials` (`astrologer`), and accept bank verdicts only from it. Alternatively, have
`apply-reviews` take `--by <reviewer id>` and apply only that reviewer's verdicts.

## L1. "The strongest family terms" compares two different units

**Where.** `plan.py:353-359` (`_strengths`).

**What is wrong.** Terms are in the score's units. On the reference chart they run from 0.15 to 11.7 (marriage's
lord 10.68, reputation's lord 11.70). Arudha and KP are ranked by vote × min(1, weight), which is at most 1. They can
never outrank a term above 1, so whether KP is said depends on the scale, not its strength.

**Fix.** Rank by each family's percentile against 10,000 charts (`contributions`, `data/family_percentiles*.json`),
which depth full already uses for "the strongest support". Record the percentile in `facts`.

## L2. Once polished, the worksheet and the chart wheel point at the wrong sentences

**Where.** `conversation.py:743` (`c["sentences"][i]["tagged"]` indexed by the polished sentence's position);
`conversation.py:1556` (the worksheet's "told" is the composed text).

**What is wrong.** The polisher merges sentences: 24 composed became 18 polished in polished-1. The wheel then lights
what composed sentence `i` rests on beside polished sentence `i`. The worksheet labels the composed text "What the
client was told".

**Fix.** Light per polished paragraph, from the union of its composed sentences. Label the worksheet's column "Composed"
when `polish.used`, with the polished text beside it (it is already returned).

## L3. `apply-reviews` writes the bank inside the database transaction

**Where.** `bank.py:370-374`.

**What is wrong.** The YAML files are written before the final `load_bank`. If that raises, the transaction rolls
back (the verdicts stay unapplied), but the files stay rewritten. A server reloading the bank then hits the
`BankError`, or the next run applies the verdicts twice.

**Fix.** Write to temporary files, `load_bank` that directory, then rename into place and commit.

## L4. A transient checker failure on the polished text is stored for the day

**Where.** `conversation.py:757-760`.

**What is wrong.** Only "the polisher could not be reached" skips the store. A checker call that fails after its
retries returns an unchecked result (`ModelChecker.ask_one`). The composed text is then stored under the polished
key, and every asking that day is served it without trying again.

**Fix.** Do not store when the checker's result is the unchecked one.

## L5. The scorecard's composer share is 100% by construction, and composed sentences have no correctness figure

**Where.** `scripts/evaluate.py` (`layered`).

**What is wrong.** `layered.composer_share` is measured on the seven scripted turns, every one of which the route
places. The share of real turns the composer answers is not measured. No number reports whether composed sentences
are true across charts, though DoD 5 rests on that ("verified once against its signature").

**Fix.**
- Report the share over a fixed set of varied messages, including unplaced ones.
- Add `bank.composed_supported`: the gate checker on a fixed sample of composed sentences from random charts,
  reported and not gated. H1, H2 and M6 would have shown there.

## L6. Wording a client would stumble on

**Where.** Fact rows.

**What is wrong.**
- `verdict.not_emphasised` (`verdicts.yaml:67`) v2 with "Your father": "Your father is not something this chart puts
  much weight on". It calls a parent "something" and reads as a judgement of him.
- The weakness role "the main planet of your father" (`plan.py:264`) reads as the father's planet.
- `stretch.least.second` (`stretches.yaml:63`) v3: "Running …, this is the least favourable stretch in the chart". It
  is the least favourable for the area, not the chart.
- `period.now.apart` when the two lords are one planet: "the period of Mercury, within that of Mercury … neither
  rules nor signifies…" (357 in the scan).
- `opening.why` v2 drops the area ("what in your chart lies behind it").

**Fix.**
- Rewrite these.
- Make the role "the main planet for {area}".
- Plan `period.now.same` for a mahadasha lord in its own antardasha.

## L7. Smaller readings to settle

- **"The weaknesses … the lean hides".** `_weakness_items` (`plan.py:255-293`) always adds them. When the lord's
  family already leans against, nothing is hidden. Say whether the spec means always or only under a favourable lean.
- **Erasure keeps chart values.** `erase_sessions` (`outcomes.py:308-310`) keeps `bank_reviews.sentence` and
  `words`, which carry the chart's values, but the comment says those values are taken off with the turn. Fix the
  comment, or keep them deliberately (H4's fix wants the slots kept).
- **A stored answer lights nothing.** A served answer emits no `light` events (`conversation.py:708-712`), so the
  chart wheel stays dark for it.

---

## What holds

- No composed sentence carried a literal slot, a never-show word or an exception on 200 random charts.
- The plan's reference-chart career items match the sample worksheet's two faults: the three yogas are told, and
  Saturn's draining house is told.
- Draft meanings stay off by default (`show_draft_meanings`). The ledger does not charge a served answer's polisher
  again.

`pytest -q tests/test_layered.py` at 3e4c023: 42 passed in 60 s. Every fault above passes the suite as it stands (M10).
