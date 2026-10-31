# Notes for the living doc, 2026-10-31

SPEC.md is the export of the living doc and is never edited directly (CLAUDE.md). These follow
docs/spec_notes_2026-10-26.md (the instant page, the live narration, the gate in use).

The first live reading on the deployed open stack (gpt-oss-120b writing at medium, GLM-5.3-Flash at
temperature 0 checking, depth curious, the reference chart, "How will my career go, and when is the best
time for a job change?") finished with no client paragraph for career or marriage, and the summary was the
engine's own. Four changes follow from it.

## Layer 7 — a lordship named in a list (2026-10-31)

The career paragraph was refused on all three attempts with "[rule:place.l5_h10] on a sentence that names
none of ['5th lord', 'lord of the 5th', 'ruler of the 5th']". The sentence said "it is the lord of the 2nd
and 5th houses". The validator matched each name as a substring, so a lordship named in a list did not
count.

`narrate._names_lordship` now also accepts a lordship named in a list joined by "and", "or" or commas:

- "lord(s) of the 2nd and 5th (houses)";
- "lord of the 2nd, 5th and 9th";
- "rules/ruling the 7th and 12th";
- "2nd and 5th house lord".

The house must be one of the list's ordinals. "Saturn rules the 10th and Mercury the 5th" lists the 10th
alone and is still refused.

The benchmark has the sentence as row `live-lord-of-the-2nd-and-5th`, a paragraph row labelled accept.
The reading's own text was not available locally, so the quoted clause is the reading's and the sentence
around it is rebuilt. That makes 149 rows. With the old check this row is the validator's one false reject;
with the new check there are none (`checker.validator.false_rejects` 0 in docs/scorecard.md). Tests:
`tests/test_narrate.py::test_a_lordship_is_named_in_a_list`, and
`tests/test_checker_bench.py::test_a_lordship_in_a_list_is_a_row_the_validator_passes`.
