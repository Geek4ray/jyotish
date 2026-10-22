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
  `jaimini`, `dasha`, `panchanga`, `ashtakavarga`, `shadbala`, `rules`, `transits`, `houses`, `bhava_bala`, `vimsopaka`, `argala`, `scoring`, `timing`, `narrate`, `page` (the reading's Markdown page), `service` (the read pipeline), `api` (the web service), `cache`, `ephemeris`, `uncertainty`, `models` (pydantic schema).
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
  Argala (Rath's reading, BPHS 31) are done. The nakshatra layer: every body carries
  `nak_attributes` (deity, gana, yoni, nadi, tri-nadi, gender, direction, activity) from
  `constants.NAK_ATTRIBUTES`, whose sources are on the table (none checked yet); `nakpoints.py` gives
  the 64th navamsa and 88th pada from the Moon and the lagna, Abhijit and the nakshatra lagnesha
  (`Features.nakshatra_points`); tables.json and chart.html show the nakshatra table, the points and
  the three dispositor chains. Not yet: synastry module.
- Phase 2 (rules and time): Vimshottari to any depth; Yogini and Chara (K.N. Rao default,
  Raman and Rath via `Meta.chara_variant`) to two levels. Rule evaluator (`rules.py`,
  schema in `rules/rule.schema.json`) and the first ten rules are done; a source is `checked: true` only
  where its verse was read in the named edition.

Transits (`transits.transit_timeline`: tagged rows and named windows over a date range) are
done, with `tara_rows` (Saturn, Jupiter and the nodes entering an adverse tara from the natal Moon;
the Moon's daily tara), tagged and not yet scored (the timing join passes `taras=False`). Layer 5 scoring (`scoring.py`, classical weights; rho table in
`src/jyotish/data/family_rho.json`, made by `scripts/family_rho.py`; one rho and one percentile table
per (`Meta.varga_term`, `Meta.kp_vote`), v2/v2 by default, v1 kept) is done; its open readings
are listed in `scoring.READINGS`. The tagged timeline and `TimingQuery` (`timing.py`) are
done; their readings are in `timing.READINGS` / `READINGS_V2`. Layer 7 narration
(`narrate.py`: Anthropic API with structured output, model and settings in `narrate.CONFIG`,
a code validator on every sentence; a reading never fails on narration alone: after the last
attempt the accepted claims stand, the rest are `narration_gaps`, and a rejected summary is replaced by
the engine's own; depth curious, the request's default, adds a plain-language paragraph per
area, checked like the summary, with the claims under "Show the astrologer's reading"; every finding
carries the `data/glossary.yaml` entries for its terms, so a gloss is checked against a definition) is done, with the
semantic checker after the validator: a second structured call (at
`CONFIG.checker_effort`) per claim and per tagged summary sentence, on every attempt. A rule's
fires on the same planets from several bases are one finding (`yoga.ruchaka@lagna+sun`). Its
non-lagna bases are marked `sudarshana` and cited to the rule only. `jyotish read` (birth data
and a question) writes the reading JSON and the Markdown page; `--model-fixture` replays a
recording offline, and sentences with no recorded checker verdict are counted as unchecked. The checker
calls of an attempt run concurrently (`CONFIG.checker_concurrency`, async SDK); `jyotish.cache`
keeps assessed charts by birth data, conventions, seed and an engine hash (JYOTISH_CACHE_DIR;
the suite points it at a temp dir). `scripts/time_reading.py` times a live reading. The service (`api.py`, FastAPI: POST /readings, GET
/readings/{id} with progress; SQLAlchemy, SQLite by `JYOTISH_DATABASE_URL`, JSONB under Postgres)
runs the shared pipeline in `service.py`; `pip install -e ".[api]"`, `uvicorn jyotish.api:app`. The website (`web/`,
plain HTML/CSS/JS modules from `design/mockups/`, no build step) is served by the same app at `/`;
it renders the reading JSON only (each claim carries its `learner` block). `tests/test_web.py` drives it
with Playwright (`.venv/bin/playwright install chromium`). The offline suite replays the frozen first recording
(`tests/fixtures/narration_career_opus55_r1.json`) and a hand-edited copy, with the checker stubbed;
`JYOTISH_LIVE_NARRATION=1` runs the live test, and `JYOTISH_RECORD_FIXTURE=1` writes every call to
`tests/fixtures/narration_career.json`.
Layer 6b (SPEC): the chart display (`display.py`; `/charts/{id}/chart.svg`, `/tables.json`,
`/chart.html`) and the review step (`review.py`; `/review/{id}`, reviewer tokens in JYOTISH_REVIEWERS,
the `reviews` and `exclusions` tables) are done. The review page is the guided review: one step at a time,
every answer logged by POST /readings/{id}/review/answer (step, area, answer, mode, and an optional
`comment` in the reviewer's own words beside every question but the note), a last question on the
reading as a whole (step `whole`), a summary of one line per question, labels in
`web/js/strings.js`, no engine vocabulary on the page; answers and comments are never shown to the
client and never checked. `?mode=blind` (the judge page's shell)
withholds an area's reading on the server until it is answered from the chart alone; rules may cite `source: practitioner` with status
`practitioner_unconfirmed`, kept out of default scoring (`rules.OUT_OF_DEFAULT`).
The placement rule library (`rules/place.*.yaml`, 144 lord-in-house from BPHS 24, 108
planet-in-house from Phaladeepika 8, and the sign and nakshatra kinds: the Moon in each sign and
nakshatra from Brihat Jataka 17 and 16, the other eight planets in each sign from Brihat Jataka 18
with Saravali second, the rising sign from Saravali; 399 rows; an area offers at most three house
placements, one sign row and one nakshatra row) are `draft`: drafted from principles, not the verses, they fire
and are recorded, are narrated as a placement fact only and carry no weight. A row is promoted to
classical_unconfirmed (source checked: true, read_by, read_on) only when the table records who read the
verse, when, and effect_confirmed yes or changed; the astrologer works in `scripts/placements_triage.csv`
(`docs/triage.md`). The library is generated from
`scripts/placements.csv` by `scripts/make_placements.py` (`--check` in the suite): edit the table, not
the files. Each fire weighs its rule's confidence_base in the rule term; an area offers narration at
most three placements, the rest are `other_placements`. Dispositor chains are findings too
(`chains.py`): per area the primary lord's and main karaka's sign, nakshatra and navamsa chains,
loops, mutual exchanges and Nadi activation at the reading date, and the chart's final dispositors in
personality, tagged `[chain:<area>.<lord|karaka|chart>]` (the sentence names the planet and the chain),
checked against their `facts`; `findings(chart, area, as_of)` takes the reading date for them.
Next (SPEC Layer 6b order of work): outcome capture, the judge page.
