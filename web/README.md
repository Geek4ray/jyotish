# The website

Plain HTML, CSS and JavaScript modules (no framework, no build step), served by the FastAPI
app (`src/jyotish/api.py`) at `/`. Built from `design/mockups/` with the palette and type in
`design/README.md`.

| screen | file | shows |
| --- | --- | --- |
| Home | `index.html` | birth-data form: Place autocomplete (GeoNames, `GET /places`) filling latitude, longitude and timezone, each correctable by hand; accuracy class; node (mean by default); question; empty, out-of-range and 0, 0 coordinates refused; the honest-scope text from SPEC "Goal and honest scope" |
| Reading | `reading.html?id=<job>` | polls `GET /readings/{id}` and shows the progress log, then the reading: summary with the engine's timing line and fields, each area with tier, three stability numbers, polarity touches, claims with citations as footnotes, school conflicts, windows, a collapsed learner panel per claim; "depends on exact birth time"; disclaimers |
| When | `timing.html?id=<job>` | the windows and the avoid window with q, t, strongest piece and the q components |
| Chart | `chart.html?chart=<chart id>` | the engine's SVG (D1, D9, D10, North-Indian) and its tables: planets, Vimshottari to the pratyantar with the current period, Shadbala, Ashtakavarga, Bhava Bala (`GET /charts/{id}/chart.svg`, `/tables.json`); linked from the reading |
| Phone | the same pages under 720 px | one column and the tab bar from `mockups/Phone.html` |

Either page also takes `?src=/examples/reference_reading.json` to show a reading file served by
the app. Everything on screen comes from the reading JSON (`js/render.js` renders, never
computes): tier words and stability labels verbatim, `probability: null` as "not calibrated".

Run locally:

    .venv/bin/pip install -e ".[api,dev]"
    ANTHROPIC_API_KEY=... .venv/bin/uvicorn jyotish.api:app
    open http://127.0.0.1:8000/

Tests: `tests/test_web.py` (Playwright; `.venv/bin/playwright install chromium` once).

Place data: GeoNames cities15000 (https://www.geonames.org), CC BY 4.0, bundled as
`src/jyotish/data/places.tsv.gz` by `scripts/make_places.py`; the footer carries the attribution.
