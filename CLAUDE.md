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
  `jaimini`, `dasha`, `panchanga`, `ashtakavarga`, `shadbala`, `rules`, `transits`, `houses`, `bhava_bala`, `vimsopaka`, `argala`, `scoring`, `timing`, `narrate`, `fullchart` (the whole chart for depth full, by path), `client` (depth full's client's layer), `sheet` (the astrologer's technical sheet, engine-written), `page` (the reading's Markdown page), `service` (the read pipeline), `api` (the web service), `db` (every table, `migrate()`, tokens), `migrations` (Alembic), `costs` (the price table), `logs` (JSON lines, no birth data), `cache`, `ephemeris`, `uncertainty`, `models` (pydantic schema).
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
   if texts disagree, a comment saying so and a setting. (The special taras are one: `Meta.special_taras`,
   `desha_27` by default, `desha_12` the SPEC's reading.)
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
  the 64th navamsa and the 22nd drekkana (the Khara points, both 210° on) from the Moon and the lagna, Abhijit and the nakshatra lagnesha
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
Depth full (2026-10-23; SPEC rev 117-118, and the second depth-full heading of docs/spec_notes_2026-10-23.md):
the writer gets the whole chart (`fullchart.payload`: every table, vote derivation, dasha to the pratyantar
and ten years of transits, under stable paths, every one resolvable (a rule fire is
`rules.<id with dots as hyphens>@<basis>`); 434,445 characters on the reference chart, held by
`tests/test_fullchart.py`), cites any field as `[fact:<path>]` (the validator resolves the path, the checker
gets the value, the reading keeps `facts_cited`), thinks adaptively at `CONFIG.full_effort` (xhigh; max by
--writer-effort; a writer call whose thinking reaches max_tokens with no draft is retried one effort level
lower, recorded in `writer.stepped_down`) with `full_max_tokens` streamed, and writes per area an `analysis`
(assessment, timing, not_said). The payload states what the engine knows: varga rows carry
`varga_dignity_label`, every stability is a labelled object, the arudha derivation `rests_on` and `why`,
plus `constants`, `houses.<lagna|moon|sun>.<n>` (following Meta.house_system from the lagna, `houses.system`
says which), `not_computed`, and per area `contributions` (each family's term in S with its percentile
against 10,000 charts, `data/family_percentiles*.json` from `scripts/family_rho.py`; strongest and weakest by
percentile, and "the strongest support" must cite it). Every sentence of a summary, paragraph or section goes
to the checker, tagged or not, and at depth full an analysis sentence must carry a tag. Analysis sentences
are checked (each proposition), syntheses (two or more items: the conclusion must follow) or judgements ("I
weigh …", "I give … weight", "I read … as", "I resolve …": every proposition about the chart must be stated by
a cited fact, only the weighing stands unverified and is shown as "the reading's weighing"; the validator
refuses one stating a figure, date, age, period, dignity, strength or outcome no cited fact states); "the
10th sign" is refused for "the 10th house from the lagna" (houses.lagna.10), and the timing filter knows ages. Section retries (`CONFIG.section_retries`, depth full only): every unit passing the
validator is checked in its attempt and held once it passes, and a retry asks only for the failed units
with their reasons (`retry_instruction`); `scripts/section_retries.py` replays a recording under both
policies. `--writer-model`/`--writer-effort` (and `writer_model`/`writer_effort` on POST /readings) move
the writer only; `CONFIG.checker_model` and `checker_effort` stay; the reading records `writer`, `checker`,
`usage`. `[tradition:<text> <chapter>]` (analysis only, `narrate.TRADITION_TEXTS`) is never checked: shown
apart as unverified, refused if it states a numeral, date, period, strength or anything the engine computes,
or names a planet with this chart's sign or house for it (or the rising sign), and a live reading appends it
to `data/candidate_rules.jsonl` (JYOTISH_CANDIDATE_RULES; gitignored; triage in
docs/triage.md). `scripts/compare_readings.py` runs two (model, effort, depth) settings and writes
docs/comparison_<date>.md with a per-attempt table (`--out` for a second run on one day: the first
comparison's files are inputs to the checker benchmark and the replay); `/compare/{a}/{b}` shows the two
blind to a reviewer, one question, logged (`reviews` action `compare`, exported with the judgements),
settings revealed after the answer; a reading in a comparison is blind at GET /readings/{id} and in the
review step to a reviewer who has not answered it, and needs a token there. The first live comparison is
docs/comparison_2026-10-23.md; its engine-fault refusals are the `b-` rows of
`tests/fixtures/checker_bench.jsonl`, and the `kind-` rows put each new sentence kind before the live
checker. docs/review_2026-10-23_depth_full.md is the independent review; F1-F13 are fixed (the third
depth-full heading of the spec notes). The re-run after the fixes is Ray's to run: the command closes that
heading.
Depth full for the client (2026-10-24, the heading "Layer 7, depth full — readable by the client" of the spec
notes): the payload's vargas table gives each of the seven planets its sign and dignity per varga
(`scoring.varga_dignity_word`, the varga vote's words) and every transit window and tara row its
`areas_touched` (houses from the Moon and the lagna, the areas by scoring.AREAS; a mapping, not an effect).
The analysis's "what the chart does not say" is two lists, `not_said_client` (the client's words) and
`not_said_astrologer`. Once claims and sections are accepted, a second writer call (`jyotish.client`, at
`CONFIG.client_effort`) writes each area's plain paragraph and the summary from accepted text and the facts
it cites only: the answer first, then for, against, the timing in dates; every sentence tagged from the
accepted text, no engine vocabulary (`client.CLIENT_WORDS`), no "I", a weighing as "in the reading's view"
(a judgement); validated and checked like the summary, held and retried per unit. The first call writes no
summary at depth full. Recordings keep `client_drafts`; one made before has paragraph gaps on replay, and a
recorded single `not_said` is the astrologer's list. The page and the site show per area the paragraph,
the client's list, the tier line, then "The astrologer's analysis" and the findings under toggles; a gap's
error is never on the client's page (one line counts the gaps), only in the JSON, on the review page and in
the comparison report. The suite stubs the client's writer (`tests/conftest.py`, EchoClient).
`scripts/replay_accepted.py` replays a comparison's recordings and diffs accepted text against the committed
readings (docs/replay_2026-10-24.md: none for r2). The live re-run is Ray's (docs/comparison_2026-10-23_r3.md).
The two-audience page (2026-10-25, docs/spec_notes_2026-10-24.md): at depth full the client's view is "What the
chart says for you" (`paragraph`: answer, for, against; no dates), "When" (`when`: windows in dates and months,
the weighing as "the reading's view") and "What this chart does not tell" (`not_said_client`), written from
accepted text only; the client's words also exclude cusp, sub-lord, arudha, dasha, Shadbala, Bhava Bala, rupa,
a Sanskrit word with a plain phrase is refused for it (`client.CLIENT_PLAIN`) and one without (`client.SANSKRIT_TERMS`)
is glossed in the same sentence, its glossary definition sent to the checker. The astrologer's technical sheet
(`sheet.build`, `ReadingArea.sheet`) is fifteen numbered points written by the engine from the payload with no
model call, each item citing its paths, at every depth (the service attaches it, `upgrade_reading` and GET
/readings fill it in for older readings; `fullchart.cached_payload`); `tests/test_sheet.py` reads every point
against the chart object. Page and site: the client's view, the tier line, then one "For the astrologer" toggle
(sheet, analysis at depth full, findings; open with no client's view); the review page shows the sheet beside the
paragraph; the reading page prints the client's view alone or both (strings in web/js/strings.js).
`scripts/rebuild_pages.py` re-renders a comparison's pages from their JSON (docs/comparison_2026-10-23_r2/*.page.md).
Model backends (2026-10-25, docs/models.md, docs/spec_notes_2026-10-25.md): the writer, the checker and the client's
layer call a `narrate.Backend` (one structured completion against a schema; `ModelDrafter`, `ModelChecker` over it;
`AnthropicDrafter`/`AnthropicChecker` are those on `AnthropicBackend`, the calls as before). `OpenAIBackend` (httpx) speaks
the chat-completions API: response_format json_schema, else JSON mode with our validation and one retry, else a
NarrationError naming the server; reasoning_effort dropped if refused; OpenRouter sent data_collection deny, zdr,
require_parameters. Each role from JYOTISH_WRITER_BACKEND / _CHECKER_ / _CLIENT_ ("anthropic" or "openai:<base url with
its path>:<model>"), keys JYOTISH_<ROLE>_KEY or JYOTISH_OPENAI_KEY. The reading records the three roles' model, effort and
backend (`client` is new; its usage is apart from the writer's); `costs` prices each role by model and host
(`OPEN_PRICES`, `PRICE_SOURCES`, read 2026-10-25; local free; unpriced never guessed); ledger revision 0003; /health
shows each role's readiness. `narrate.full_depth_guard` refuses depth full on a local model unless
JYOTISH_ALLOW_LOCAL_FULL, and on a hosted model whose known window cannot hold the ~195,000-token message
(`CONTEXT_TOKENS`). `scripts/checker_bench.py --checker-backend` writes docs/checker_scorecard_<model>.md with the
rule's verdict; `scripts/compare_readings.py` takes `openai:` settings, `--checker-a/-b`, `--live-checker`. The checker
changes for client readings only when its recall is not worse on any category (docs/models.md). Tests:
tests/test_backends.py, tests/test_openai_backend.py (a stub OpenAI-compatible server). The OpenAI backend retries
dropped connections, timeouts and 429/5xx (five attempts, backoff, Retry-After, `backend.retry` logged without the key),
opens one async client per batch and closes it (`Backend.aclose`), defaults to 4 calls at once hosted and 1 local
(JYOTISH_CHECKER_CONCURRENCY overrides; Anthropic 16); a checker call that fails after the retries fails its sentence
as unchecked (`Reading.unchecked_sentences`). The benchmark writes data/bench_partial/ as it goes and both scripts take
--resume and read keys from the gitignored .env (`jyotish.envfile`). Scorecards: docs/checker_scorecard_zai-org-glm-4.7.md,
docs/checker_scorecard_qwen-qwen3.6-35b-a3b.md (2026-10-25). The gate in use is GLM-4.7 on DeepInfra (Ray's decision, no
Anthropic): `checker_bench.py` compares against it by default (`GATE`, `--gate`; `--apply-rule` re-applies the rule to a
scorecard from its table); against it Qwen fails on three categories. The local `.env` sets all three roles on DeepInfra
(gpt-oss-120b writer and client's layer, GLM-4.7 checker); docker-compose passes the variables. The checker's effort is
JYOTISH_CHECKER_EFFORT or CONFIG.checker_effort (`narrate.checker_effort`; `none`, reasoning off, only on an OpenAI-compatible
backend; `checker_bench.py --checker-effort`). GLM-4.7 at low passes the rule but saves 9% of tokens; with reasoning off it
is 7.9 times faster and fails the rule on eight categories (docs/spec_notes_2026-10-26.md): the gate stays GLM-4.7 at high.
Layer 6b (SPEC): the chart display (`display.py`; `/charts/{id}/chart.svg`, `/tables.json`,
`/chart.html`) and the review step (`review.py`; `/review/{id}`, reviewer tokens in JYOTISH_REVIEWERS,
the `reviews` and `exclusions` tables) are done. The review page is the guided review: one step at a time,
every answer logged by POST /readings/{id}/review/answer (step, area, answer, mode, and an optional
`comment` in the reviewer's own words beside every question but the note), a last question on the
reading as a whole (step `whole`), a summary of one line per question, labels in
`web/js/strings.js`, no engine vocabulary on the page; answers and comments are never shown to the
client and never checked, and another reviewer's answers and comments are not shown to a reviewer
either (the export is where judgements meet). `?mode=blind` (the judge page's shell)
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
Evaluation harness v1 (2026-10-22): `scripts/crosscheck.py` is the Phase 0 cross-check against
PyJHora, which is AGPL and dev-only (extra `crosscheck`, never imported by src/); 1,000 births pass
the 1″ gate, see docs/crosscheck.md. `tests/test_metamorphic.py` holds the label-free invariants on
the reference chart and three synthetic births (`tests/fixtures/births.json`).
`tests/fixtures/checker_bench.jsonl` is built and scored by `scripts/checker_bench.py`; the live
checker run is marked live. `jyotish export-reviews` writes the judgements to data/preferences/
(gitignored client data; judgements, not outcomes). `scripts/evaluate.py` writes
docs/scorecard.{md,json}, and `.github/workflows/ci.yml` runs pytest and then fails when any *gated*
scorecard number is worse than the committed one: the verdicts (tests passed and failed, the
cross-check's maxima, the validator's wording catch and false rejects, the placement check) and two
pass/fail checks on the 20,000-subject synthetic runs. Sampled statistics (the synthetic shares and
counts, the sampler's seed agreement, the validator's precision and recall on the benchmark) and the
last live checker run (read from docs/checker_scorecard.md) are reported, not gated. Re-run
`scripts/evaluate.py` and commit the scorecard when a change is meant to move a number.
Outcome side (SPEC Layer 6, 2026-10-22). `outcomes.py` with the consents, subjects, events and
erasures tables, the fixed event vocabulary, and `data/outcome_map.yaml` (areas and rule outcomes to
events; an unmapped rule is not_testable_yet). `jyotish outcomes import|consent|withdraw|status` and
POST /outcomes (clerk tokens in JYOTISH_CLERKS) refuse bad rows with reasons, and `jyotish subject
erase` removes a subject and logs it. Subjects, charts, readings and exclusions carry a `birth_key`
(`cache.birth_key`: the UTC instant and the place, nothing of the engine), by which a subject's rows
are matched at import and erased, across engine versions and accuracy classes; twins keep their shared
chart. `scripts/validate.py` (extra "validate": scipy, scikit-learn, statsmodels) runs SPEC tests 1-8
and 10 over the database: a salted-hash sequestered 25% by household (a household's charts land on one
side) frozen in data/sequestered.txt (gitignored) and registered by its salt's hash in
docs/pre_registration.json, which also logs every scoring of the sequestered cohort; grouped
stratified K-fold; test 4's activation is the engine's own windows (the timing join's pieces over the
life, the best third by joint, `jyotish.cohort`); test 8 compares the schools' vote sums per area; abstention (test 5) is the engine's own gate when
`--stability-samples` runs the sampler per chart (200 by default on a real cohort), the accuracy class
standing in without it; docs/validation.md. Chart features for cohorts come from `jyotish.cohort`. `scripts/synthetic_cohort.py` makes planted and null cohorts;
the suite runs them at small N, and the harness at 2,000 and 20,000, writing
docs/validation_synthetic_*.md (every heading says synthetic).
Deployable service (2026-10-23, docs/deploy.md): a Dockerfile (python:3.12-slim-trixie, the checkout installed
editable, /data a volume), docker-compose.yml (Postgres 16; Caddy and the nightly `scripts/pg_backup.sh` under the
`host` profile), fly.toml, configuration from the environment only. Every table is in `jyotish.db` and migrated by
Alembic (`src/jyotish/migrations`; `migrate()` on every open, a create_all database adopted and stamped); a new
table needs a revision and `tests/test_db.py` fails on drift. Reviewer, clerk and owner tokens are rows in
`credentials` (`jyotish reviewer|clerk|owner add|revoke|list`; the token printed once, its hash kept);
JYOTISH_REVIEWERS / JYOTISH_CLERKS still work locally and are logged as such. POST /readings is rate-limited; every
finished reading gets a `ledger` row (GET /costs/daily, owner token); GET /health reports the engine hash and the
database revision; /source is the AGPL offer (JYOTISH_SOURCE_URL). JYOTISH_MODEL_FIXTURE replays a recording, for
the CI smoke test only (`scripts/smoke.py`: a reading, its review page in Playwright, one answer; the image job
runs it in the container, tests/test_web.py against the checkout).
Next (SPEC Layer 6b order of work): outcome capture, the judge page.
