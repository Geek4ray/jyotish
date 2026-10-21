# Jyotish engine — working rules for Claude Code

Read `SPEC.md` before changing anything. It is the build specification (eight layers,
19 life areas, validation protocol, worked example). The living copy is a Claude doc;
`SPEC.md` is its export and says so in its first line.

## What this repo is

A Vedic-astrology computation engine. Every classical quantity is computed exactly and
every finding is reported with its stability under birth-time uncertainty. The engine
never claims precision about outcomes; the validation layer (SPEC Layer 6) decides what
wording is allowed. Keep that posture in code comments, CLI output and any UI copy.

## Layout

- `src/jyotish/` — the engine. `chart.analyse` builds the chart object from sidereal
  longitudes (no ephemeris needed); `chart.compute` goes from birth data via Swiss
  Ephemeris. One module per concern: `vargas`, `nakshatra`, `dignity`, `dispositors`,
  `jaimini`, `dasha`, `panchanga`, `ashtakavarga`, `shadbala`, `rules`, `transits`, `houses`, `bhava_bala`, `vimsopaka`, `argala`, `scoring`, `timing`, `narrate`, `page` (the reading's Markdown page), `ephemeris`, `uncertainty`, `models` (pydantic schema).
- `src/jyotish/reference.py` — the reference chart from the SPEC worked example, with its
  birth data (2001-03-12 10:10:25 IST, Rewari, Haryana), used with the owner's consent.
  Every feature you build must be exercised on this chart first.
- `tests/test_reference_chart.py` — the worked example as executable acceptance tests
  (positions → features). **This is the Phase 1 gate.** If a test here fails, either the
  code or SPEC.md is wrong; fix both, never weaken the test.
- `tests/test_ephemeris_reference.py` — birth data → positions against the reference app
  (2″ on planets, 1′ on the ascendant). The app screenshots were made with the time entered
  as 10:10:00; the true time is 10:10:25. Tests compare printed positions at 10:10:00 and
  use the true time elsewhere.
- `rules/` — the YAML rule library (SPEC Layer 3). Rules are data, with a text source and
  edition on every one.

## Rules that bite

1. Astrological conventions are settings, not silent choices: ayanamsa, node type (the
   reference app uses the **mean** node), house system, dasha year length, karaka scheme,
   node aspects. Every new convention goes in `constants.py` with its text source and,
   if texts disagree, a comment saying so and a setting.
2. No placeholder values in the chart object. A field exists only when a layer produces
   it (see `models.py`). Illustrative numbers belong in SPEC.md, labelled, never in code.
3. Floating-point sign and nakshatra boundaries: use the `lon * 27 / 360` style
   (`nakshatra._nak_index`) rather than dividing by 13.333…; add a boundary test when you
   touch a division.
4. Layer order is a dependency order. The uncertainty sampler (`uncertainty.py`) runs
   before scoring and uses only the accuracy class; the rectifier (not yet written) runs
   after scoring. Do not create a cycle between layers 1b, 5 and 6.
5. Any rule you add needs: `id`, `school`, `source` with edition/chapter/verse, `status`
   (`classical_unconfirmed` for a cited rule), `basis`, `themes`, `outcomes`, and a test
   that fires it on a known chart and one that does not. An `experimental` rule may omit
   `source`; its fires carry that status and stay out of default scoring.
6. Licensing (SPEC Tech stack): Swiss Ephemeris is AGPL/commercial and there is no LGPL
   fallback; PyJHora/Maitreya are GPL and are dev-time references only; Astro-Databank is
   CC BY-NC-SA. Do not add dependencies that change this picture without a note in SPEC.md.

## Environment

- Python 3.11+. Use the venv (`python -m venv .venv && .venv/bin/pip install -e ".[dev]"`).
  On Debian/Ubuntu with the system setuptools, `pip install pyswisseph` fails with
  `AttributeError: install_layout`; the venv's own setuptools avoids it.
- Moshier ephemeris (no files) is the default; set `JYOTISH_EPHE_PATH` to a Swiss
  Ephemeris data directory for full precision.
- `pytest -q` must be green before every commit. `jyotish reference` prints the worked
  example; its output is what SPEC.md's worked example must say.

## Phase status

- Phase 0 (astronomical core): done except special lagnas (Hora, Ghati, Indu, Sree,
  Varnada). Sripati bhavas are in `houses.py` (`Meta.house_system`). The Layer 1b sampler
  (`uncertainty.assess`) stamps every fired rule, varga placement and dasha boundary with
  time / ayanamsa / house stability.
- Phase 1 (feature engine): lordship, dignity (natural + compound), avasthas, sensitive
  degrees, aspects, three dispositor chains, Parivartana, chara karakas (7 and 8), arudhas,
  Navatara, KP sub-lords, Sudarshana H10, Ashtakavarga (BAV incl. lagna, SAV, Trikona and
  Ekadhipatya, Sodhya Pinda, Kakshya), Shadbala (BPHS 27, all six balas with settings in
  `Meta`), Bhava Bala (whole sign and Sripati), Vimsopaka (four schemes), Ishta/Kashta and
  Argala (Rath's reading, BPHS 31) are done. Not yet: synastry module.
- Phase 2 (rules and time): Vimshottari to any depth; Yogini and Chara (K.N. Rao default,
  Raman and Rath via `Meta.chara_variant`) to two levels. Rule evaluator (`rules.py`,
  schema in `rules/rule.schema.json`) and the first ten rules are done; a source is `checked: true` only
  where its verse was read in the named edition.

Transits (`transits.transit_timeline`: tagged rows and named windows over a date range) are
done. Layer 5 scoring (`scoring.py`, classical weights; rho table in
`src/jyotish/data/family_rho.json`, made by `scripts/family_rho.py`) is done; its open readings
are listed in `scoring.READINGS`. The tagged timeline and `TimingQuery` (`timing.py`) are
done; their readings are in `timing.READINGS` / `READINGS_V2`. Layer 7 narration
(`narrate.py`: Anthropic API with structured output, model and settings in `narrate.CONFIG`,
a code validator on every sentence) is done, with the semantic checker after the validator: a second structured call (at
`CONFIG.checker_effort`) per claim and per tagged summary sentence, on every attempt. A rule's
fires on the same planets from several bases are one finding (`yoga.ruchaka@lagna+sun`). Its
non-lagna bases are marked `sudarshana` and cited to the rule only. `jyotish read` (birth data
and a question) writes the reading JSON and the Markdown page; `--model-fixture` replays a
recording offline, and sentences with no recorded checker verdict are counted as unchecked. The offline suite replays the frozen first recording
(`tests/fixtures/narration_career_opus55_r1.json`) and a hand-edited copy, with the checker stubbed;
`JYOTISH_LIVE_NARRATION=1` runs the live test, and `JYOTISH_RECORD_FIXTURE=1` writes every call to
`tests/fixtures/narration_career.json`.
Next: Layer 6 (validation), the retrieval corpus for Layer 7, and the synastry module.
