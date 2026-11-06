# Notes for the living doc, 2026-11-02

SPEC.md is the export of the living doc and is never edited directly (CLAUDE.md). These follow
docs/spec_notes_2026-11-01.md and record the fixes after Ray's first use of the live chat (2026-11-02) and the
writer bake-off that followed them, against SPEC Layer 8 (rev 132).

## What Ray's first turns showed

Ray asked "how much money will i earn in my life, will i be rich", then "whan and how". Three faults were the
writer's, and one was the route's:

- The answer copied the engine's vote lines back to the client: "The image point of wealth is marked as
  against.", "The overall wealth indications are for.", "(arudha)". The writer was given the findings' whole
  data, area votes and family labels included.
- "whan" was not read as "when". The follow-up was routed as a plain follow-up, and its answer repeated the
  first answer with no timing.
- No sentence answered the question as asked: nothing said that a chart gives no amount and no promise.

## The fixes, one commit each

1. **The writer's material is plain words only** (91678d6). The writer of a turn is given:
   - the question and what it asked about, as `asked_about` ("what is hard", "what is good", "the good and the
     hard"; never a "for" / "against" label);
   - whether it asks when, why or how;
   - the earlier turns as the client read them;
   - the engine's own answer;
   - per finding, one plain sentence of what it is and which way it leans (`conversation.finding_sentence`).

   A family's sentence is the engine's own sentence with "supports" / "works against" in place of "leans
   favourably / unfavourably". A yoga is named with its glossary meaning and the houses it joins. A draft
   placement is "a placement only, with no lean of its own". A dispositor chain is the path of sign rulers.
   Each finding is cited by a short handle (`[f3]`; `conversation.Handles`), which is put back to the finding's
   own tag before the sentence is validated and checked. The checker still reads the finding's whole data.

   On the reference chart, the money question's material is 3,654 characters (45,053 before). The engine's tier
   sentence no longer says "indications" ("For money, most of what the chart shows agrees, and on balance it
   leans favourably."). The weakest-areas opener says "works against". The test reads the material on every
   area and direction of four charts for the label words.

   *Reading settled:* "for" and "against" are refused as labels (a JSON value, "is for", "are against"), not as
   English. "Works against" is the material's own lean word, as the request gave it, and "For money, …" is a
   preposition.
2. **What the conversation never shows is refused** (8cace44). `client.NEVER_SHOW` is a set of refusals in a
   turn's answer, each refusal stating the plain words to use instead. It refuses:
   - vote(s), and family / families in the engine's sense;
   - KP, Krishnamurti, analysis, a D-code, score(s);
   - "marked as", "indications are", and a bare "is for" / "is against" closing a clause;
   - arudha, dasha, cusp, sub-lord, Shadbala and Bhava Bala.

   A refused sentence is retried alone, as a held paragraph's is. The gloss, "I", the pronoun opener,
   CLIENT_PLAIN and the rest of CLIENT_WORDS stay warnings. The engine's own sentences pass the list on four
   charts.

   The sentences on Ray's screen are benchmark rows (`where: "answer"`, category `client_words`): his two quoted
   sentences verbatim, and "(arudha)" in a sentence built for the row around the arudha finding, since the rest
   of it was not quoted. Each row carries the tag of the finding it restates, because the client's screen shows
   no tags. The two engine-word sentences the live conversation of 2026-11-01 showed under the warning rule are
   rows too ("The marriage house family is for.", "The KP analysis of the seventh house…").

   The D12 row (a true sentence naming "D12") is now a wording reject. The benchmark has 182 rows; the validator
   alone catches the six `client_words` rows with no false reject.

   *Readings settled:*
   - "Family" is refused as the engine's word and kept in the client's own sense: your family, family life,
     money and family.
   - "Every Sanskrit term without its plain phrase" is read as: these words never reach the client, and the
     refusal names the plain phrase ("say 'how others see' the area").
3. **When, why and how are read with spelling tolerance, and a follow-up adds what is new** (211261c).
   - **The readers.** "When" and "why" are read from listed forms (whan, wen, kab; wy, kyun), and from any word
     one letter off that keeps the first letter. The common words that are one letter off are excepted ("went",
     "who").
   - **"How".** It has too many common neighbours (hot, hop, hoe), so only its listed forms count (how, kaise and
     their spellings). It asks what in the chart does it, and is answered as "why" is, where it stands alone,
     closes a clause or is a short follow-up. It never asks this in "how is", "how much", "how soon" or "how
     about". `Route.how` records it, and "when and how" is both.
   - **Follow-ups.** A follow-up that carries the last turn's areas does not repeat the earlier answers. The
     engine leaves out the sentences they already said, except the caveat that closes every set of dates. A
     writer's sentence restating one is refused and retried, by the held paragraph's measure. The prompt asks for
     the reason, or what in the chart does it.
   - **Streamed verdicts.** A verdict from the streamed draft is reused only for the same sentence.

   The test: "whan and how" after the money question ends with the money stretches and restates no sentence of
   the first answer.

   *Reading settled:* a follow-up naming an area ("and marriage?") is new by its area, and the no-repeat rule does
   not apply to it. The engine's sentences about two areas are worded alike, and the measure would otherwise
   refuse them as restatements.
4. **A turn answers the question as asked** (ead9e6c). The question's kinds are read from its words
   (`conversation.kinds_of`):
   - an amount ("how much", "will I be rich", kitna, crore);
   - a yes-or-no question;
   - when;
   - why or how.

   The engine's answer opens with one fixed line per kind (`narrate.OPENING`), for example "A chart gives no
   amount and makes no promise; what it shows is how well it supports money.". A "when" line comes only where
   stretches follow it. A why or how follow-up whose reasons were all given says so: "What lies behind it is what
   the answer before set out; the chart has no further reason to add.".

   The writer is asked to open the same way, in its own words. An untagged first sentence that says what a chart
   cannot give, and names no planet, sign, house or number, is an opening (`opens_on`). It is held to the
   forbidden words and the never-show list, not sent to the checker, which has no finding to read it against.
   Where the writer's first sentence does not open so, the engine's lines open the answer (`doc.opened_by`). The
   page redraws the stored answer when the turn is done, so they reach the client. Ray's two questions join the
   conversation test, which is now seven turns.
5. **The writer bake-off** (the commit with docs/writers_2026-11-02.md).
   - **The tooling.** `scripts/live_timing.py --turn` takes `--writer`, `--writer-model` (a Claude model on the
     anthropic backend, the writer role only) and `--out`. The default conversation is now the seven turns.
     `scripts/compare_writers.py` runs that conversation on each writer, the checker unchanged (GLM-5.3-Flash at
     temperature 0). It lists DeepInfra's models first, skipping any not served, and checks the anthropic key by
     name (the SDK reads `ANTHROPIC_API_KEY`, which `.env` holds). It prints the expected cost per writer and in
     all, and stops over USD 4.
   - **The Haiku request.** `narrate.AnthropicBackend` sends Claude Haiku 5.5 no `fallbacks` and no fallback beta:
     it has no server-side refusal fallback.
   - **The writers.** gpt-oss-120b (the baseline), Qwen3.6-35B-A3B, DeepSeek-V3.2, Kimi-K2.6 and GLM-5.3 on
     DeepInfra; claude-haiku-5-5 and claude-sonnet-5-5 on the anthropic backend.
   - **New prices in `jyotish.costs`.** DeepInfra's listing gave DeepSeek-V3.2, Kimi-K2.6 and GLM-5.3, read
     2026-11-06. Haiku 5.5's comes from Anthropic's list: its 100K-or-fewer price, with cached tokens at input
     since no cache-read price is listed.

   The results are under "Measured" below. The script chooses no writer.

## Measured: the writer bake-off (docs/writers_2026-11-02.md)

Run on 2026-11-06, as of 2026-11-02, with one seven-turn conversation per writer. The worst-case estimate was USD 3.28
for all seven writers, under the USD 4 limit. This run spent USD 0.24.

**Only three of the seven writers ran to the end.** DeepInfra's account ran out of balance during Kimi-K2.6's first
turn, and it refused Kimi-K2.6 and GLM-5.3 with HTTP 402. The Anthropic account's credit balance was too low for
claude-haiku-5-5 and claude-sonnet-5-5 (HTTP 400). Those four spent nothing. Each runs again with
`scripts/compare_writers.py --only <label> …` once the accounts have credit, and the report is then rewritten with
every writer that has records. The checker runs on DeepInfra too, so until that account has balance no live turn or
reading can be checked: that includes the deployed service.

Means over the six answered turns:

| writer | first verified s | done s | removed share | USD / turn | ten turns, INR (USD 1 = INR 88) |
| --- | --- | --- | --- | --- | --- |
| gpt-oss-120b (in use) | 67.1 | 163.0 | 0.56 | 0.0060 | 5.28 |
| Qwen3.6-35B-A3B | 87.6 | 236.8 | 0.54 | 0.0256 | 22.50 |
| DeepSeek-V3.2 | 17.5 | 55.4 | 0.70 | 0.0079 | 6.95 |

All three writers ran under INR 149 a ten-turn session. INR 123.75 is left after GST at 18% and a 2% payment fee;
both rates are assumed, not quoted. gpt-oss-120b took 4.3% of that, DeepSeek-V3.2 5.6% and Qwen3.6-35B-A3B 18.2%.

No turn of the three fell back to the engine's answer. The fixes held on every writer:
- No answer carried a vote, family, tier or "marked as" label.
- Every "when" turn ended with the engine's stretches.
- Ray's two turns opened on the question: by the writer in eight of nine, and by the engine's line once (DeepSeek-V3.2
  on the money question).

What the transcripts show besides, recorded for the review and not acted on here:
- **The opening line.** Every writer copied the engine's opening line word for word rather than saying it in its
  own words.
- **Restating within an answer.** Qwen3.6-35B-A3B restated a sentence within one answer: the no-repeat rule reads
  earlier turns only. It also called houses "rooms" and planets "stars".
- **"Also".** gpt-oss-120b's sentences still lean on each other with "also" despite the prompt.
- **The voice.** The voice is still mostly one placement sentence after another.

The choice of writer is Ray's, made by reading the side-by-side turns in the report.

## Not done here

- **DoD 7.** compare_readings.py was not re-run: the reading's writer, prompt and payload are unchanged. The turn's
  writer is what changed, and it is measured by the bake-off.
- **DoD 8.** No person has yet read the client's view. Ray choosing the voice from the bake-off is the first such
  reading.
- **DoD 9.** The independent review of this batch is the next session's.
- **The distress list.** It still waits for a clinician's or the helpline's reading.
