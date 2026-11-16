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
supported; USD 0.027 drafting and checking in all). Read here: a hard family about a planet that also has hidden
weaknesses is still its own sentence; "one sentence per planet" was read as one sentence for a planet's weaknesses.

**A meaning follows its fact.** One meaning a fact (a rule said for several areas gives its first area's), directly
after it, and a meaning closes its paragraph, so no paragraph attributes to the tradition twice. Read here: "joins"
was not done by splicing two rows into one sentence, since a verdict on a sentence is a verdict on one row; the
meanings are outside the eight, so with draft meanings on the three-part question is 10 sentences (24 before).

`compose(shaped=False)` composes every sentence the sections take, every meaning of a fact: the composed check and the
tests of a row's variants, refusals and verdicts use it (the worksheet tests lift `SHAPE` in their fixture), since they
are tests of the rows, not of the shape.
