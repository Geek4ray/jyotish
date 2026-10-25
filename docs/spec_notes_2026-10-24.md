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
