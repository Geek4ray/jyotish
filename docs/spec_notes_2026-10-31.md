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

## Layer 7 — a paragraph held sentence by sentence (2026-10-31)

The marriage paragraph was refused on all three attempts because one sentence tagged
[rule:place.l12_h7] without naming Mars as the 12th lord. The whole paragraph was one unit, so each retry
rewrote it and the whole of it was lost each time.

A paragraph's sentences are now units, the way depth full's sections are (`live.HeldParagraph`). This
applies wherever units are held: the writer's paragraph at curious depth in the live narration, and the
client's layer's paragraph at depth full. With `JYOTISH_LIVE=0`, curious depth keeps the single call's
whole-draft retries.

- **Held.** A sentence that passes the validator and the checker is held.
- **Keys.** The first draft's sentences take the keys 1, 2, …. A retry's j-th sentence takes the j-th
  failed sentence's key, and any extra sentences follow the last one as "<key>.1", "<key>.2", …. A sentence
  the retry sends again verbatim beside the held ones is not placed twice.
- **The retry.** `retry_instruction` lists the held sentences as "the <area> paragraph's other sentences (k
  of n)". It asks for each failed sentence, quoted, with its position ("the marriage paragraph, sentence 2 of
  3 (…)") and its reasons, and adds `PARAGRAPH_RETRY_NOTE`: return only the rewritten sentences, in order.
- **The phrase to use.** A refusal for a rule tag on a sentence that does not name it now states the phrase
  to use (`narrate.name_hint`), for example "(name Mars as the 12th lord or the lord of the 12th)". The
  planet comes from the finding's placement.
- **After the last attempt.** The held sentences stand as the paragraph, in key order. If any sentence
  never passed, the paragraph keeps one gap, counted as a paragraph's gap always was. The page and the site
  show the held sentences and count the gap.
- **The live view.** Each sentence is the unit "paragraph:<area>:<key>". A refusal removes that sentence
  alone, and the site (`web/js/live.js`) shows the sentences inside one paragraph in key order, so a
  replacement lands where the refused sentence was.

Tests:

- `tests/test_live.py::test_curious_paragraph_is_held_sentence_by_sentence_and_the_retry_names_the_lordship`
  (the Fly case: sentences 1 and 3 held, the retry asks for sentence 2 with "name Mars as the 12th lord or the
  lord of the 12th", and the replacement takes its place);
- four tests in `tests/test_client_layer.py` (a retry rewrites only the failed sentence; a sentence that never
  passes leaves the others and one gap; held sentences sent again are not placed twice; extra sentences
  follow the failed one);
- `tests/test_web.py::test_the_site_replaces_one_paragraph_sentence_in_its_place`.

**The replay** (`scripts/replay_accepted.py docs/comparison_2026-10-23_r2`, written to
docs/replay_2026-10-31.md): 0 differences in accepted text on either side, and the gaps are the same as a
replay at 1ec91cd, the commit before this change. The policy cannot show there:

- A is at astrologer depth, which has no paragraph.
- B is at depth full but was recorded before the client's layer, so it has no client drafts to replay.
  Every paragraph and every When is a gap on replay, now as before. The three When gaps that docs/replay_2026-10-24.md
  did not list are there at 1ec91cd too, so they predate this change.

No recording in the repository holds a paragraph: those of 2026-10-23 to 2026-10-27 and docs/live_2026-10-26
are at astrologer depth or full. The policy is measured live in the comparison at curious depth below.
