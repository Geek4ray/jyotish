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
