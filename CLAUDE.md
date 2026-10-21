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
  `jaimini`, `dasha`, `panchanga`, `ephemeris`, `uncertainty`, `models` (pydantic schema).
- `src/jyotish/reference.py` — the reference chart from the SPEC worked example.
- `tests/test_reference_chart.py` — the worked example as executable acceptance tests.
  **This is the Phase 1 gate.** If a test here fails, either the code or SPEC.md is wrong;
  fix both, never weaken the test.
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
   that fires it on a known chart and one that does not.
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
  Varnada) and Bhava Madhya/Sripati cusps.
- Phase 1 (feature engine): lordship, dignity (natural + compound), avasthas, sensitive
  degrees, aspects, three dispositor chains, Parivartana, chara karakas (7 and 8), arudhas,
  Navatara, KP sub-lords, Sudarshana H10 are done. Not yet: Shadbala, Bhava Bala,
  Vimsopaka, Ishta/Kashta, Ashtakavarga, Argala, synastry module.
- Phase 2 (rules and time): Vimshottari to any depth exists; no rule evaluator yet.

Next milestones in order: Ashtakavarga → Shadbala → rule evaluator over `rules/` →
Chara and Yogini dashas → transits.
