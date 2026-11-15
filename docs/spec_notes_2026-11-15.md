# Notes for the living doc, 2026-11-15

SPEC.md is the export of the living doc and is never edited directly (CLAUDE.md). These record the build of "The
layered answer" (SPEC Layer 8, rev 134, set 2026-11-15 before the build), one commit per step, against the
paragraph as written. The paragraph was read from the living doc; Ray's re-export of rev 134 (0134da3) landed
during the build.

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
2. **The sentence bank** (`jyotish.bank`, `data/bank/*.yaml`, `data/bank/bank.schema.json`). A row has:
   - its signature, its kind (`fact`, or `meaning` for one area, signed `<signature>@<area>`), its slots and three
     variants;
   - a source (required for a meaning row: the rule's citation);
   - the model and date that drafted it;
   - its status (`draft`, or `approved` with who and when), and `rewritten_by` for the astrologer's own words;
   - the gate checker's verdicts on its fact variants (`checks`).

   The loader validates the schema and every row at load time, as the rule library does: a slot a variant uses but
   the row does not declare, a broken slot, a meaning row with no source or area, a fact row naming an area, an
   approval with no name or date, or a second row for one signature. Every variant, its slots filled with sample
   values, must pass the never-show list, the client's-word rules for a conversation and the tier words; a row
   that does not is a load error. The bank's version is a hash of its files.

   `jyotish bank coverage` (`bank.coverage`) plans 1,000 random synthetic charts (`synthetic_cohort.births`) over
   every area, every question kind and a "when" turn. It counts the share of plan items that find a fact row whose
   slots the item fills, by part, the meaning rows' share among the rules and weaknesses, the approved share, and
   the signatures most often missing. `jyotish bank check` prints every row that cannot stand. The image ships
   `data/bank` beside `rules/`.

   *Readings settled:*
   - **Client-word checks on every variant.** These are refusals at load time, not warnings as in a live turn: a
     bank row is written once and shown to every later client, so it is held to the stricter rule.
   - **Meaning rows.** They are drafted for the rules and the hidden weaknesses, per area. A family's lean is a
     fact only.
3. **The drafted bank** (`scripts/draft_bank.py`; `data/bank/*.yaml`, 126 rows, all `draft`; `docs/bank_draft_2026-11-15.json`).
   - **Which signatures.** Those that the areas career, marriage and wealth produce, over 300 random charts and the
     reference chart, with every question kind and a "when" turn, plus every opening, period and stretch. A fact
     row is drafted for each, and a meaning row per area for each rule and hidden weakness of the three areas: 131
     signatures in all.
   - **The drafting.** claude-sonnet-5-5, on the anthropic backend, drafts about ten rows a call. For a fact row it
     is given the engine's own sentence as what the row says; for a meaning row, the rule's names, glossary,
     themes, outcomes and citation (its `source`). Each variant is held to `bank.row_errors`, and a refused row is
     redrafted once with the reasons.
   - **The check.** Every fact variant, filled with a real chart's values, was checked once by the gate checker
     (GLM-5.3-Flash at temperature 0) against the item's facts and the engine's sentence. A row with an
     unsupported variant was redrafted once and checked again; if it still failed it was left out. The verdicts
     are on the row (`checks`).
   - **Cost.** The expected cost was printed before each run and was under USD 2 each time (1.61, 0.92 and 0.51,
     worst case). Spent: USD 1.80 over three runs (drafting 1.45, checking 0.36).

   **The three runs.**
   1. 71 rows written, 60 left out. Most were refused because the facts the checker was given named no area, its
      houses, its main house or a dignity's meaning.
   2. Every plan item's facts now carry `about` (`plan.about`: the area, its houses from the rising sign, its main
      house and that house's lord, its significators), and the check is given the engine's dignity words and the
      glossary. 27 rows written, 33 left out, mostly rule rows with a bare Sanskrit name in one variant.
   3. A rule's slot `{named}` gives its name with its condition in plain words (`plan.RULE_PLAIN`, from each rule's
      `when`), and the engine's fallback sentence uses it. 28 rows written, 5 left out.

   **Coverage.** On 1,000 random synthetic charts (every area, every question kind, a "when" turn), 99.7% of plan
   items find a fact row whose slots they fill. Every part is at 100% except the rules, at 94.7%. Meaning rows exist
   for 24% of the rule and weakness items, the three areas drafted first.

   **What the astrologer must settle.** The 5 rows left out are Gaja Kesari in its BPHS form (four signatures) and
   Neecha Bhanga reduced. The checker refused them because `RULE_PLAIN` for those two rules does not say what their
   glossary entries say: the glossary defines Gaja Kesari from the Moon, while the rule's BPHS form counts from the
   ascendant or the Moon. Until the plain phrase and the glossary agree, those items fall back to the engine's
   sentence, which carries the same phrase.

   *Readings settled:*
   - **"Batch where possible".** About ten signatures to a call, rather than the Message Batches API: the gate
     checker is on DeepInfra, and the drafting wanted the redraft loop within one run.
   - **The cost limit.** USD 2 is applied per run, to the printed estimate.
