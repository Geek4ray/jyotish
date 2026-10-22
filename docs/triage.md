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

## What happens next

The engineer merges the sheet into the table and regenerates the rules:

    .venv/bin/python scripts/make_placements.py --merge-triage
    .venv/bin/python scripts/make_placements.py

A promoted row becomes `classical_unconfirmed` with its source `checked: true`, your name and
the date: from then on it carries weight in scoring (as a placement, at a third of a yoga's
confidence), and a reading may state its effect. The rule still has to earn
`data_confirmed` against dated outcomes (SPEC Layer 6); your reading confirms what the text
says, not that it is true.
