# Notes for the living doc, 2026-11-01

SPEC.md is the export of the living doc and is never edited directly (CLAUDE.md). These follow
docs/spec_notes_2026-10-31.md and record how chat v1 was built against SPEC Layer 8, "The conversation
(Tatva)" (rev 128): what was built, the readings the spec leaves open and how they were settled, the
measured numbers, and what is not built yet.

## Built, in seven commits

1. **The engine's own answer** (`narrate.engine_reading`). No model, deterministic, no figure: per routed area
   the tier in plain words, how far it depends on the birth time, the families leaning the way the question asks,
   each with the derivation row it rests on, and for a "when" turn the most and least favourably scored stretches
   as months. Every sentence carries notes into the area's technical sheet: an item `{area, point, item, text}`,
   or the votes table's row `{area, point: 10, row, text}`. `EngineAnswer.footnoted()` renders them as footnotes.
   Frozen on the reference chart in tests/test_engine_reading.py (the career question, and "what are the
   challanges in my life").
2. **The route** (`conversation.route_turn`). The direction, follow-ups, the weakest areas for an "against"
   question with no area, and the off-limits kinds, each with a fixed reply and logged by kind only.
3. **Sessions and turns.** `POST /sessions`, `POST /sessions/{id}/turns`, `GET /sessions/{id}/turns/{n}/events`,
   tables `sessions` and `turns` (Alembic 0004), and a ledger row per turn (`ledger.kind`).
4. **The checks refuse wrong facts, not word choices.** `client.WORD_RULES = "warn"`.
5. **The page.** `web/chat.html`, in the look of the canvas "Tatva — website mockups".
6. **The astrologer's review of a conversation.** `/review/sessions/{id}`, edits stored as reviews rows with a
   `turn_id` (Alembic 0005), and `jyotish export-reviews` writing `turns.jsonl`.
7. **Tests and measurements.** The five-turn conversation, the Playwright run of the page, the smoke test,
   `scripts/live_timing.py --turn`, and the scorecard's turn numbers.

## Readings the spec leaves open, and how they were settled

- **Weakest areas.** The spec says "lowest tier, then most against votes, then polarity". The tier order is
  not emphasised < weak / mixed < moderate < strong. Ties go to more families against, then to more polarity
  words (delay, intensity, volatility). The number of areas is the same as the top areas (three). Longevity,
  health and synastry are never picked: the off-limits rules keep death and illness out of a question that did
  not name them, and synastry needs two charts. On the reference chart the weakest areas are father, children
  and gains, all "not emphasised", and none of them is a top area.
- **Spelling tolerance.** A word matches a listed form if it is within one letter (five letters or more) or two
  letters (eight or more) and starts with the same letter. Short words ("good", "best") must match exactly. A
  short list of common English words is never treated as a typo (`conversation.NOT_A_TYPO`: "rather" is not
  "father", "horse" is not "house"). Trade words must match exactly, because "trading" is one letter away from
  "reading".
- **Follow-ups.** A message is a follow-up when there is a last turn that was not off limits, and the message
  either opens with and/but/what about, asks why, or has six words or fewer and lacks an area or a direction. A
  follow-up carries the last turn's areas (if it names none) and its direction (if it names none). "When" is
  never carried.
- **"Why".** The route keeps the last turn's areas and direction. The engine's answer to a "why" turn gives
  every family behind those areas, for and against: these are the sheet's points the last answer rests on. The
  writer is still told the direction that was asked.
- **"When".** The writer may not write timing (Layer 7's forbidden claims). A "when" turn's answer is the
  writer's sentences followed by the engine's stretch sentences, in their own paragraph.
- **Off limits.** Distress is read first, so "I want to die" gets the helpline reply (Tele-MANAS 14416, and 112
  in India; elsewhere the local emergency number) and never the death reply. A minor is anyone under 18 on the
  session's date. A minor's chart answers only the general areas (personality, intellect, mind, siblings, home
  and mother, father, fortune, spirituality). The log line is `turn.off_limits` with the kind alone. A plain
  "how is my health?" is not off limits: only illness and diagnosis words are.
- **The client's fallback.** The engine's own answer reaches the client only when no sentence of the writer's
  answer passes after `CONFIG.max_attempts`. When some sentences pass, they stand, and the removed ones are in
  the JSON and on the review page only.
- **The chart that lights up.** At the start of a turn the page lights the routed areas' houses, the lord of
  each area's first house and its main significator. As each sentence passes, it lights the planets the
  sentence names, the houses it names, and the signs it names (counted as houses from the rising sign). The
  newest pulses until the next one, and the chart settles when the answer is done. D9 and D10, the timeline and
  installability (Layer 8 "The surface") are not built in v1.
- **The word rules everywhere.** Layer 8 states the rule for the conversation. It is applied wherever the
  client's-word rules refused before: the curious paragraph, depth full's client's layer and its list, the
  summary, a reviewer's edit and the turns. That way the benchmark measures one policy. The rule of 2026-10-24
  to -31 is the setting `client.WORD_RULES = "refuse"`, and it is still tested. Warnings are kept on the reading
  (`Reading.word_warnings`), on the turn (`warnings`) and on a reviewer's edit result, and they are logged by
  unit kind and count (`narration.word_warnings`), never with the text.

## What the benchmark keeps (step 4)

`scripts/checker_bench.py --word-rules` wrote docs/word_rules_2026-11-01.md. It covers the 157 rows, with the
gate checker (GLM-5.3-Flash at temperature 0 on DeepInfra) run live on the rows that change.

- **What the old rule threw out.** The old rule ("refuse") threw out 10 rows that the new one keeps. Three are
  true sentences: accept-18, accept-19 and accept-44. Each names a Sanskrit term without a gloss in the same
  sentence. Seven are wrong:
  - the six dasha-lord changes, whose unglossed "nakshatra" the old rule caught before their wrong lord was
    read;
  - the held paragraph's pronoun opener ("It is the 12th lord…").
- **What the checker does with them.** The checker passes all three true sentences. It refuses 6 of the 7 wrong
  ones on the facts: all six dasha-lord rows, each with the right lord named in its reason. It passes the
  pronoun opener, because "It" read against its finding is the 12th lord. That is the one sentence the new rule
  lets through that the old rule held. In a paragraph that sentence is now a warning, not a refusal (bench row
  `live-retry-sentence-leans-back`, category `leans_on_another_sentence`, now the checker's).
- **The benchmark's labels.** The three true sentences are accepted rows again, each carrying its warnings, so
  the benchmark has 67 accept rows and 90 reject rows. The validator's wording catch is 23 of 23 (it was 27 of
  27), because three `client_words` rows went back to accept and one row moved to a semantic category. False
  rejects are still 0. The validator's recall on its own (reported, not gated) fell from 0.376 to 0.278: the
  seven wrong rows are now the checker's to catch, and docs/scorecard.md has the new numbers.

## Measured

The live turns are on the deployed stack: gpt-oss-120b writing, GLM-5.3-Flash at temperature 0 checking, on
DeepInfra. Each turn is "what are the challanges in my life" on the reference chart, timed by
`scripts/live_timing.py --turn` into docs/live_timings.jsonl (kind "turn"), with each turn's record in
docs/live_2026-11-01/.

| run | writer effort | session (payload) | engine's answer | first verified sentence | done | removed | USD |
| --- | --- | --- | --- | --- | --- | --- | --- |
| turn-challenges-1 | medium | 9.0 s | 0.002 s | 31.2 s | 32.5 s | 2 of 7 | 0.0049 |
| turn-challenges-2 | medium | 11.6 s | 0.002 s | 22.9 s | 39.8 s | 3 of 7 | 0.0053 |
| turn-challenges-3 | medium | 12.1 s | 0.002 s | 36.1 s | 38.4 s | 3 of 7 | 0.0057 |
| turn-challenges-low-1 | low | 12.4 s | 0.70 s | 9.8 s | 14.5 s | 0 of 3 | 0.0030 |
| turn-challenges-low-2 | low | 11.2 s | 0.72 s | 22.0 s | 25.5 s | 5 of 8 | 0.0035 |

- **Engine time.** The engine's own answer takes milliseconds once the session's payload is made. Making the
  payload takes 9 to 12 s and happens when the session is created. The low-effort rows' 0.7 s is the cost of
  each of those runs making its own chart.
- **The writer.** The first verified sentence comes at 23 to 36 s at medium effort. Most of that is the
  writer's reasoning before its first word. The spec's "first sentences appear within seconds" is not met.
- **Low effort.** Low effort was tried and is not a clear gain: one run was quick but vague ("the children area
  is challenged by the main significator"), and the other took 22 s with 5 of 8 removed. Medium stays.
- **What the checks removed.** Every answer shown had at least three sentences, and none fell back to the
  engine's own answer.
  - **The word "weak".** It was refused in every medium run: the tier words stay refusals, and the writer
    uses "weak" despite the prompt.
  - **Wrong facts.** The checker refused them where they occurred: the Sun in Pisces in the D11 called an
    enemy sign, which the derivation gives as a friend; "several planets" in the D7 where two are named;
    "friendships", which the gains findings do not state; and an "also" that leaned on another sentence.
- **Two changes after the first run.**
  - The area label "gains and friendships" became "your gains". It had invited the friendships claim, and it
    changes the frozen challenges text.
  - The writer's prompt now names the tier words outright and asks that each sentence stand alone.
- **The removed share.** Over the three medium runs it is 0.29, 0.43 and 0.43. The next step for it is to retry
  the failed sentences alone, as a held paragraph does; this build does not do that.

The scorecard reports, per turn and as medians, the engine's seconds, the first verified sentence and the
removed share, never gated.

## Not built yet, by the spec's own list

- The ten-year "when" timeline that the client drags.
- D9 and D10 on the page.
- The astrologer's review as an order.
- Installability (PWA).
- Product analytics.
- History across sessions (v2).

The astrologer's first session runs on the deployed conversation (Layer 8), so that waits for a redeploy. The
independent review (definition of done, item 9) follows the build.

## The review of chat v1, fixed

docs/review_2026-11-01_chat.md found two critical, seven high and six medium findings and one list of smaller points;
SPEC Layer 8 (rev 130, "Decided after the independent review") settles every open reading. Each finding is fixed in
its own commit, in the order C1, C2, H1, H3, H4, H6, H7, H5, H2, M2, M3, M4, M5, M1, M6, L1, with its test in
tests/test_chat_review.py unless named otherwise.

- **C1. Long life and health are never a default route.** `conversation.top_areas` is the scored top areas without
  longevity, health or synastry (`NOT_DEFAULT`), filled from the other emphasised areas by tier and then score; on
  the reference chart a question with no area and no "against" now goes to career, marriage and debts and rivals,
  where it went to career, marriage and longevity. The weakest areas already left them out. `narrate.NO_STRETCHES`
  keeps the stretch sentences of long life and health out of the engine's answer on every route, a named one
  included ("when will my health improve" gets no stretch). Before the first question the page offers three chips
  that each name an area ("How is my career?", "What about marriage?", "When does money come in?"); the follow-ups
  ("and marriage?", "when?", "why?") come once a question is answered. The test runs every chip, "when?", "why?" and
  "what are my strengths" as first turns on the reference chart and the three synthetic births and finds no shown or
  engine sentence that mentions long life or health. The synthetic birth of 2036 is read thirty years on: a session
  dated before the birth breaks the technical sheet (the Yogini period has no current entry), which M2's server
  date now refuses.
- **C2. Distress is read first and widest.** `conversation.normalise` reads every message with its apostrophes
  straight (’ ‘ ʼ ′ ` ´), in lower case, NFKC and with its spaces collapsed, before every pattern. `DISTRESS` now
  holds, in English, "better off dead", "no point (in) living", "nothing to live for", "not worth living", "tired of
  living", "can't take it anymore", "hopeless", "worthless", "end it all" and their kin; in Hinglish (Latin script)
  marna hai/chahta, mar jaun/jana, jeena nahi chahta, jeene ka mann nahi, zindagi khatam, khudkushi, aatmahatya, jaan
  de dun, koi umeed nahi; in Devanagari मरना, मर जाऊं, जीना नहीं, जीने का मन नहीं, आत्महत्या, खुदकुशी, ज़िंदगी खत्म,
  कोई उम्मीद नहीं, निराश. `route_turn` reads distress before anything else, so a distress message is never a
  follow-up and carries nothing. The test set (46 messages: the review's table, apostrophe and case variants, English
  kin, Hinglish, Devanagari) must all reach the helpline reply, cold and after the challenges turn. **Open:** no
  published Tele-MANAS list of phrases was found (a web search on 2026-11-01 turned up general warning signs only), so
  the Hindi and Hinglish list is the review's examples and their common forms; a Hindi-speaking clinician or the
  helpline has still to read it.
- **H1. Off limits are phrases, not words.** `conversation.DEATH`, `ILLNESS`, `TRADE` and `OTHER_PERSON` are phrase
  patterns on the normalised message. Death is the client's own death or lifespan ("will I die", "my death", "how
  long will I live", "meri mrityu kab", मेरी मृत्यु), never a death in the family or a dead end. Illness is a
  diagnosis or a disease asked about ("do I have cancer", "will I get diabetes", "what disease", "will my surgery go
  well", "koi bimari"); "Cancer" next to rising, Moon, Sun, sign, ascendant or lagna, or after "in", is the sign. A
  trade is a market instrument or a bet (stocks, crypto, mutual funds, the share market or share bazaar, buying or
  selling shares, investing money or savings, the lottery, betting, satta); "my trade is carpentry", "trade
  finance", "shares my values", "invest time", "a gamble" and "should I buy a house" are ordinary. Another person
  is a question about that person's own chart, fate, life, luck, marriage, career, health or job ("my wife's
  future", "will my son get a job"). "Can't go on" is distress only at the end of the message or before "anymore",
  "like this", "any longer" or "living", so "I can't go on this trip" is answered. "Will she marry me" and "will
  they hire me" are the client's own marriage and career (`Route.third_party`; "hire", "interview" and "employer"
  are career words): the answer is read from the client's chart and ends, in its own paragraph, with
  `THIRD_PARTY_LINE` ("This is read from your own chart, so it describes your side of it; it cannot say what
  another person will decide."). The false-positive set (the review's eighteen rows and four more) must all be
  answered, and 23 off-limits phrases, Hindi and Hinglish among them, are still refused.
- **H3. The client's screen is held to the client's words.** Every engine sentence the client can see is now in
  the client's words. The "when" lines say "The most favourable stretch for marriage, as the chart reads it, runs
  from …", "The least favourable stretch runs from …" and "Neither stretch is a prediction of when you will act."
  (no "scores"). A divisional chart is "the divisional chart for marriage", with no D-code (the code stays in the
  sentence's note into the sheet), and the KP family is "the reading of the exact start of each house". The tier
  sentence carries no tier word and gives the area's overall lean ("For your career, most of the chart's
  indications agree, and on balance they lean favourably."; "This chart does not emphasise your father; on balance
  its indications lean favourably."). A house is "among the least supported", "less supported than most", "better
  supported than most" or "among the best supported" of the twelve, and a dignity "exalted, where it is at its
  best" or "debilitated, where it is least at ease", so no "weakest" or "strongest" either. The minor's reply says
  "brothers and sisters, home and parents" where it said "family and home", "family" being an engine word.
  `client.CONVERSATION_WORDS` (a D-code, a score, "Krishnamurti", "KP", the tier words and their adverbs) is added
  to `client_warnings(…, conversation=True)`, which the turn's checks use; a reading's list is unchanged (D9 and
  D10 stay its English aliases). `conversation.unbullet` drops a heading line, makes list items paragraphs and takes
  bold and code marks off a writer's answer before it is split, and `shown_text` (`client.plain`) takes any mark
  left off a sentence with its tags. The test runs `client_warnings` with the conversation's list over every engine
  sentence the client can see on the reference chart (every area, every direction, with the "when" lines, the fixed
  replies and the third-party line) and finds none, and a writer's markdown answer reaches the client unmarked. The
  frozen career, challenges and five-turn texts change with it.
