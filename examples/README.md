# Example readings

`reference_reading.json` and `reference_reading.md` are a live `jyotish read` of the reference
chart (2001-03-12 10:10:25 IST, Rewari; used with the owner's consent), recorded 2026-10-21
with claude-opus-5-5 under varga v2 and KP v2: three areas, 21 claims, three attempts, every
sentence through the validator and the checker. The Markdown page's header carries the exact
command that reproduces it. This is the input the website renders.

The JSON was later brought up to the current schema with `jyotish page --from
examples/reference_reading.json … --json-out examples/reference_reading.json` (no model call):
each claim gained its engine-written `learner` block and the summary its `timing_line`; the
model's text is unchanged, and the page was re-rendered from it.

`reference_reading_curious.json` and `reference_reading_curious.md` are the first complete
curious reading: a live reading of the same birth data made through the website (POST
/readings) on 2026-10-22 with claude-opus-5-5, varga v2 and KP v2, saved from GET
/readings/967c22064f054c9daf5e6db140a7c231. The question was the owner's own about a career
change. It covers three areas (career, marriage, longevity), with a plain paragraph each and 28 claims
under "Show the astrologer's reading". It took three attempts, every sentence went through the
validator and the checker, and nothing was left as a narration gap. The summary was the model's.
Its review status is `draft`: no astrologer has reviewed it. The place was chosen from the GeoNames
list, so its coordinates are GeoNames' Rewāri (28.199, 76.6183), not the 28.1989, 76.617 of
`reference.py`. The page was rendered with `jyotish page --from
examples/reference_reading_curious.json` and those coordinates (the command is in its header), and
it matches the page the server stored byte for byte.
