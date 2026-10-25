# Notes for the living doc, 2026-10-24

SPEC.md is the export of the living doc and is never edited directly (CLAUDE.md). These are the
places where the code moved past it from 2026-10-24 on, each with what it does and why, for Ray to
port. They follow docs/spec_notes_2026-10-23.md, whose last heading ("Layer 7, depth full — readable by
the client without losing anything") built the client's layer this builds on.

## Layer 7 and Layer 6b — the two-audience page (2026-10-25)

A reading is read by two people: the client, who knows no astrology, and the astrologer, who checks
it. The page now has a view for each.

**The client's view (part 1).** At depth full each area opens, in plain words, with three parts: "What
the chart says for you" (the answer in two or three sentences, what supports it, what works against
it), "When" (the windows in dates and months, the reading's weighing carried over as "the reading's
view") and "What this chart does not tell" (the client's half of not-said, written in the first call
beside the analysis). The first two and the summary are written by the client's layer's call
(`jyotish.client`), which sees only the accepted analysis and claims and the values of the facts they
cite, and is checked like the summary; every sentence carries the tags of what it draws on. The split
is new: the paragraph used to end with the timing, and now the timing is its own part (`when` in the
client's draft and on the area, `when_cites`, a gap of kind `when` when it never passes; an area with
no accepted timing has none), and the paragraph refuses a date ("dates go under When"). The client's
words are wider than before: besides vote, family, term, percentile, learned score, house system and
sample, none of cusp, sub-lord, arudha, dasha, Shadbala, Bhava Bala or rupa (`client.CLIENT_WORDS`). A
Sanskrit word that has a plain phrase is refused for the phrase (`client.CLIENT_PLAIN`: lagna, the
rising sign; bhava, house; kendra, angular house; trikona, trine house; karaka, significator; varga,
divisional chart; and rashi, graha, gochara, uccha, neecha, swakshetra), except inside a rule's own
name (Kendra-Trikona Raja yoga) or a term (marana karaka sthana, chara karaka). A Sanskrit term with no
plain phrase (`client.SANSKRIT_TERMS`, from the glossary: the yogas, nakshatra, navamsa, vargottama,
marana karaka sthana, tara, panchanga and the rest) is allowed only with its gloss in the same
sentence, right after it (", a combination formed when …" or "(…)"), and the checker receives the
term's glossary definition beside the sentence, so the gloss is checked against it. Which terms have
a plain phrase is the list's decision, not the writer's: a term moves from one list to the other by an
edit with its reason. At astrologer and curious depth the existing paragraph stays as it was. The
Markdown page and the site head the three parts with the same words (page.CLIENT_SAYS and
web/js/strings.js's client.* keys).

**The astrologer's technical sheet (part 2).** Per area, fifteen numbered points written by the engine
from the whole-chart payload with no model call (`jyotish.sheet.build`; `ReadingArea.sheet`): (1) the
area's houses from the lagna, the Moon and the Sun, with Bhava Bala rupas and rank of 12; (2) the lords
with sign, degree, house, dignity (and compound), Shadbala ratio with its rupas, Baladi avastha,
sensitive-degree flags, retrograde, combust and roles; (3) the karakas the same way, the main one
first; (4) every rule and placement fired on the area's themes, with its planets, text, edition,
chapter and verse (or "not yet located") and whether the verse was read, status, scale and the reason
for each reduction; (5) the area's vargas with each planet's sign and dignity, the varga lagna and its
birth-time stability, and the vargottama planets; (6) nakshatra, pada, lord and tara of the primary
lord and the main karaka, their three dispositor chains with the finals, and the activation sets of the
running major and sub-period; (7) KP: the cusp's star and sub-lord, matter and denial houses, each
level's planet with its significations and outcome, the verdict; (8) Jaimini: each arudha with its
house, occupants and benefics, the verdict and why; (9) the panchanga lords and the houses they rule,
and which of the area's houses they rule; (10) the family votes as a table (family, vote, what it rests
on in one line, percentile against 10,000 charts); (11) the running periods in Vimshottari (three
levels), Yogini and Chara, each lord's dignity, tara and activation, and every window with score, q,
t, periods, dignity_of, confidence and tags, and the span to avoid; (12) every transit span of
Saturn, Jupiter and the nodes over the range with its house from the Moon and the lagna, BAV and grade,
the named transit windows and the tara rows; (13) the reading's weighing sentences, verbatim and
marked (depth full writes them; at the other depths the point says there are none); (14) the area's
three stability numbers and every fired rule or placement whose ayanamsa or house-system stability is
below 1; (15) the drafts, the abstaining families and every not_computed entry. Each item is one or two
lines and cites the payload paths it reads; a test resolves every one. Sanskrit terms are written as
the texts use them, the English beside on first use in the area's sheet. The sheet needs only the
chart, so it is made at every depth: the service attaches it to every reading (`narrate.with_sheets`),
`upgrade_reading` gives one to a reading made before it, and the Markdown page makes one from the chart
when the reading has none. The payload behind it is kept for the last few charts
(`fullchart.cached_payload`), about two seconds to build once. On the Markdown page every area now has
one toggle, "For the astrologer", holding the sheet, then (depth full) the model's analysis sections,
then the findings; it is open where the area has no client's view (astrologer depth) or the client's
paragraph is a gap. `tests/test_sheet.py` reads every point's figures against the chart object itself.
