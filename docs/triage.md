# Triage of the placement rules

The engine has 252 placement rules: the lord of each house in each house (144, BPHS chapter 24)
and each planet in each house (108, Phaladeepika chapter 8). Their effect lines were drafted
from the principles those chapters apply, **before anyone read the verses**. Until a verse is
read, a rule is a *draft*: it fires and is recorded, a reading may say where the planet is and
which house it rules, but it says nothing about what that means, and it carries no weight in
any score. Your reading of the verse is what makes a rule the text's.

## What you need

- *Brihat Parashara Hora Shastra*, translated by R. Santhanam (1984), chapter 24, "Effects of
  the Bhava Lords".
- *Phaladeepika*, translated by V. Subrahmanya Sastri (1937), chapter 8, "Effects of planets in
  the twelve houses".
- `scripts/placements_triage.csv`, open in a spreadsheet. One row per rule.

## The sheet

| column | what it holds | what you do |
| --- | --- | --- |
| `id` | the rule's id | leave it |
| `placement` | the placement in words ("the lord of the 10th in the 1st", "Saturn in the 1st") | leave it |
| `draft_effect` | the engine's draft effect line | compare it with the verse; rewrite it if the verse says something else |
| `verse_reference` | edition and chapter, and the placement to look for | leave it; tell the engineer the verse number (see below) |
| `verse_read_by` | empty | your name, as it should appear in the rule's source |
| `verse_read_on` | empty | the date you read the verse, `YYYY-MM-DD` |
| `effect_confirmed` | empty | `yes` if the draft line says what the verse says; `changed` if you rewrote `draft_effect`; `no` if the verse does not support the placement as drafted |
| `practitioner_note` | empty | anything worth keeping: a condition the verse adds, a disagreement with another text, what you see in practice |

## How to read a row

1. Find the verse for the placement in the named edition. Note its number (for example
   BPHS 24.37, or Phaladeepika 8.14) in `practitioner_note` if the engineer has not yet filled
   the verse; a rule cannot be promoted without its verse.
2. Read the draft effect against the verse. Write in your own words: never copy the
   translation (it is under copyright; the engine paraphrases and cites).
3. Fill `verse_read_by`, `verse_read_on` and `effect_confirmed`. A row with all three filled and
   `yes` or `changed` is promoted; `no`, or any of the three left empty, keeps it a draft.
4. Conditions the verse attaches (only if the lord is strong, only for a malefic, cancelled
   by an aspect) go in `practitioner_note`; the engineer turns them into the rule's
   modifiers.

Work in any order; half an hour on one house's twelve lords is a good session. Rows you have
filled are kept when the sheet is regenerated.

## The sign and nakshatra rows (added 2026-10-22)

The sheet now has 147 more rows of four new kinds. They are drafts like the house rows, and they
carry no weight in any score until promoted. A reading may say where the Moon or the planet is
(or which sign rises), but nothing about what it means.

| kind | rows | what to read | the row's placement reads |
| --- | --- | --- | --- |
| the Moon in each sign | 12 | *Brihat Jataka*, tr. N. Chidambaram Iyer (1885), chapter 17 | "the Moon in Libra" |
| the Moon in each nakshatra | 27 | *Brihat Jataka*, Iyer (1885), chapter 16 | "the Moon in Chitra" |
| the planets in each sign (Sun, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu) | 96 | *Brihat Jataka*, Iyer (1885), chapter 18, with *Saravali* (Santhanam 1983) as the second source | "Saturn in Taurus" |
| the rising sign | 12 | *Saravali* (Santhanam 1983), the chapter on the twelve rising signs: its number is not yet located, so the first reader names it | "Taurus rising" |

The draft effect lines here were written from the sign's nature and its lord, the planet's
dignity in the sign, and the nakshatra's deity and class. Read them the same way as the house
rows: find the verse, compare, fill the four columns. A few things are particular to these kinds:

- *Brihat Jataka* is terse; where Iyer's notes or another commentary carry the reading, say so in
  `practitioner_note`.
- The node rows name no text: Brihat Jataka 18 and Saravali treat the seven planets in the signs,
  not Rahu and Ketu, so their source is "not yet located" and the draft lines say only that a node
  takes on its sign's colour. Name the text you follow when you find one.
- The Moon's rows are reduced when its Paksha bala is low (under 30 of 60 virupas, the measured
  brightness; a waning Moon is a dim one) and when it is debilitated. The planet rows are reduced
  by combustion and marked up when retrograde. If the verse attaches another condition, put it in
  `practitioner_note`.
- A reading offers at most one sign row and one nakshatra row per area (the strongest by theme).
  The rest stay in the learner material, so a rough row costs little while it is a draft.

## What happens next

The engineer merges the sheet into the table and regenerates the rules:

    .venv/bin/python scripts/make_placements.py --merge-triage
    .venv/bin/python scripts/make_placements.py

A promoted row becomes `classical_unconfirmed` with its source `checked: true`, your name and
the date: from then on it carries weight in scoring (as a placement, at a third of a yoga's
confidence), and a reading may state its effect. The rule still has to earn
`data_confirmed` against dated outcomes (SPEC Layer 6); your reading confirms what the text
says, not that it is true.

## Candidate rules from depth-full readings

A reading at depth full may say what a classical text holds beyond the rule library, in a sentence
ending `[tradition:<text> <chapter>]`. The engine never checks such a sentence: the client sees it
set apart, marked unverified. Each one is also appended to `data/candidate_rules.jsonl`, one JSON
row per sentence: the sentence, the citation (text and chapter), the area, the chart hash and the
reading's date and writer, with no birth data. Read the chapter it names. Where the text says what
the sentence says, the row can become a draft rule (`scripts/placements.csv` for a placement, a rule
file for anything else), with your name and the date as for the placements above. Where it does
not, tell the engineer which row: the writer's prompt can be told to stop making that kind of
claim. A candidate is a lead for you to read, never a rule until you have.
