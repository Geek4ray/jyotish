# Notes for the living doc, 2026-10-26

SPEC.md is the export of the living doc and is never edited directly (CLAUDE.md). These follow
docs/spec_notes_2026-10-25.md (the model backends, the GLM-4.7 gate).

## Layer 7 — the checker with reasoning off (2026-10-26)

The checker's effort may now be `none` (`narrate.CHECKER_EFFORTS`): reasoning switched off, sent as
reasoning_effort none, which DeepInfra documents for its reasoning models; Anthropic has no such setting and
it is refused there. The service takes the checker's effort from JYOTISH_CHECKER_EFFORT when set
(`narrate.checker_effort`), else CONFIG.checker_effort (high), and the reading records the effort the
checker ran at. `scripts/checker_bench.py --checker-effort none` measured GLM-4.7 with reasoning off on
DeepInfra: every check answered, 313 s against 2,467 s at high (7.9 times faster), 44,016 output tokens
against 603,884, USD 0.17 against 1.15; recall 0.884 (76 of 86) against 1.000, 18 false rejects against 10.
Against the gate in use (GLM-4.7 at high) it is worse on eight categories (negated, house_changed,
dasha_lord_changed, cites_too_narrowly, judgement_premise, unstated_claim, synthesis_does_not_follow,
wrong_dignity) and does not pass the rule: the gate stays GLM-4.7 at high. With effort low already
measured (passes, 9% fewer tokens, no faster), the reasoning GLM-4.7 does at high is what catches these
errors; a faster gate needs another model, held to the same rule.
