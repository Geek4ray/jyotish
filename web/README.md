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
| Review | `/review/<reading id>` | the guided review, for a reviewer (token from JYOTISH_REVIEWERS). The chart is fixed on the left (D1, D9, the Vimshottari maha and antar tables with the current period) and the questions are on the right, one step at a time, with a progress bar, large buttons and keys (1/2/3… choose, Enter goes on, Ctrl+Enter from a text box). Every answer is saved as it is given, and text being typed is kept in the browser until it is sent; the page reopens at the first step not yet answered. Step 0, once per reviewer, is three screens: what the engine did, what checked text means, and that the note goes to the client in their name. Then each area has five steps: (1) the paragraph in full, "Does this match your reading of the chart?" (Agree / Partly / Disagree); (2) if not Agree, "What is off?" (several choices, an optional line); (3) each sentence as a card, Keep or Rewrite, where a rewrite is shown beside the chart facts it rests on, read back by the validator and the checker, and refused with the reason in plain words; (4) the note, which the client sees as the astrologer's own words; (5) for an area with windows, "Does the best period match yours?" (Yes / Earlier / Later / A different period, with a range). A summary and Approve close it. All labels are in `js/strings.js`. The client's Reading page changes only by an accepted rewrite, a note and the approval ("Reviewed by"). |
| Judge | `/review/<reading id>?mode=blind` | the same page in blind mode, the judge page's shell: for each area the reviewer first answers from the chart alone (their reading: Promising / Mixed / Difficult, and their best period where the area has windows). The server sends that area's paragraph and windows only after, then the five steps follow with the reviewer's own answers beside the engine's. Answers from the chart alone cannot be changed once the reading is shown, and the chart is excluded from the learning set only then. |
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
