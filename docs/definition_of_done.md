# Definition of done — every change, every step

Set 2026-10-23. "State of the art" here means measured, reviewed and reproducible, not
maximal. A change is done when all ten hold; a prompt to Claude Code ends with "meet
docs/definition_of_done.md", and the independent review checks against this list.

1. **Spec first.** The living doc says what the change is and why before it is built;
   `SPEC.md` is its export and is never edited directly. A note for the doc goes to
   `docs/spec_notes_<date>.md`.
2. **Reference chart first.** Every feature is exercised on the reference chart, and the
   worked example still prints from `jyotish reference`. A rule or placement has a test that
   fires it on a known chart and one that does not.
3. **Conventions are settings.** Any astrological choice (ayanamsa, node, house system,
   year length, karaka scheme, tara scheme, varga method) is a `Meta` setting with its text
   source, and a comment where texts disagree. No silent choice, no placeholder value.
4. **Every number has a home.** A quantity the change adds or moves appears in the scorecard
   with its direction; a change meant to move a number re-runs `scripts/evaluate.py` and
   commits the scorecard; CI is green before the commit is called done.
5. **Every sentence is gated.** A new kind of sentence a reading can contain (claim, synthesis,
   judgement, tradition, paragraph, analysis section) is validated by code, checked by the
   checker where the policy says so, and represented in `tests/fixtures/checker_bench.jsonl`;
   every miss found in an audited reading becomes a benchmark row.
6. **Content is draft until read.** A rule or text effect written from principles is `draft`:
   it fires, is narrated as a fact only, carries no weight, and is promoted only by a named
   reader of the verse on a dated row. No weight changes without a held-out test.
7. **The writer is measured when it changes.** Any change to the writer, its prompt, its
   payload or its settings re-runs `scripts/compare_readings.py` on the reference chart, so
   pass rate, gaps, cost and time are current numbers, recorded in the spec.
8. **Humans try human-facing pages.** A page built for the astrologer, the clerk or the
   client is tried by that person before it is iterated further; their first hour outranks
   the next build.
9. **Independent review before the batch is done.** A fresh session that did not build the
   work reviews it against the spec at the highest effort, writes `docs/review_<date>.md`,
   and its findings are fixed before the next build starts. The reviewer does not fix.
10. **Commit messages claim only what the tests show.** A number quoted in a message comes
    from a committed report at that commit; a feature claimed is one a test exercises.

Two standing rules beside the ten: no content prompt (rules, effects, text) without a
scorecard number it is meant to move, and nothing the product says is ever ahead of the
evidence the validation layer has for it.