4. **The composer** (`conversation.compose`, `answer_turn`).
   - **What it does.** It fills the plan from the bank: for each item, its fact row's variant with the chart's
     values, else the engine's sentence. After a rule or a weakness comes its meaning row for the area, where the
     row is approved, or where JYOTISH_SHOW_DRAFT_MEANINGS is on; no public client sees an unapproved meaning.
   - **Paragraphs.** Three short paragraphs, then the timing: the answer as asked (openings, verdict, stability),
     what helps (families, rules), what is hard (families, weaknesses), then the period now and the stretches. A
     question asking what is against puts the hard paragraph before what helps.
   - **The variant.** It is `sha256(session | signature) mod 3`. One client's answers vary across signatures and
     stay the same for a signature from turn to turn.
   - **A follow-up.** One that carries the last turn's areas repeats nothing, the stretches' caveat excepted. A
     why or how turn with nothing new says so.
   - **In `answer_turn`.** It is the default for every turn the route placed (named, carried or weakest areas).
     A question the route could not place keeps the writer loop, as does `JYOTISH_LAYERED=0`. No model is called:
     the turn's document records the plan, the composed sentences with their rows, and the bank's version.

   *Readings settled:*
   - **A row is used only when the item fills its slots and the gate checker supported every variant.** Anything
     else falls back to the engine's sentence.
   - **"A question the route cannot place".** A turn whose areas the route took from the chart's top areas by
     default (`areas_from == "top"`).
   - **The test suite.** It runs with JYOTISH_LAYERED=0 (tests/conftest.py), so the conversation's earlier tests
     still drive the writer loop that the service keeps. tests/test_layered.py turns the composer on and tests the
     default with the variable unset.
   - **Fixes the frozen texts showed.**
     - A verb right after a slot now agrees with the slot's value (`bank.agree`): "the Sun and Mercury sit",
       "Jupiter has a hand".
     - A row is not filled where the item leaves one of its slots empty.
     - The composed path makes the payload when it is given none, so the stretches have their dates.
     - A turn over several areas says each rule once, naming every area it bears on. It says each hidden weakness
       once, and the period once with every area its lords touch (`plan._once`).
   - **Frozen.** The seven-turn conversation of tests/test_conversation.py is frozen composed, with the bank version,
     in tests/fixtures/layered_seven_turns.json. Six turns are composed and the death question gets its fixed reply.

   *Open, for the review:*
   - **Length.** The weakest-areas turn ("what are the challanges in my life") over three areas is 25 sentences,
     not three short paragraphs.
   - **A second verb.** A coordinated verb after the first is not made to agree ("the Sun and Mercury sit … and
     forms").
5. **The polisher** (`conversation.polish`; JYOTISH_POLISH, off by default).
   - **The calls.** One claude-haiku-5-5 call at effort low rewrites the composed answer for flow. Its stable
     prefix (`POLISH_SYSTEM`, about 750 tokens, over Haiku 5.5's 512-token minimum) is sent with
     `cache_control`. Then one call to the gate checker asks whether every proposition of the polished text is in
     the composed text.
   - **When the composed text is shown instead.** When the checker finds a proposition the composed text does not
     state, or when the polished text carries a never-show, client or tier word; markdown and HTML are taken off
     first. Either call failing also shows the composed text.
   - **Prices.** The polisher's tokens, cache reads included, are priced in `jyotish.costs` and counted in a
     turn's ledger total, with its backend under `backends`. Haiku 5.5's cache reads are now priced at 0.1 times
     input; the bake-off of 2026-11-02 priced them at input for want of the figure.
