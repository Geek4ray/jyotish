# Independent review: the shaped answer (2026-11-16)

Definition of done, item 9. Reviewed: the fifteen commits `093a736..e433f24` on main ("Shaped answer: the
three-part question … frozen" through "The conversation page's test waits for the chart wheel"), against SPEC.md
Layer 8 rev 136 ("The shaped answer (decided 2026-11-16)", its six decisions), docs/spec_notes_2026-11-16.md,
docs/definition_of_done.md and CLAUDE.md. The reviewer did not build this work and fixed nothing. No model was called
and no key was read.

What was done:
- Read the diffs of `conversation.py` (parts_of, kind_of, CHANGE, VOCATION, GREETING, AREA_VOCAB, sections_of,
  _section_for, shape, compose), `plan.py` (cannot_give, CANNOT_LINE, _weakness_items, _vocation_items, the varga and
  panchanga slots), `narrate.py` (default_top, varga_row, panchanga_ruled), `client.py` (CLIENT_FIRST_PERSON),
  `api.py` (GET /, session_day, the payload per day, /health), `db.py` and Alembic 0009, `bank.py`,
  `scripts/draft_bank.py`, `scripts/composed_check.py`, `scripts/shaped_measure.py`, `scripts/evaluate.py`, every
  bank row the batch added or redrafted (openings, `weakness.planet` and its meanings, the twelve vocation rows),
  `tests/test_shaped.py`, the frozen `tests/fixtures/shaped_three_parts.json`, and every test the batch changed.
- Ran `tests/test_shaped.py`: 85 passed.
- Split about a hundred varied English, Hinglish and Devanagari messages with `parts_of` and composed about thirty of
  them on the reference chart (`assess(...)`, as of 2026-11-16) with draft meanings off and on.
- Composed fourteen turns (ten conversations: the three-part question, "which field will i work in", "how is my
  marriage" then "tell me more" three times, "when will i marry", "what are the challenges in my life", "how are my
  career, marriage and money", "how is my health", "when will my career and money improve", "what are the problems in
  my career", "how is my career" then "why?") on 150 random synthetic charts (`synthetic_cohort.births(150, 11)`,
  `assess(n=12)`, so stability lines are present), draft meanings off and on: 4,200 answers. "The scan" below means
  this run.
- Ran the same "tell me more" and "when will my career and money improve" turns on the parent commit's code
  (`git archive 99423d7 src data rules`) to tell what this batch changed from what it inherited.

The probes are in the reviewer's scratchpad, outside the repo:
`/private/tmp/claude-501/-Users-rayankejriwal-jyotish/9c5a2d43-3608-486e-9e1f-8f806938da52/scratchpad/` (`parts.py`,
`parts2.py`: the splitting; `comp.py <draft 0|1> <session key> <message>...`: a conversation composed through
`route_turn` and `answer_turn`, "NEW:" starting a fresh one; `scan.py` and `an.py`, `an2.py`: the scan and its
counts).

Findings are listed most severe first. H = high (the client is answered something other than what was asked, or
nothing, without being told; or a named part of the question is silently dropped). M = medium (a draft row says
something false; a refusal broader than decided; repetition the shape was meant to remove; a decision's ask missed
on common phrasings). L = low.

---

## H1. "work in" makes any sentence about working somewhere a "which field" question, and a vocation-only answer drops every other area the message names

**Where.** `src/jyotish/conversation.py:540` (`\bwork in\b` in `VOCATION`); `areas_of` (`:244`, a VOCATION match names
career); `kind_of` (`:557-572`, vocation before when and yes_no); `_section_for` (`:1083-1103`) with `PLACES`
(`:985`): a lean, help or hard item goes only to a general, why or timing section, so a message whose only section is
vocation holds every area's lean.

**What is wrong.** SPEC decision 3 routes "which field", "which line", "what kind of work", "business or job" to the
ask `vocation`. The regex also takes the bare phrase "work in", which most questions about working somewhere contain.
Such a message becomes career with the ask vocation, its answer is the four 10th-house placements, and any other area
it names (foreign, marriage) is held with "no part of the message asks for it". A yes-or-no question also loses its
cannot-give line and its lean.

**Reproduced** (`comp.py 0 k "<message>"`, reference chart, draft meanings off):
- "Can I work in the US?" → parts `[vocation]`. The answer is the 10th's sign and ruler, the Sun, Mars in the D10 and
  Mercury, and nothing else. There is no lean on career and no "a chart cannot answer yes or no".
- "will I work in abroad" → areas career and foreign, parts `[vocation]`. The same four placements. Every foreign item
  (verdict.mixed, four families) is in `composed.held` as "no part of the message asks for it". The client asked about
  abroad and hears nothing about it.
- "will my wife work in a bank" → areas career and marriage, parts `[vocation]`. The client's own 10th-house
  placements are given, then `THIRD_PARTY_LINE`. The answer reads as the client's chart answering the wife's work. It
  should be the other-person handling or the client's own marriage reading.
- Also read as vocation: "I want to work in a bank, will it go well?", "will i work in the same company", "work in
  progress on my house, when will i buy property" (this one adds career to a property question).

**Why it matters.** This batch exists because the composer answered "which field" with something other than the ask.
H1 is the same fault the other way round: everyday questions get a list of placements that answers none of them, and
nothing tells the client their question was not answered. Working abroad is one of the most common questions there
is.

**Suggested fix.** Drop the bare `work in`, or keep it only after "which/what … will I". Let an area named outside
the vocation phrase keep its own general part. Add a test that composes "will I work abroad" and finds foreign's
lean.

## H2. "Tell me more" answers with nothing from the second time on, and cannot reach what the shape held from a vocation or timing part

**Where.** `conversation.py` `route_turn` (`:462`: a follow-up's `parts` are `parts_of("tell me more")`, one `goes`
part); `compose` (`:1139-1241`: no sentence when every key was said); `_composed_turn` (`:864-947`: an empty `shown`
is stored and streamed as `done` with no text). This is decision 2's "Everything else in the plan is held for 'tell me
more', which the follow-up already serves by key".

**What is wrong.** The shape now holds part of every answer for "tell me more". "Tell me more" is a `goes` part over
the carried areas, so it can reach only what a general section takes. Once that is said, the answer is empty and says
nothing:
- In the scan, the first "tell me more" after "how is my marriage" is empty on 22 of 300 charts. The second and the
  third are empty on 300 of 300.
- On the reference chart, "how is my marriage" then "tell me more" gives one sentence (the karaka help). The next "tell
  me more" gives `shown == []`.
- After "which field will i work in" (where the shape held `vocation.d10` for Saturn, "held for tell me more"), "tell
  me more" gives the career's general lean and helps. The held vocation item is never offered, because no vocation
  part is ever planned again. A change-of-job answer likewise leaves its held lean to a general follow-up only by
  chance.

The parent commit also gave an empty "tell me more" once everything had been said. Since this batch, the shape is what
creates the "more" and promises it, so the empty turn is now on the path the SPEC tells the client to take.
`test_2_tell_me_more_gives_what_the_shape_held_and_repeats_nothing` checks only the first "tell me more" on the
reference chart's career, which has three held rules.

**Why it matters.** The client asks for more and gets a blank bubble. That reads as a broken service. And what the
SPEC says is held for them (a fifth vocation placement, the lean of a change-of-job answer) is unreachable.

**Suggested fix.** A follow-up carries the last turn's parts, not `goes`. When nothing is left, say so in one fixed
line, as `OPENING_SAID` does for a "why". Test the second and third "tell me more" and a "tell me more" after a vocation
answer.

## H3. The ask `change` takes questions that are not about leaving a job, and answers them with the no-date line and no lean

**Where.** `conversation.py:530-538` (`CHANGE`) and `kind_of` (change before vocation, when and yes_no);
`_section_for` (`:1099`: a change-only section takes no lean).

**What is wrong.** SPEC decision 4 is "'When will I leave, change or switch' is the ask `change`". The regex matches
any of leave/left/quit/change/switch/resign within 30 characters before job, work, company, office or career, with or
without a "when". In every match the answer is "A chart cannot give a date for leaving or changing a job …", then the
period and the stretches, with the lean held.

**Reproduced** (`parts.py`, `parts2.py`, `comp.py`):
- "will my career change for the better" → change. The client asks for the lean ("for the better"). The lean is held,
  and the client is told a chart cannot date a resignation they never mentioned.
- "should I quit my job" and "job badalni chahiye kya" (both in the decision's tests) → change. A "should" question
  gets no lean and no yes-or-no line. The SPEC's change is a "when" question.
- "will I get leave from my office this year" and "can I take leave from work in december" → change. "Leave" as a
  holiday is common Indian English.
- "how will things change at work", "I left my job last year, what now for my career?" and "I left my job, will I find
  a new one soon" → change. The last gets "cannot answer yes or no or give a date for leaving or changing a job".
- "Should i leave my job for higher studies" → change over career and intellect. Learning's lean is held. The no-date
  line covers "your career and learning and studies". "Looking at the stretches the chart shows, the least favourable
  one runs from November 2028 to August 2029." is said twice word for word, once per area, the second naming no area.
- The other way: "should i switch careers" → yes_no, because the regex wants `career\b` and `careers` misses.

**Why it matters.** The decision answers "when will I leave". Taking every mention of change or leave hides the lean
the client asked for. It answers an unasked resignation question on the client's own page.

**Suggested fix.** Read change only with a "when", "should" or "will I" plus a leave/quit/change/switch verb whose
object is the job. Drop the noun "leave" and the past "left". Let a "should" part keep its lean. Allow "careers".

## M1. Every vocation meaning row says the planet "shapes the house of work", which is false after a D10 placement (248 of 300 draft-on answers)

**Where.** `data/bank/meanings.yaml:764-916` (`vocation.works.<planet>@career`, all nine rows); the drafting prompt
`scripts/draft_bank.py:91-94` ("the kinds of work tradition links with that planet where it shapes the house of
work"), while `VOCATION_WHAT` (`:188`) says "rules the 10th house, sits in it or is strong in the D10". The composer
attaches the planet's one row to whichever vocation item names the planet first (`conversation.py:1186`).

**What is wrong.** One meaning row per planet follows three different facts. After a `vocation.d10` item (the planet
is own or exalted in the D10 and need not touch the birth chart's 10th), the row says:

> In the divisional chart for work, which speaks to your career, Mars is in Capricorn, exalted, where it is at its best.
> For your career, Mars is traditionally linked with soldiering, policing, engineering, sport and work with metal or
> land wherever it shapes the house of work.

On the reference chart, Mars is in the 7th and rules the 7th and 12th. It does not shape the 10th. The Sun and Venus
rows say "{planet} in the house of work" ("Texts associate the Sun in the house of work …"), which is false for a D10
planet. In the scan, 248 of the 300 draft-on "which field" and three-part answers have a D10 item followed by its
meaning.

**Why it matters.** The rows are draft, so an outside client never sees them (decision 6). But Ray and the astrologer
read them now, and an approval would carry the false clause to every chart.

**Suggested fix.** Make the row neutral about the placement ("tradition links {planet} with …"). Or make three meaning
signatures per planet, one per fact kind.

## M2. The vocation meaning rows cite a text that cannot hold all of them

**Where.** `data/bank/meanings.yaml:764-916`, `source` "Brihat Jataka 10 (Karmajiva), the kinds of livelihood linked
with each planet; the verse not yet read in a named edition" (`scripts/draft_bank.py` `VOCATION_SOURCE`).

**What is wrong.** As the reviewer knows the text (the astrologer should confirm), Brihat Jataka 10 names livelihoods
for the seven planets only. It reaches them through the lord of the navamsa held by the 10th lord, the karmajiva
method the spec note left out, not through a planet sitting in the 10th. Rahu and Ketu have rows citing it anyway
(21 of the 150 scan charts have a node in the 10th, so the rows are reached). The kinds of work are the drafting
model's, including modern lore no classical verse gives: "technology", "chemicals", "astrology", "work abroad". Some
variants also attribute a reading of this client's career to the texts ("and that is how texts read it for your
career", "texts associate these with your career").

**Why it matters.** DoD 6 lets a draft stand while it carries no weight. But its `source` tells the astrologer where
to read, and for the nodes there is nothing there to read. A row approved against that source would assert a citation
that does not exist.

**Suggested fix.** Give the node rows another source (named, or `practitioner`), or none until one is given. Have the
source say the lists are the drafting model's. Drop "for your career" from the attribution.

## M3. The "client's first person" refusal also refuses the writer's own "I can see" and "in my reading", in every conversation turn, unmeasured

**Where.** `src/jyotish/client.py:60` (`CLIENT_FIRST_PERSON`) and `:274` (in `client_errors`, whatever
`WORD_RULES` says); `conversation.py:1647` (`check_sentence` calls `client_errors` for every writer-loop turn
sentence).

**What is wrong.** Decision 5 is about the reading page, where a paragraph opened "In my chart" (the client's voice).
The pattern cannot tell the client's first person from the writer's. In a conversation the writer is Tatva, and
(since 2026-11-01) its bare "I" is a warning. Reproduced with `client_errors`:
- Refused: "I can see that your career leans favourably", "I would read your career as favourable", "In my reading,
  your career leans favourably", and a sentence quoting the client's own question ("'will my marriage last'").
- Passed: "I see your career leaning favourably", "as I read it", "I’m reading …" (curly apostrophe), "MY career …".

The spec note says "a bare 'I' (the writer's) stays a warning as before". For "I" before a modal or "have", it is now a
refusal. The writer loop answers 8 of the 20 varied first questions, every greeting among them (L1). It now loses
those sentences and retries them, and no writer measurement (DoD 7) or timing was re-run. No benchmark row covers the
new refusal (DoD 5: Ray's "In my chart" paragraph is an audited miss). `checker_bench.jsonl` has 187 rows, unchanged
by this batch.

**Why it matters.** It changes the conversation's refusals without the evidence the definition of done asks for, and
it is inconsistent ("I see" passes, "I can see" fails).

**Suggested fix.** Apply it to the reading's paragraphs and the client's layer only, or narrow it to the
client-perspective phrases ("my chart", "my career", "my 10th house", "I have <planet>"). Add bench rows both ways and
read the curly apostrophe.

## M4. Repetition the shape was meant to remove: the vocation section restates the lean's placements, and one sentence is said once per area

**Where.** `plan._vocation_items` (`plan.py:407-448`) beside the general section's families. `shape`
(`conversation.py:1022-1062`) and `variant_of` (`:1113`: one variant per signature per session). Multi-area helps
(`shape`, `n > 1`: one help per area, chosen per area).

**What is wrong.** Reproduced in the frozen fixture and the scan:
- The three-part answer (frozen, draft off) says Mars in Capricorn exalted twice (the varga help, then
  `vocation.d10`), the Sun in Aquarius in the 10th twice, and Saturn in Taurus in the 1st twice. In the scan, 60 of 150
  three-part answers restate a general-section placement in the vocation section. Some name one placement three times
  (`('the Sun', 'Sagittarius') x3` on SYN-000007).
- When the 10th's ruler sits in the 10th, `vocation.tenth` and `vocation.in_tenth` say it twice in a row ("its ruler
  Jupiter is placed in Sagittarius, in your 10th house. In the house of work, your 10th, … you have Jupiter.").
  12 of 150 "which field" answers.
- Two planets' weaknesses in one area get the same meaning variant with only the planet changed ("When Saturn is held
  back like this, texts traditionally read the promise of your career as slow …" followed by "When the Sun is held
  back like this, …"). 73 draft-on answers.
- Over several areas, the panchanga help is one chart-wide fact said once per area, word for word but the area
  ("Looking at your career, the Moon, which rules the lunar day …", "Looking at marriage, the Moon, which rules the
  lunar day …", "Looking at money, …"). 130 answers. So are the three verdict sentences of one variant ("This chart
  puts no special weight on X, though what it does show leans favourably." × 3).

The spec note records the first case as found and not fixed, "because its meaning (the kinds of work) hangs on it".
With draft meanings off, which is every outside client's setting, there is no meaning to hang, and the repetition has
no reason.

**Why it matters.** Decision 2 aims at an answer a person would give, and Ray's complaint was four sentences in a row
on one planet. These answers still repeat a placement two or three times.

**Suggested fix.** Leave out a vocation fact whose placement a kept sentence already states (say "already named above"
in `held`). Merge `tenth` and `in_tenth` when the ruler is in the 10th. Over several areas, say a chart-wide help once
for the areas it touches. Vary the variant by item, not by signature alone.

## M5. The common ways of asking "which field" are not the ask vocation

**Where.** `conversation.py:539-552` (`VOCATION`).

**What is wrong.** These route to career with the kind `goes`, so they get the lean and no vocation section:
- "which career is best for me", "which career should I choose", "what job suits me", "which job is right for me",
  "best career for me", "what kind of job"
- "what is the best field for me", "my field of work", "What is my vocation", "what is my profession"
- "IT or government job?", "job karu ya business", "business karu ya job", "कौन सा करियर अच्छा है"

"what should I do for a living", "which industry" and "doctor or engineer?" name no area and go to the writer loop.
The decision's list is "which field", "which line", "what kind of work", "business or job (and their Hinglish and
Devanagari forms)", and "which career" is the most common form of all.

**Why it matters.** The batch was built to answer "which field". Asked in its most common words, it is still answered
as "how does it go".

**Suggested fix.** Add "which/what/best career|job|profession", "suits me", "<x> karu ya <y>", "कौन सा करियर", and a
part that names "vocation", "profession" or "field" as its subject.

## M6. With draft meanings off, "which field will I work in" names no field and does not say so

**Where.** `conversation.compose` and `plan._vocation_items`. No cannot-give or "awaits the astrologer" line exists
for the vocation ask (`plan.CANNOT_GIVE`).

**What is wrong.** The outside client's answer (frozen fixture, draft off) is four placements:

> Your 10th house, the house of work and your career, is in Aquarius, and its ruler, Saturn, sits in Taurus in your 1st
> house. In your 10th house, the house of work, you have the Sun, … In the divisional chart for work, … Mars is in
> Capricorn, exalted, … In your 10th house, the house of work, you have Mercury, …

None names a kind of work, and nothing says that the kinds of work are not given yet. In the scan the vocation answer
is 1 to 4 sentences with draft off; one sentence when the 10th is empty and the D10 has no strong planet. The decision
makes the meaning rows draft. It does not say the answer should leave the client to guess why their question went
unanswered.

**Why it matters.** This is the first live complaint ("it says nothing on 'which field'") repeated in a different
form. It is what every outside client will see until the astrologer approves nine rows.

**Suggested fix.** One fixed line after the placements while no `vocation.works` row is approved, in the decision 1
spirit ("A chart points to the kinds of work through these placements; what each means for your work is not yet given
here"). Or ask the astrologer to approve those nine rows first.

## M7. A greeting or thanks after a turn now gets an unasked reading of the top areas from the writer

**Where.** `conversation.py:97` (`GREETING`) and `route_turn` (`:444`): a greeting is never a follow-up, so its areas
are `top_areas`, `areas_from == "top"`, and `composes()` is false.

**What is wrong.** On the reference chart, "thanks", "ok" and "thank you so much" after "how is my career" route to
career, marriage, and debts and enemies, and go to the writer loop (a model call). The fix for "hi after a health turn
answered as a health follow-up" replaced one unasked answer with another, and it now costs a writer call per "thanks".
The spec note reads this as "read as a first message is". The first-message "hi" has the same fault, and is one of the
eight questions the composer's share leaves to the writer.

**Why it matters.** A client who says thanks gets a reading of their debts and enemies. In a conversation that is
worse than repeating the last answer.

**Suggested fix.** A greeting or thanks after a turn gets a fixed one-line reply with no model call, and a first-turn
"hi" a fixed invitation to ask.

---

## L1. In a timing section the period comes before the lean, and a single-area part is cut as if the answer had several areas

**Where.** `compose` (`conversation.py:1226-1234`: every sentence of a timing section has the period's rank, so the
plan's order decides, and the plan is in `route.areas` order, AREA_VOCAB's, not the part's); `shape` (`:1036`: `n`
counts every area in the answer).

**Reproduced.** "when will I marry and how is my career" (the spec note's own example) gives the cannot-give line,
then "Until November 2028 you are in the period of Jupiter … have a hand in your career and marriage", then "For
marriage, most of what the chart shows agrees …". The period comes before marriage's lean and names career inside
marriage's section. The career part, the only `goes` part, gets the lean, one help and one hard sentence, because
the answer has two areas.

## L2. Several areas asked "when": the caveat and an area-less stretch sentence are said once per area

`stretch.caveat.*` is said twice in all 300 scan answers to "when will my career and money improve". The "least
favourable one" variant, which names no area, appears twice word for word when the windows coincide (12 answers),
and so does "This depends in part on the exact birth time." (16). This is inherited (the parent commit does the
same), but the shape's "the period is said once" did not extend to the caveat.

## L3. The Latin-script "aur" before a noun is not split either

`PART_SPLIT` (`conversation.py:522`) splits at "aur" only before a question word, so "meri shaadi kab hogi aur naukri
kaisi rahegi" is one `when` part over both areas. "naukri kaisi rahegi" (how the job goes) gets career's lean and
stretches, with no help or hard sentence. The spec note's "Found and not fixed" names only the Devanagari "और".

## L4. The reading's default areas are not filled as the conversation's are

`narrate.default_top` (`narrate.py:860`) drops longevity, health and synastry from `scored.top` but does not refill
it, while `conversation.top_areas` fills to three. The reference chart's reading now offers career and marriage only
(the test was updated to two). A chart whose top is two of the three left-out areas gets one area, and a chart whose
top is all three would get none. Decision 5 says "as the conversation's do".

## L5. The day a turn is read at: the review page's sheets and the minor flag stay at another day

`api.py:975-990`: the session review page builds its sheets once at `session_day` (today), beside turns each
answered at its own `as_of`. A reviewer reads turn 1's sentences against today's period. `api.py:696`: `minor` is
computed at the conversation's first day and never again, though a conversation now lives 180 days on the moving
date. `session_day` uses the server's local date (UTC on Fly), not the client's: an Indian client's turn just after
midnight IST is read at the day before.

## L6. Draft meanings: nothing outside /health checks the flag

The DoD line is right, but `docs/deploy.md`, `docker-compose.yml`, `fly.toml` and `scripts/smoke.py` never mention
`JYOTISH_SHOW_DRAFT_MEANINGS` or `draft_meanings`. An operator deploying for an outside client learns of it only by
reading the DoD. A smoke check that fails when `draft_meanings` is true on a client deployment would make the rule
hold by itself.

## L7. Smaller wordings and edges

- `PANCHANGA_ROLE` (`narrate.py`): "the Moon, which rules the weekday" and "which rules the day's combined motion of
  the Sun and Moon" read as general statements. "The weekday you were born on" and "the nitya yoga of your birth
  day, the Sun's and Moon's combined motion" are what the facts state.
- `_vocation_items` takes the 10th's sign by whole sign (`asc + 9`) but "planets in the 10th" from `bodies[p].house`,
  which is the Sripati bhava under `Meta.house_system = "sripati"`. The two disagree there, though not under the
  default.
- "mujhe kaun sa kaam karna chahiye", one of the decision's Hinglish forms, also routes to debts and enemies:
  "karna" is one letter from "karza" (`_near`). The vocabulary is inherited, but the new phrase is what reaches it. Add
  "karna", "karni", "karne" to `NOT_A_TYPO`.
- "which field should I study" is career with the ask vocation and intellect's lean is held: a student is answered
  with the 10th house.

## Tests

No test was weakened rather than updated to a decision. Each changed assertion says why: the kinds now in the order
asked, `weakness.planet` replacing the three per-kind signatures, the reading's areas without longevity, and in
`test_m3`/`test_m4` "repeats nothing" replacing a sentence count the shape made meaningless. Gaps that let the
findings above through:
- `test_2_tell_me_more_…` checks one "tell me more" on one chart (H2).
- `test_3_which_field_…` and `test_4_leaving_…` are positives only. No message that must *not* be vocation or change
  is tested (H1, H3, M5).
- `test_2_over_random_charts_…` uses `compute`, so the stability line never enters the eight. The scan, with
  `assess`, found no single-area answer over eight, so the shape itself holds.
- `test_5_a_paragraph_in_the_clients_first_person_is_refused` has no writer-voice negatives (M3).

## What holds

Decision 1's kinds and the one cannot-give line, with every combination it can make drafted and placed at its part.
Decision 2's eight per area: no single-area answer over eight in 4,200 answers. "Why?" after a shaped answer gives
the held reasons. The vocation items state only what the engine computes (checked against the chart on 60 charts by
the batch, and on 150 in the scan). No karmajiva rule, no change-of-job rule. GET / opens the conversation. /health
reports the flag. A turn is read at the day it is asked and a reviewer's date stays fixed (`test_w4`, and
`as_of_fixed` requires the reviewer's token at `api.py:672`). The varga and panchanga wordings: no "ruler(s) of the
day" in the scan, no literal slot, double space or lower-case start.
