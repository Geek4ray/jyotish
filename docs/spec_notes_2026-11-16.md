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
