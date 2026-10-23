# Notes for the living doc, 2026-10-23

SPEC.md is the export of the living doc and is never edited directly (CLAUDE.md). These are the
places where the code moved past it on 2026-10-23, after `docs/review_2026-10-23.md`, each with the
commit that did it, for Ray to port. Line numbers are SPEC.md's at rev 101.

## Layer 1 (lines 44, 480) — the cross-check

- `scripts/crosscheck.py` chooses PyJHora's varga method for each chart by PyJHora's own label (the
  lowest-numbered method its docstring calls "Traditional Parasara": 1 everywhere but the hora,
  whose 2 it is), never by agreement with the engine, and a control with the Raman hora must fail
  (0c417af). The gate still passes on 1,000 births. The independent ephemeris remains the jplephem
  track; both programs call Swiss Ephemeris.

## Layer 1b (line 54) — what the sampler stamps

- Every body's and the lagna's nakshatra now carry the three numbers too (`Uncertainty.nakshatras`),
  and a dispositor-chain finding's stability is the smallest share among what its steps state: D1
  signs, the D9 signs and D9 lagna of the navamsa chain, the nakshatras of the nakshatra chain. On
  the reference chart the career-lord chain is 0.78 stable, the D9 lagna's number, not 1.0 (add7b22).

## Layer 2 (lines 123, 125) — the nakshatra layer

- Line 125: the "88th-degree point" is gone. The 64th navamsa (63 navamsas on) and the 22nd drekkana
  (21 drekkanas on) are both 210° on, the eighth sign from the body: the texts' two Khara points.
  `nakpoints.py` computes the 22nd drekkana from the Moon and the lagna (span, sign, place in the
  sign, the lord of its D3 sign); the 88th pada, 290° on, matched nothing (add7b22). The sentence
  "which counted from a first pada is the last pada of the 22nd (Vainashika) nakshatra" should go
  with it: the engine's own table puts Vinasha at the 23rd (line 564 agrees).
- Line 123: "gender" is two things. The yoni koota's sex of the animal (`yoni_sex`: one male and one
  female per animal, the mongoose a male alone) and the modern compilations' nakshatra gender
  (`gender`: eight male, sixteen female, Mrigashira, Mula and Shatabhisha neuter), with no classical
  text located for the second (add7b22).

## Layer 3 (line 201; worked example lines 679, 681) — the placement drafts

- The 24 Rahu and Ketu sign rows name no text: Brihat Jataka 18 and Saravali treat the seven planets
  in the signs. The Moon's rows carry one phase modifier (Paksha bala under 30 of 60), not a second
  "waning" code stacked on it (9ed50af). `jyotish reference` shows 32 placement fires with the sign
  and nakshatra rows, where line 679 counts 21; the Moon's two rows fire at full scale.

## Layer 5 / worked example (lines 659, 683) — `jyotish reference`

- The command prints its Life areas from the true-time chart now, so the first tier table it prints
  is the worked example's (career moderate 0.70, health weak / mixed, top three career, marriage,
  longevity), not the positions-only chart's; line 683's sentence holds again.

## Layer 6 (lines 309–318, 345) — the outcome side

- Test 1: the split assigns by household (a household's charts land on one side; a subject joining
  an assigned household takes its side) and the salt's SHA-256 is registered in
  `docs/pre_registration.json`, which also logs every scoring of the sequestered cohort; a missing
  file or another salt is refused, never redrawn (854e816).
- Test 4: the activation covariate is the engine's own windows, the timing join's pieces over the
  life with the best third by joint active, a third of the person-years for everyone (b5727f3). The
  dasha gate alone covered nine years in ten.
- Test 8 is built: each school's vote sum per area, AUC with DeLong's interval on the development
  set, the winner estimated once on the sequestered cohort (854e816). "Tests 1–8 and 10" is now true.
- Subjects, charts, readings and exclusions carry a birth key (the UTC instant and the place, nothing
  of the engine), by which rows are matched at import and erased, across engine versions and
  accuracy classes; twins keep their shared chart (1d624cf).
- The synthetic planted run counts the unplanted areas (father, gains, reputation) that survive BH:
  all three at 20,000, lift inherited through the shared outcome map, reported and not gated
  (0cdb2a4). The nested-model table marks a DeLong p whose AUC fell.
- The harness gates verdicts only; sampled statistics are reported with their direction (a90f712).

## Layer 6b (line 345, the review step) — judgements

- The review view shows a reviewer their own answers, verdicts and words only; another reviewer's
  appear nowhere on the page, the export is where judgements meet (4022662). Note, whole-reading and
  edit texts are bounded.

## Layer 7 (line 370, item 10) — the validator

- The rule that a claim stands alone is enforced now, narrowly: a claim with "again", "likewise",
  "aforementioned", "as above/noted/said/mentioned/before" or opening "The/This/That same" is refused
  before checking; summaries and paragraphs are exempt (4699460). The two benchmark rows the checker
  could never catch are caught; the validator's recall on the benchmark is 0.243.

## Two differences decided on 2026-10-23

- Line 564 (the Sun in PurvaBhadra "the 12th (Desha)", "27th (Jati)") against the engine's Jati 26 and
  Desha 27: the special taras are now a setting, `Meta.special_taras`. The default, `desha_27`, is the
  common modern list (Jagannatha Hora's among them: Jati 26, Desha 27); the SPEC's reading is kept as
  `desha_12` (Desha 12, Jati 27), so nothing the doc says is lost. Neither is read in a named edition.
  The doc should say the Sun's 12th is a special tara only under the second scheme, or name a text
  for the 12th. (SPECIAL_TARAS predates the review's range: 2228f41.)
- Line 558 ("the Venus–Jupiter loop"): one name everywhere now, the loop read from the planet
  earliest in graha order, in the chart object, the chain findings and the chart page: Jupiter–Venus.
  The `houses` beside it read in the same order (Jupiter in the 1st, Venus in the 11th: [1, 11]).

## Still standing

- Abstention (test 5) now follows the engine's gate when `--stability-samples` runs the sampler
  (200 by default on a real cohort); the synthetic harness keeps the accuracy class as the gate's
  stand-in, and every report says which gate it used.
- The facts shown beside a sentence are stored with the edit (`reviews.facts`) and the export reads
  them, recomputing (and saying so) only for rows from before.
