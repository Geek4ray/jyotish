# Notes for the living doc, 2026-11-15

SPEC.md is the export of the living doc and is never edited directly (CLAUDE.md). These record the build of "The
layered answer" (SPEC Layer 8, rev 134, set 2026-11-15 before the build), one commit per step, against the
paragraph as written. SPEC.md in the repository is still the rev 132 export; the paragraph was read from the living
doc.

## The layered answer, step by step

1. **The answer plan** (`jyotish.plan`, `conversation.plan_turn`). For a turn's routed areas, direction ("both" on
   a why or how turn, as the engine's answer reads it) and question kinds, the plan lists what the answer says, each
   item with a bank signature, slots, the finding tags it rests on, the facts it states, the engine's own sentence
   and its sheet notes. What it leaves out is listed with the reason (`left_out`). Per area, in order:
   - the opening per question kind (and the weakest-areas opener);
   - the verdict line, and the stability line where the area depends on the birth time;
   - the two or three families that help and the one or two that are hard;
   - every fired cited rule of the area, full or with its reductions;
   - the main lord's and main significator's hidden weaknesses;
   - the Vimshottari period running at the turn's date;
   - the stretches on a "when" turn.

   On the reference chart the career plan holds Budhaditya (reduced: Mercury in a feeble state), the
   Kendra-Trikona raja yoga, Ruchaka with its three reductions (Saturn's aspect, an unhelpful star from the Moon, a
   house that drains it) and Saturn's three hidden weaknesses: marana karaka sthana in the 1st house, a Mrita
   avastha, and a Shadbala ratio of 0.69. The sample worksheet's two faults are now plan items.

   *Readings settled:*
   - **"By the strongest family terms".** A family's term in the area's score (`AreaScore.terms`). The arudha and KP
     votes have no term, so they rank by their vote times their family weight, the claim confidence
     `narrate.findings` gives them. Helps take the three strongest positive families, hard the two most negative.
   - **"Every fired cited rule".** A non-draft rule fire that is stable to the birth time (stability at least 0.5,
     as `narrate.findings` splits them). The draft placements, the chains and the time-unstable findings are left
     out, each with its reason.
   - **The main lord and significator.** The lord of the area's first house from the rising sign (`scoring.AREAS`),
     and the area's first karaka (the payload's `main_karaka`). One planet that is both is named once with both
     roles.
   - **Reductions in the client's words.** `plan.REDUCTION_PLAIN` maps each modifier condition with a scale under 1
     to a plain phrase. A rule whose reduction has no phrase yet stays out of the answer and is listed in
     `left_out`, rather than reaching the client in the engine's words.
   - **The engine sentence for a rule, a weakness and a period.** `engine_reading` had none, so the plan writes one
     in code. It is the fallback when no bank row is found, and it passes the never-show list on four charts.
