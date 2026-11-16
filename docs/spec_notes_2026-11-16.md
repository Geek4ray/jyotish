# Spec notes, 2026-11-16: the shaped answer

SPEC Layer 8 rev 136, "The shaped answer (decided 2026-11-16)": six decisions, built one commit each on the reference
chart first; tests in tests/test_shaped.py. These notes say how each decision was read where the SPEC leaves a choice,
and what was measured. Nothing here is a promise about outcomes.

## The failing case, frozen first

`tests/fixtures/shaped_three_parts.json` holds, on the reference chart as of 2026-11-16 with every bank row's first
variant, the three-part question Ray asked on the deployed service and the two single questions inside it, with draft
meanings off and on:

- "How will my career go, which field will i work in, when will i leave my current job"
- "which field will i work in"
- "when will i leave my current job"

Before any decision (bank `default_bank().version` of that commit): `kinds_of` read the first as `['yes_no', 'when']`;
"which field will i work in" routed to career, marriage and debts and enemies (`areas_from` top), so the composer did
not answer it; the composed answer to the first was 17 sentences (24 with draft meanings on), opened with two lines of
what a chart cannot give and had four sentences in a row on weaknesses, three of them Saturn's (six with draft meanings
on, each fact followed by its own "Texts link ..." or "tradition reads ..." sentence). Every decision's commit
re-records the fixture, so its diff is what the decision changed.

## 1. Parts

`conversation.parts_of` splits a message at a comma, semicolon, question or exclamation mark, a full stop or the danda,
and at "and", "but", "also", "aur" or "or" only where a question word follows, so "your career and marriage" stays one
ask and "whan and how" is two. `kind_of` gives each part one kind, read in this order: why (a "why", or a "how" that
asks what in the chart does it, as `asks_how` already read it), change, vocation, when, amount, yes_no, goes. Yes or no
only where the part opens on an auxiliary (will, shall, would, can, could, should, may, might, must, am, is, are, was,
were, do, does, did, have, has; "kya", "क्या") or closes on "hoga" and its forms; "how will" and "which" are not, and
"when will I marry" is now a when question (it was yes_no and when). The route keeps the parts (`Route.parts`, each
`{kind, areas}`, a part's areas the ones it names, else the route's), and a stored answer's key includes them.
`kinds_of` is the parts' kinds in the order asked, each once, with "when" or "why" added where the whole message's
route reads one that no part did.

Read here: Devanagari is split at "और" only where a Hindi question word follows; "मेरी शादी कब होगी और नौकरी कैसी
रहेगी" stays one part (when, over both areas). The kinds' order changed from narrate.OPENING's to the order asked; the
writer loop's engine reading still opens on narrate.OPENING's lines for the kinds it knows (amount, yes_no, when, why),
so a "goes", "vocation" or "change" kind adds none there.

