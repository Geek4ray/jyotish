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

## Dispositor chains for career (2026-10-22)

The reading now offers chain findings (`src/jyotish/chains.py`), and the sentences below are the engine's,
written from its rows. Two of them are offered for career on the reference chart, at the
reading date 2026-10-21, when the Jupiter–Mercury period is running. The semantic checker reads
every `[chain:…]` sentence the writer drafts against them. The two example readings above predate
the chains, so they hold no chain claim. A live run (`JYOTISH_LIVE_NARRATION=1`) records the
writer's sentences for them.

`chain:career.lord` (Saturn, the lord of the 10th, the area's first house):

- Saturn is the lord of the 10th, the area's first house.
- Sign chain of Saturn: Saturn in Taurus, the 1st, friend → Venus in Pisces, the 11th, exalted → Jupiter in Taurus, the 1st, enemy; it ends in the Jupiter–Venus loop.
- Saturn is in no sign loop; its final sign dispositors are Jupiter and Venus.
- Nakshatra chain of Saturn: Saturn in Krittika (Taurus, the 1st, friend) → Sun in PurvaBhadra (Aquarius, the 10th, enemy) → Jupiter in Rohini (Taurus, the 1st, enemy) → Moon in Chitra (Libra, the 6th, neutral) → Mars in Jyestha (Scorpio, the 7th, own) → Mercury in Dhanishtha (Aquarius, the 10th, neutral); it ends in the Mars–Mercury loop.
- Saturn is in no nakshatra loop; its final nakshatra dispositors are Mars and Mercury.
- Navamsa chain of Saturn: Saturn in Capricorn (12th from the D9 lagna, own); it ends in Saturn, self-disposited.
- Saturn is its own final navamsa dispositor.
- Saturn is in neither current period's activation set.

`chain:career.karaka` (Sun, the area's main significator (karaka)):

- Sun is the area's main significator (karaka).
- Sign chain of Sun: Sun in Aquarius, the 10th, enemy → Saturn in Taurus, the 1st, friend → Venus in Pisces, the 11th, exalted → Jupiter in Taurus, the 1st, enemy; it ends in the Jupiter–Venus loop.
- Sun is in no sign loop; its final sign dispositors are Jupiter and Venus.
- Nakshatra chain of Sun: Sun in PurvaBhadra (Aquarius, the 10th, enemy) → Jupiter in Rohini (Taurus, the 1st, enemy) → Moon in Chitra (Libra, the 6th, neutral) → Mars in Jyestha (Scorpio, the 7th, own) → Mercury in Dhanishtha (Aquarius, the 10th, neutral); it ends in the Mars–Mercury loop.
- Sun is in no nakshatra loop; its final nakshatra dispositors are Mars and Mercury.
- Navamsa chain of Sun: Sun in Gemini (5th from the D9 lagna, neutral) → Mercury in Libra (9th from the D9 lagna, friend) → Venus in Aquarius (1st from the D9 lagna, friend) → Saturn in Capricorn (12th from the D9 lagna, own); it ends in Saturn, self-disposited.
- Sun is in no navamsa loop; its final navamsa dispositor is Saturn.
- Sun is activated by the current major period (mahadasha) of Jupiter (in a nakshatra of Jupiter); that period activates Jupiter, Sun, Moon.

