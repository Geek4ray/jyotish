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