**One cannot-give line.** `plan.cannot_give` gives the kinds that need one (amount, yes_no, when, change; an amount line
also says no yes or no, a change line also says no date), and the plan makes one opening item, `opening.<kinds joined
by dots>`, about the areas of the parts that need it. Its sentence opens the first section with such a part: the
answer's first line when that is the first part, else the head of that part's section (the three-part question's line
is at its change of job, after the career's lean). Read here: "opening line" was taken as "the one line of what a
chart cannot give"; placing it at the part that needs it keeps "at most one" and does not open an answer on a caveat
the first part never asked for. Five rows were drafted for the new combinations (`opening.change`, `.yes_no.when`,
`.amount.when`, `.yes_no.change`, `.amount.change`) with scripts/draft_bank.py `--only opening.` (Sonnet 5.5; every
variant checked and supported by the gate checker; USD 0.019), status draft.

**The parts in order.** The composer (`compose`) puts each sentence in a section, one per kind of ask, in the order
asked: general (goes, yes_no, amount: the lean, what helps, what is hard), vocation, timing (when, change: the period
now and the stretches) and why (the reasons, after "Here is what in your chart lies behind it"). An item goes to the
first section in its order of preference (`PLACES`) that the message asks and whose areas hold its area: the lean to
general, else why, else timing (a when-only question is its lean and its timing alone); the period to timing, else
general; the stretches to timing. An item no section takes is held (`composed.held`, by key) for a later turn. So "when
will I marry and how is my career" answers marriage's timing first, then career, and "whan and how" now gives the
stretches before saying nothing new lies behind them (the seven-turn fixture's turn 7; turn 3's "when?" is now one
paragraph).

## 2. Shape

`conversation.shape` cuts the placed sentences to the answer's shape before they are ordered. For one area, at most
`SHAPE` (8) facts: the lean (with the stability line where the area depends on the birth time), the two things that
help most (`HELPS_SHAPE`; the families as the plan ranks them by percentile, then the cited rules), what is hard (the
hardest families, then one sentence per planet), the period now, and the stretches where a part asks when. Where the
eight are short the hard part keeps one sentence and the helps give way first (the three-part question: the lean, two
helps, Saturn, the period and the three stretch sentences). A question about what is against gives the hard part
first and as much room as the eight leave after one help. Read here, since the SPEC sets the shape for one area only:
over several areas each area gives its lean, one help and one hard sentence (a question about what is against, its
hard sentence alone) and the period is said once; "what are the challanges in my life" went from 27 sentences to 8.
The cannot-give line and a vocation section are outside the eight.

Everything the shape leaves out is in `composed.held` with its key. "Tell me more" is a short follow-up, so it carries
the areas and leaves out every key said (the layered answer's M4), and the shape is then made from what is left: the
held helps, the cited rules and the other weaknesses come next (`test_2_tell_me_more_...`). A "why?" after a shaped
answer now gives the reasons it held back, where it said there was nothing new before (the seven-turn fixture's turn 7,
and the review's M3 and M4 tests, which now check that nothing said is said again rather than a count).

**One sentence per planet.** `plan._weakness_items` makes one item per planet, `weakness.planet`, its weaknesses in one
list slot `{weaknesses}` (`WEAKNESS_PLAIN`: "sits in your 1st house, which drains it", "is in a feeble state by its
degree in Taurus", "has less strength than it needs to give fully what it promises"), with every weakness's facts.
The per-kind rows (`weakness.mks`, `.mrita`, `.low_strength` and their nine meaning rows) composed nothing any more and
were removed; with them goes the row that composed "no matter what Taurus says" (the engine's own "whatever the sign
says" is gone too). The new fact row and its three meaning rows (`weakness.planet@career|marriage|wealth`) were drafted
with `--only weakness.`; the fact row's first variant (which named the planet twice) and the meaning rows' variants
(one repeated the whole list, two did not name the planet, which the layered review's M9 asked of these rows) were
rewritten by Opus and say so in `drafted_by`; the fact row was rechecked on each slot shape (12 checks, all
supported; USD 0.032 drafting and checking in all). Read here: a hard family about a planet that also has hidden
weaknesses is still its own sentence; "one sentence per planet" was read as one sentence for a planet's weaknesses.

**A meaning follows its fact.** One meaning a fact (a rule said for several areas gives its first area's), directly
after it, and a meaning closes its paragraph, so no paragraph attributes to the tradition twice. Read here: "joins"
was not done by splicing two rows into one sentence, since a verdict on a sentence is a verdict on one row; the
meanings are outside the eight, so with draft meanings on the three-part question is 10 sentences (24 before).

`compose(shaped=False)` composes every sentence the sections take, every meaning of a fact: the tests of a row's
variants, refusals and verdicts use it, and since the measurement commit so does scripts/composed_check.py (the worksheet tests lift `SHAPE` in their fixture), since they
are tests of the rows, not of the shape.

## 3. Vocation

**The ask.** `AREA_VOCAB` gives career the words field, fields, sector, sectors, occupation, vocation, profession(s),
kshetra, pesha, vyavsay (and its spellings), क्षेत्र, पेशा, व्यवसाय, धंधा; `VOCATION` reads the phrases ("which field",
"which line", "what kind of work", "work in", "business or job", "line of work"; "kaun sa field", "kis line", "kya
kaam", "naukri ya business"; "कौन सा काम", "किस क्षेत्र", "नौकरी या व्यापार"), and a message it matches names career
(`areas_of`) and its part is the ask `vocation`. "which field will i work in" is now career, named, and composed.

**The items** (`plan._vocation_items`), only what the engine computes, on a vocation part about career: the 10th house
from the rising sign (its sign, its ruler, the ruler's sign and house), each planet in the 10th, and each of the seven
planets the D10 holds in its own or exalted sign (`scoring.varga_dignity_word`, the varga vote's words; a varga has
no degree, so moolatrikona is not read). In that order of preference, the first of each kind before the second of
any; the vocation section keeps four (`VOCATION_SHAPE`) and holds the rest. Each item's meaning is its planet's kinds
of work, `vocation.works.<planet>@career`, said once in an answer though the planet is the 10th's ruler and strong in
the D10. The items carry no vote or rule tag and nothing of them weighs in scoring.

**Karmajiva left out.** The classical karmajiva lord (the ruler of the navamsa sign the 10th lord occupies, counted
from the stronger of the rising sign, the Moon and the Sun) was not built: I did not read the method in a named
edition, and the editions differ on which point it is counted from. It needs the astrologer, or a verse read in
Brihat Jataka 10 or Phaladeepika 5 in a named translation, before it is a rule; then it is `draft` and weighs nothing
until its verse is read, as every placement is.

**The rows.** Three fact rows (`vocation.tenth`, `.in_tenth`, `.d10`) and nine meaning rows (one per planet, the nodes
included) were drafted with `--only vocation.` and checked as the others were (every fact variant on each slot shape,
all supported); Saturn's first draft said "long-term", refused for "term", and was redrafted alone. The meaning rows'
source is "Brihat Jataka 10 (Karmajiva), the kinds of livelihood linked with each planet; the verse not yet read in a
named edition": the drafting model wrote the kinds of work from the tradition as it knows it, and nobody has read them
against the verse. All twelve are draft. USD 0.085 drafting and checking.

Read here: the vocation section is its own; a placement the career's lean already named (the Sun in the 10th as the
main significator, Mars exalted in the D10 as the varga's lean) is named again there, because its meaning (the kinds
of work) hangs on it. With draft meanings off the vocation answer is the four placements only, with no kind of work,
until the astrologer approves the meaning rows.

The words are tolerant of spelling as the rest of the vocabulary is (`_near`), so "vacation" read as "vocation" and a
vacation became a career question (the routing probe of the chat review caught it): "vacation", "yield", "fiend" and
"vector" and their plurals are in `NOT_A_TYPO`.

## 4. A change of job

`CHANGE` reads leaving, quitting, changing, switching or resigning a job, work, company or employer (and "job change",
"career switch"), in Hinglish ("naukri kab chhodunga", "job badalni", "meri job kab chhutegi", "company switch karu")
and in Devanagari ("नौकरी छोड़", "नौकरी बदल", "जॉब छोड़"). Its part is the ask `change`, a message it matches names
career, and the route gives the stretches (`Route.when`) whether or not the message says "when". The answer is the
cannot-give line for a change (`opening.change`: "a chart cannot give a date for leaving or changing a job"), then the
period now and the stretches: the timing section of a change takes no lean, where a when-only question's does
(`_section_for`). Asked beside how the career goes, the lean is the general part's and the change's line opens its own
part. No rule for a change of job was added (`test_4_no_rule_for_a_change_of_job_is_added`); the stretches are the
career's timing windows as before, and the caveat closing them says they are not a prediction of when you will act.

## 5. Which page is the client's

GET / serves `web/chat.html`, the conversation (`api.client_entry`); the reading's form, which was `web/index.html`, is
`web/readings.html`, the astrologer's and the reviewer's, with the reading, timing and review pages as before. The
site's navigation (`web/js/chrome.js`) opens the conversation from the brand and a "Conversation" link, and lists
"Readings" for the form; the conversation's own brand links to /. The Playwright tests that drive the form open
/readings.html.

**The reading's default areas.** `narrate.default_top` is the chart's top areas without longevity, health and synastry
(`conversation.NOT_DEFAULT`); the reading's router falls back to it, the service adds it to the asked areas (where
health was offered beside career on Ray's first three-part reading), and the engine's own summary names it. An area the
question names is the question's, whatever it is.

**The client's first person.** `client.CLIENT_FIRST_PERSON` ("my", "mine", "myself", and "I" with have, had, am, was,
will, would, can, could, should, need, want, got or feel, or a contraction) is refused in every text held to
`client_errors`: every paragraph at every depth, the client's layer, the curious summary, a reviewer's edit of the
client's words. It is a refusal whatever `WORD_RULES` says; a bare "I" (the writer's) stays a warning as before.

## 6. Draft meanings while there is no outside client

GET /health carries `"draft_meanings"`, true where `JYOTISH_SHOW_DRAFT_MEANINGS` is on (`conversation.show_draft_meanings`:
1, true, yes, on), so whoever runs a deployment sees at a glance whether a client is reading unapproved meaning rows.
docs/definition_of_done.md gains, beside its two standing rules, that the flag is off on every deployment an outside
client can reach and /health says `"draft_meanings": false` there; Ray's and the astrologer's own deployment may run with
it on while the meaning rows are drafts.

## The wordings left open at rev 135

**The varga sentence names the divisional chart it rests on.** `family.varga.*` said "the divisional chart for <area>"
of the row of greatest score, which could be the area's second varga (the D16 of wealth, the D9 of fortune) or the
birth chart itself (the D1 of personality and of the mind), which the layered answer's recheck refused once.
`narrate.varga_row` now takes the row from the area's own divisional chart (the first `scoring.AREAS` lists, the birth
chart excepted) where one lies on the vote's side, else the row of greatest score; a sentence on another chart says
"the divisional charts read for <area> lean ...; in <that chart, in plain words>, <planet> falls in ..."
(`narrate.VARGA_PLAIN`, `family.varga.for.other` / `.against.other` with a `{varga}` slot), in the engine's sentence and
the bank's. The two new rows were drafted with `--only family.varga.` (draft_bank.py now gathers every area's fact
signatures, since `.other` arises outside career, marriage and wealth; meaning rows stay those three areas') and
checked on four slot shapes each, all supported. A test over 40 random charts and every area holds every own-chart
sentence to the area's own varga and every other one to its named chart.

**Each ruler of the panchanga named with what it rules.** The panchanga vote's planets are the lords of the tithi, the
weekday (vara), the nakshatra and the nitya yoga of the birth (scoring); the sentence called them all "the rulers of the
day you were born", which only the weekday's lord is (on the reference chart Mars is the lord of the tithi and the
nakshatra, the Moon of the weekday, a Monday). `narrate.panchanga_ruled` names each with what it rules
(`PANCHANGA_ROLE`: the lunar day, the weekday, your birth star, the day's combined motion of the Sun and Moon), and the
plan's slot is `{ruled}` for several, `{ruler}` for one, with no bare `{planets}`; each role's plain meaning is in the
item's facts, which the checker reads (`panchanga_roles`). The four rows were removed and redrafted with `--only
family.panchanga.`: the first draft was refused for want of those facts, the second stood but for one row redrafted
once more, and two variants that wanted a comma after `{ruled}` were mended by Opus and rechecked; one variant ("the
planets that rule these parts of your birth day") the recheck refused as ambiguous, so it is never shown. `row_errors`
now refuses "ruler(s) of the day" in any row.

**A greeting is not a follow-up.** A short message with neither an area nor a direction is carried as a follow-up
(SPEC Layer 8, decided after the review of chat v1), so "hi" or "thanks" after a health turn was answered as a health
follow-up. `conversation.GREETING` (hi, hello, hey, namaste, namaskar, good morning and its kin, thanks, thank you, ok,
okay, shukriya, dhanyavad, नमस्ते, धन्यवाद, with "there", "ji", "so much" or "a lot" after them) is never carried: it is
read as a first message is (the chart's top areas, the writer loop). Read here: only greetings, thanks and a bare "ok"
were taken out; "what should I know" after a turn is still a follow-up under the SPEC's rule.

## The day a turn is read at

GET /sessions/current returned `as_of` 2026-11-01 on 2026-11-16 for a conversation begun on 1 November, and it was not
only the field: every turn was answered as of the session's `as_of` (`api.run_turn` read `srow.as_of`), so the period
now and the stretches were read at the day the conversation began, and the session's payload was made once for that
day. Now `sessions.as_of_fixed` (Alembic 0009, false for every conversation begun before it) says whether a reviewer
fixed the date (POST /sessions with `as_of` and a reviewer's token); `api.session_day` is that date where fixed, else the
server's today. A turn is read at `session_day` when it runs, the session's payload is made again when the day changes
(`PAYLOADS` holds it with its day), and GET /sessions/{id}, /sessions/current, the session's chart tables and the
conversation review page say that day. A reviewer's rewrite of a turn is checked at the date the turn's own document
records. `test_w4_...`: a conversation begun on 1 November and asked on 16 November is answered as of 16 November (its
document and its plan say so), and one a reviewer fixed at 1 November stays there.

## Measured, not promised

`scripts/shaped_measure.py` (no model call) on the reference chart, run on e66a526 (the head before this batch) and on
the batch's head; both outputs are in docs/shaped_2026-11-16.json. Sentences per answer, with the session's own variants:

| answer | before, draft meanings off | before, on | after, off | after, on |
| --- | --- | --- | --- | --- |
| "what are the challanges in my life" | 27 | 27 | 8 | 8 |
| "and marriage?" | 7 | 8 | 6 | 7 |
| "when?" | 4 | 4 | 4 | 4 |
| "why do you say that?" | 1 | 1 | 2 | 2 |
| "will I die early?" (fixed reply) | 1 | 1 | 1 | 1 |
| "how much money will i earn in my life, will i be rich" | 8 | 9 | 6 | 6 |
| "whan and how" | 5 | 5 | 7 | 8 |
| "How will my career go, which field will i work in, when will i leave my current job" | 17 | 24 | 13 | 18 |
| "which field will i work in" | not composed | not composed | 4 | 8 |
| "when will i leave my current job" | 17 | 24 | 5 | 5 |

The three-part question is 13 sentences with draft meanings off: the lean, two helps, Saturn's one sentence, four
vocation placements, the change's line, the period and three stretch sentences; on, it is 18, each vocation placement
and Saturn's weaknesses followed by a meaning. "why do you say that?" and "whan and how" now give reasons the shaped
answers before them held back, where they said nothing new.

- **The composer's share** of the twenty varied first questions (scripts/evaluate.py `COMPOSER_MESSAGES`): 12 of 20,
  as before. The eight it does not answer name no area ("tell me about my life", "what should I know", "hi", "is
  this a good year for me", "what are my strengths", "why?", "what does my chart say", "what will happen next year")
  and keep the writer loop; none of this batch's decisions places them.
- **Bank coverage** on 1,000 random charts (`bank.coverage`, now with a vocation part): 156,162 of 156,294 plan items
  find a fact row (99.9%); every part 100% but cited rules (96%, the Gaja Kesari BPHS and Neecha Bhanga rows never
  drafted); the meaning share among the items that can take one, 61%. 140 rows, all draft.
- **The composed check on the new rows** (`scripts/composed_check.py --new`, the gate checker GLM-5.3-Flash at
  temperature 0, 120 sentences from 60 random charts, only the rows this batch added or redrafted): 119 of 120 on the
  first run, the refusal `vocation.tenth`'s "the house of work", unstated in its facts; the facts now state the 10th
  as the glossary gives it (da93079) and the run after is 120 of 120 (docs/composed_check_2026-11-16_new.json, USD
  0.048). Reported in the scorecard as `bank.composed_supported.new`, never gated.
- **Drafting and checking cost** of the batch's rows: USD 0.42 in all (docs/bank_draft_2026-11-15.json, the ten runs
  of 2026-11-16 from the openings' draft on), and USD 0.10 for the two composed checks.

Found and not fixed: the Devanagari split at "और" before a noun (decision 1); a hard family about a planet with
hidden weaknesses is its own sentence beside the planet's (decision 2); a vocation placement the lean already named is
named again (decision 3); one `family.panchanga.for.many` variant is refused and never shown; the composer's share is
unchanged; every bank row, the twelve vocation rows among them, still waits for the astrologer, and no person has read
the shaped answer on the client's page (DoD 8).
