# Independent review: chat v1 (2026-11-01)

Definition of done, item 9. Reviewed: commits ee2b4e9..2e9126a on main, against SPEC.md Layer 8 (rev 129),
docs/spec_notes_2026-11-01.md, CLAUDE.md and docs/definition_of_done.md. The reviewer did not build this work and
fixed nothing. No model call was made and no key was read.

What was done: read `conversation.py`, the Layer 8 parts of `api.py`, `db.py`, `export.py`, `outcomes.py`,
`web/chat.html` and `web/js/chat.js`, and the tests; ran the suite; probed `route_turn` and `off_limits` with 62
messages of my own (the appendix); replayed the five-turn conversation, plus a first-turn "when?" through
`answer_turn` with the offline writer; read the five live turn records in docs/live_2026-11-01/; reproduced a pool
deadlock; measured one session's payload.

Findings are listed most severe first. C = critical (a client can be harmed, or the spec's safety promise is
broken), H = high, M = medium, L = low.

---

## C1. Long life, and a "least favourable stretch for long life", reach the client on ordinary questions

**Where.** `conversation.route_turn` (`areas = list(chart.scored.top)` when no area is named and the direction is not
"against"); `NOT_FOR_WEAKEST` is applied in `weakest_areas` only. `answer_turn` appends the engine's stretch
sentences on every "when" turn, after the writer and with no check. `web/js/chat.js` `chips()` offers "when?" on
the first screen.

**What is wrong.** On the reference chart the top areas are career, marriage **and longevity**. Any message with no
area and no "against" word goes to them: "what are my strengths", "why?", "tell me about my love life", "what's bad
in my chart?", the distress messages C2 misses, and the "when?" chip. The spec puts death and its timing off limits
with a fixed reply. The builder kept longevity out of the weakest areas for that reason
(`conversation.py:39-41`), but not out of the top areas.

**Failure scenario.** A client draws their chart and taps the "when?" chip, which is shown before any question. The
route is `areas=['career','marriage','longevity'], when=True`. The answer ends with the engine's own sentences, which
no writer or checker sees:

> The stretch the chart scores most favourable for long life runs from January 2030 to June 2032.
> The stretch it scores least favourable runs from July 2035 to April 2036.

Reproduced with `answer_turn(chart, "when?", route_turn("when?", chart), …)` and the offline writer. The live path
appends the same sentences (`elif route.when:` at `conversation.py:573`). "What are my strengths" gives the writer
and the fallback "For long life, the chart's indications are moderately supportive … the main one, the 1st house
… is weaker than most of your twelve houses." On the wheel, the 8th house lights up.

**What a fix needs.** Longevity (and health) are never a default route, top or weakest. No stretch sentence for
longevity or health reaches the client, whatever the route. Remove the "when?" chip before the first turn, or give
it an area. Add a test that runs every chip, plus "when?", "why?" and "what are my strengths", as first turns on the
reference chart and on the synthetic births, and asserts that no shown sentence mentions long life.

## C2. Acute distress is missed when phones type curly apostrophes, in Hinglish, and as "better off dead"

**Where.** `conversation.DISTRESS` (`conversation.py:120-122`), and `off_limits`, which runs it on the raw message.

**What is wrong.** The regex spells `can'?t` and `don'?t` with an ASCII apostrophe. iOS and most Android keyboards
type ’ (U+2019) by default, and the product is mobile first. "Better off dead" is caught by DEATH, so it gets the
death reply, not the helpline. Hindi and Hinglish are not read at all. After any turn, a short distress message
also counts as a follow-up and gets a reading of the last turn's areas.

**Failure scenarios (probed).**

| message | route |
| --- | --- |
| `I can’t go on like this anymore` | no off-limits; a reading of career, marriage, **longevity** |
| `I don’t want to live anymore` | no off-limits; a reading of career, marriage, longevity |
| `I’d be better off dead` | `death`: "Tatva does not answer questions about death … a doctor is the right person" (no helpline) |
| `mujhe marna hai, kuch accha nahi ho raha` | no off-limits; career, marriage, longevity |
| `jeena nahi chahta ab` (after the challenges turn) | a follow-up: the challenges in father, children and gains |
| `I feel hopeless, nothing works` | a career reading ("works" contains "work") |

**What a fix needs.** Normalise apostrophes (’ ‘ ʼ ′ to ') and case before every off-limits pattern. Read "better
off dead", "no point (in) living", "end it", "hopeless" and the like as distress, before DEATH. Add a Hinglish and
Hindi distress list (marna, mar jaun, jeena nahi, khudkushi, aatmahatya, in Latin script and Devanagari), drawn up
with someone who knows the helpline's guidance. Check distress before the follow-up rule can carry anything. Keep a
distress test set (the rows above and their variants) that must all reach the helpline reply.

## H1. The off-limits rules refuse ordinary messages, including the zodiac sign Cancer

**Where.** `ILLNESS` (fuzzy matching through `_has`), `DEATH[:7]` (any token), `TRADE` (any token),
`TRADE_PHRASE` ("should i buy"), `OTHER_PERSON` (`\bwill (?:he|she|they) …`) and `DISTRESS` (`can'?t go on\b`).

**Failure scenarios (probed; each gets a fixed reply and no reading).**

| message | refused as |
| --- | --- |
| `My Moon is in Cancer, what does that mean for my mind?` | illness |
| `I'm a Cancer rising, how is my personality?` | illness |
| `I'm sick of my job, should I change careers?` | illness |
| `I failed the vehicle inspection, what about property?` | illness ("inspection" is two letters from "infection") |
| `My father died last year. How is my career looking?` | death: the reply tells a grieving client to see a doctor |
| `after my brother's death I feel lost, what about my mind` | death |
| `my job feels like a dead end` / `is my career dead?` | death |
| `my trade is carpentry, will my business grow?` | trade |
| `I work in trade finance, is my career good?` | trade |
| `should I invest time in this relationship?` | trade |
| `my partner shares my values, is marriage good?` | trade |
| `is changing careers a gamble?` | trade |
| `should I buy a house this year?` | trade (property is the mother_home area) |
| `will they hire me after the interview?` | other_person |
| `will they accept my visa application for abroad?` | other_person |
| `I can't go on this trip because of work, will my career suffer?` | distress: the helpline reply |
| `I cannot go on vacation this year, is that bad for my marriage?` | distress |

The rules are also inconsistent. "My mother passed away, will my home life settle?" is answered, while "my father
died" is refused. "Cancer" refused as an illness is the worst case: about one chart in twelve has the Moon or the
rising sign in Cancer, and the check line names that sign before the first question.

There are false negatives too: "meri mrityu kab hogi" (when will I die) and "share bazaar mein paisa lagana" (put
money in the share market) pass, and the first goes to the top areas, longevity included (C1).

**What a fix needs.** Refuse a death question about the client ("will I die", "when will I die", "my death", "how
long will I live"), not any message containing a death word. A message that mentions a death in the family gets an
answer, perhaps with one gentle line. Read "Cancer" as an illness only in an illness phrase ("have cancer", "get
cancer"), never next to rising, Moon, sign, ascendant, lagna or "in". Match trade words only in a trade phrase (buy
or sell shares, invest money, stock, crypto); "should I buy a house" routes to property. Read "will they" as another
person only with a named person. Anchor "can't go on" at the end of the message or before "anymore" or "like this".
Add a false-positive test set: the rows above must not be refused.

**A reading for Ray.** `tests/test_conversation_route.py` deliberately asserts that "will she marry me" is
other_person. It is a question about the client's own marriage, and the reply ("cannot read someone else's chart or
fate") does not fit it. Worth settling in the living doc.

## H2. "What are the challenges in my life" answers with three areas that lean supportive

**Where.** `conversation.weakest_areas` (the spec's "lowest tier, then most against votes, then polarity", built as
written), `TIER_RANK`, and `narrate.engine_reading` for direction "against".

**What is wrong.** A tier says how far the families agree, and "not emphasised" means S is below the area's
40th-percentile S in the population run (`scoring.py:50`). Neither says an area leans against. On the reference
chart all 18 areas have S > 0 ("supportive"). The three picked are:

| area | tier | direction | families for / against | polarity |
| --- | --- | --- | --- | --- |
| father | not emphasised | supportive | 2 / 3 | intensity |
| children | not emphasised | supportive | 2 / 2 | delay, intensity |
| gains | not emphasised | supportive | 3 / 2 | none |

The engine's answer for "against" gives only the families against, so the client reads three areas the engine scores
supportive as their challenges. The live writer then made outcomes of them: "showing difficulty in that
relationship" (father), "indicating obstacles in matters related to children", "creating hurdles for income and
financial growth" (removed for its "also", not for the claim).

**Would a client call these challenges?** Father, partly: its main house is one of the weakest of the twelve, and
three families are against. Children and gains, no. To a 25-year-old, "Jupiter … debilitated, where it is at its
weakest" in the children's chart reads as a statement that they will have trouble having children, and the engine
does not say that. Gains has more families for it than against. The areas with the most families against are
reputation and siblings (3 each, confidence 0), which never come up. The polarity flags a client might feel
(delay and intensity on personality, intellect, children and health) are not mentioned.

**What a fix needs.** This is a spec reading, so it is for Ray and the astrologer in the living doc. Two
suggestions: rank adverse direction first, then families against, then polarity, then tier; and when no area leans
against, have the answer say so ("no part of your chart leans against you; the parts it supports least are …"), and
give each area's overall lean beside the families that oppose it. Keep the frozen CHALLENGES text in step with
whatever is decided.

## H3. Engine words, test names and marks reach the client, and the word rules catch none of them

**Where.** The engine's stretch sentences, which `answer_turn` appends on every "when" turn. The fallback
(`source = "engine"`). `client.CLIENT_WORDS`, `ENGLISH_ALIASES` (D9, D10 and D30 are allowed). `TAG.sub` is the only
thing removed before the client reads a sentence.

**Failure scenarios.**
- Every "when" turn ends with "The stretch the chart **scores** least favourable …" and "These are the chart's
  **scores** …". The spec says the client sees no score, and the writer's prompt forbids the word.
- Live run turn-challenges-3 showed the client "In the divisional chart for your father **(D12)**, Mars falls in
  Gemini …".
- The fallback, and the material the writer copies from, carry "(D7)", "(D9)", "(D11)", "(D12)", "The Krishnamurti
  method, which reads the exact start of each house", "moderately supportive" (a tier word) and "the rulers of the
  day you were born".
- `client.client_warnings` returns [] for all of these (checked). The warnings list was empty in all five live
  turns, so the "warn" layer caught nothing that actually happened.
- Markdown from the writer would reach the client as literal characters: `narrate.sentences` keeps
  `**The Sun** … [tag].\n\n- Jupiter … [tag].` as one sentence, and only tags are stripped.

**What a fix needs.** Write the client's version of the engine's "when" sentences without "scores", as
`narrate.client_windows` does for readings. Remove D-codes and method names from every engine sentence the client
can see. Add D-codes, "score(s)" and "Krishnamurti" to the client's-word list for the conversation. Strip markdown
from a sentence before it is shown. Add a test that runs `client_warnings` over every engine sentence that can reach
the client on the reference chart (the fallback and the "when" lines, for every area) and asserts there are none.

## H4. A turn can deadlock the reading pool: reproduced

**Where.** `api.run_turn` calls `session_payload(...).result()` inside a pool worker. When `PAYLOADS` has no entry
for the session, `session_payload` submits the payload job to **the same pool**. That happens to every session after
a restart or deploy, and to a session served by another process.

**Failure scenario (reproduced in the scratchpad).** Two sessions are created, then a fresh app is made on the same
database with one worker, and one question is asked in each. After 61 s the statuses are `['running', 'queued']`,
and every later question in the first conversation gets 409. With the default two workers, two such turns that start
together (for example, queued behind a reading) hold both workers forever. Every reading and turn on the machine
then stops until a restart, and the next restart sets up the same trap. A single such turn behind a live reading
waits for that reading to finish.

**What a fix needs.** Make the payload inline in the turn's own worker (`fullchart.cached_payload` directly; it is
cached), or on a separate executor. Never block a pool worker on the pool. Add a test: a session made in one app, a
turn asked in a fresh app with `workers=1`, finishing within a time limit.

## H5. Every session's payload is held in memory for the life of the process, and POST /sessions is not rate-limited

**Where.** `PAYLOADS: dict[str, Future]` in `create_app`, which is never evicted (`fullchart._CACHE` evicts, but the
Future keeps the dict). `post_session` has no `limits.check`.

**Measured.** One payload for the reference chart takes 12.6 s and holds 4.7 MB (tracemalloc). fly.toml gives the
machine 1 GB, so about 200 conversations between deploys use up the memory. Anyone can also queue 12 s jobs on the
two-worker pool, with no token, as fast as they can post, which starves every reading and turn.

**What a fix needs.** A bounded cache (or none: rely on `fullchart._CACHE` and recompute), POST /sessions under the
rate limit, and a test that the number of payloads held is bounded.

## H6. A turn interrupted by a restart blocks its conversation for good

**Where.** `post_turn` refuses with 409 while any turn of the session is queued or running. No code marks a turn
failed or re-queues it after a restart. The SSE `finished()` returns only on done or failed.

**Failure scenario.** A deploy lands while a turn is being written. The row stays "running". Every later question in
that conversation gets 409 ("the last question is still being answered"), and the page shows "Reading your chart"
for ever. The client's only way out is to enter their birth data again.

**What a fix needs.** At startup, mark queued and running turns failed (or re-queue them), and/or treat a turn older
than a time limit as failed in `post_turn`. Add a test.

## H7. The session id is the only key to a conversation, and it is in the URL and in the logs

**Where.** `GET /sessions/{sid}`, `POST /sessions/{sid}/turns` and the turn routes have no other credential. chat.js
writes `?s=<sid>` into the address bar. `logs.safe_path` masks `/charts/<id>` but not `/sessions/<id>`, and
`session.created` logs the id.

**What follows.**
- Anyone who has the link (browser history and sync, a screenshot, a link the client shares with a friend or the
  astrologer) can read every question and answer and can ask new questions, which are stored under the client's
  birth key.
- `GET /sessions/{sid}` returns `chart_id`. That opens `/charts/{chart_id}/tables.json`, with positions to the arc
  second and the dasha table, from which the birth moment can be recovered. The logs module masks chart ids because
  they are a hash of birth data, but the session id leads straight to one.
- Anyone who can read the service's logs can read every conversation. `http.request` writes
  `/sessions/<sid>/turns/<n>/events` in full. The logs promise that "a question cannot reach a log", and that holds
  only to the letter.
- There is no expiry, no revoking and no "forget this conversation".

**What a fix needs.** Keep a session secret out of the URL (an HttpOnly cookie, or a header held in the page's
storage), separate from the id. Mask `/sessions/<id>` in `safe_path` and drop the id from `session.created`. Don't
return `chart_id` to the client, or put the chart routes behind the session secret. Add an expiry and a client-side
"forget". Add tests for each.

## M1. A conversation cannot be erased

**Where.** `outcomes.erase(session, subject_id, …)` needs a `subjects` row, and `jyotish subject erase` is the only
way in.

**What is wrong.** A chat client is not an outcome subject. Their turns (the questions, distress messages included),
the birth key and the chart cannot be erased with any command. They are kept indefinitely, and they appear in
turns.jsonl once reviewed.

**What a fix needs.** Erasure by session id and by birth key (`jyotish session erase`), logged as subject erasure
is, with a test. Decide in the spec how long turns are kept.

## M2. A minor's chart gets the minor reply for the general reading too

**Where.** `off_limits(..., minor=True, areas=…)` is checked against the routed areas, and the default routes (top,
weakest) are not limited to `MINOR_AREAS`. `SessionRequest.as_of` comes from the public request body.

**Failure scenarios (probed with `minor=True`).**
- "tell me about my chart", "what are his strengths", "what are the challenges" and "when?" all get the minor reply,
  because they route to career, marriage and longevity, or to father, children and gains.
- "how is my son's chart" gets other_person: "Tatva reads only the chart whose birth details were entered here".
  The chart entered is the son's.
- Only a message that names a general area ("how is his education") is answered.
- A caller can post a session with `as_of` years ahead, which turns a minor's chart into an adult's. That date also
  moves every "when" stretch.

**What a fix needs.** For a minor, choose the default routes from MINOR_AREAS. Don't read "my son's/daughter's
chart" as another person when the chart is a minor's. Take `as_of` from the server, or allow it only to a reviewer
or the tests.

## M3. The follow-up rule carries the last turn into fresh questions

**Where.** `follow = … (short and (not named or direction is None))` at `conversation.py:208-209`. A message of six
words or fewer that names no area is a follow-up, even when it has a direction or a question of its own.

**Failure scenarios (each after "what are the challanges in my life").**
- "what are my strengths" → father, children, gains, direction "for": the client asks for strengths and is answered
  with the weakest areas.
- "how is my health?" → health, with "against" carried, so the writer is told to start with the hard part about
  health.
- "shaadi kab hogi?" (when will I marry) → father, children, gains, against, and not read as "when".
- "jeena nahi chahta ab" → see C2.

The spec says a *bare* follow-up carries ("and marriage?", "when?").

**What a fix needs.** The short-message rule applies only when the message has neither an area nor a direction of
its own. Add a test for "what are my strengths" after an "against" turn.

## M4. The routing vocabulary sends common questions to the wrong areas, or to the strongest ones

**Where.** `AGAINST_WORDS`, `narrate.AREA_WORDS`, which `areas_of` matches as substrings, and `_near`.

**Failure scenarios (probed).**
- "what's bad in my chart?", "what should I be careful about?", "any doshas in my chart?" and "what are my
  negatives?" go to the **top** areas. The spec says such a question never goes to the strongest. "bad", "negative",
  "careful", "dosha", "issue", "trouble" and "hard" are not against words.
- "tell me about my love life" names no area: "love" is not a marriage word.
- Substrings and near-matches misroute:

  | message | read as |
  | --- | --- |
  | "I want to learn about my chart" | wealth ("learn" contains "earn") |
  | "for example, how is my marriage?" | intellect too ("exam") |
  | "I can't sleep properly" | home ("properly" is one letter from "property") |
  | "will my medication work?" | spirituality ("meditation") and career ("work") |
  | "my friend Mary …" | marriage ("marry") and gains |

- Hinglish is not read: shaadi, naukri, paisa, kab.

**What a fix needs.** Match area words as whole words or listed stems, not substrings. Extend the against list and
the area words with Ray. Whether to read Hinglish is a product decision, but the clients are in India (the helpline
reply is Indian), so it belongs in the spec either way.

## M5. The removed share, the "weak" refusals, a splitter fault and no benchmark rows for turns

**Where.** `TURN_PROMPT`, `_material` (the engine's answer is given to the writer as material), `narrate.sentences`
and `tests/fixtures/checker_bench.jsonl`.

**What is wrong.**
- **"weak".** In all three medium runs the first sentence, about the father's house, was refused for "weak". The
  material the writer is given says "one of the weakest of your twelve houses", "weaker than most" and "moderately
  supportive" (itself a tier word), while the prompt bans the tier words. The writer paraphrases its material and is
  refused for it. With no retry, the client never reads the sentence that explains the house. The removed share was
  0.29, 0.43 and 0.43.
- **The splitter.** It does not split `…purpose. [vote:father.varga]Your children’s area …` (a tag with no space
  after it). In turn-challenges-low-2 that lost four sentences to two "tags must end the sentence" refusals. The
  fault was the splitter's, not the writer's.
- **Checker verdicts.**
  - "also" is inconsistent: it was refused once (gains, run 2) and passed in "The divisional chart for your father
    **also** leans unfavourably" (runs 1 and 2), "**further** weakening" and "adding **more** strain". The prompt
    forbids all of these.
  - Outcome glosses the findings do not state passed: "showing difficulty in that relationship", "indicating
    obstacles in matters related to children".
- **No benchmark rows.** Not one of the 157 rows has `where: "answer"`, so the turn's sentence kind is not in the
  benchmark (definition of done, item 5). None of the live misses or doubtful passes above is a row.

**What a fix needs.**
- Retry the failed sentences alone, as a held paragraph does (the builder names this as the next step).
- Give the writer material without tier words, or plain substitutes for them.
- Split after `]` followed by a capital letter, and add a boundary test.
- Turn each live refusal and each doubtful pass above into a benchmark row, with a `where: "answer"` category.

## M6. The live answers are not yet in the voice the spec asks for

**Where.** docs/live_2026-11-01/*.turn.json, `shown`.

**What is wrong.** In all five runs, every sentence the client read is a placement statement in the engine's terms:
"The main significator for children, Jupiter, sits in Taurus in your 1st house, an unfriendly sign for that
purpose." There is no sentence to the client, no hard part named in plain words, and no paragraphing. Low-1 reads
"The father area shows difficulty in the house position, the main significator and the divisional chart." The spec
asks for "plain and warm, in the voice a good astrologer uses with a client". The client's view has not yet been
tried by a person (definition of done, item 8), and these records suggest it should be before the next build.

**What a fix needs.** Measure the prompt against the five-turn conversation live, not only the challenges question
(the scorecard has one question, five runs), and put a person in front of the client's view.

## L1. Smaller points

- **chat.js, when the live events are gone.** If a turn ends with no events left in this process (an SSE `done`
  from `finished()`, or polling after a restart), the page ends on "Reading your chart" and never fetches the
  stored answer. Polling fetches the turn only for its status. Fix: on `done` with no text, render from
  `GET /sessions/{sid}/turns/{n}`.
- **Two posts at once.** Both can pass the 409 check, and the second then fails the
  `UniqueConstraint(session_id, n)` with a 500 (Postgres). Fix: catch IntegrityError and return 409.
- **Unbounded history.** `history` sends every earlier turn's full text to the writer, so the cost of a long
  conversation grows each turn.
- **"why?" after a fixed reply.** It explains the last answered turn, not the refusal the client just read.
- **Logging in route_turn.** `route_turn` logs `turn.off_limits` itself, so a script or test that only routes a
  message also writes the event (`scripts/live_timing.py` does). Logging in `run_turn` would count only real turns.

---

## Checked and found sound

- **The suite.** `pytest -q` finished with 1430 passed and 5 skipped in 10 min 24 s on this checkout.
  `tests/test_conversation.py` replays the five turns: each route asserted, the engine answers frozen, the fifth the
  death reply with no writer call, and the same through the service.
- **Off limits before any model call.** `run_turn` builds no writer or checker for an off-limits route, and
  `answer_turn` returns before `make_backend`. The test counts zero writer calls.
- **"I want to die" gets the helpline.** Distress is read before death, for straight apostrophes. The reply gives
  Tele-MANAS 14416 and 112 and contains no chart reading.
- **Nothing of the working in the client's JSON or events.** `client_turn` returns only the question, status, shown
  sentences and paragraphs. The SSE stream sends `light` (planet names, house numbers), `text` and `done`.
  Removed sentences, checks, the engine's answer and warnings stay in the stored document and on the review page,
  behind a reviewer token.
- **Ordering and fallback.** `_Order` shows only passed sentences, in the order written. The engine's answer is the
  client's only when no writer sentence passed after the attempts.
- **The writer's history.** The writer is given the earlier turns' shown text only, never a removed sentence.
- **No message text in the logs.** Every `logs.event` the batch adds carries ids, a kind, counts, cost and seconds.
  `turn.failed` logs the exception's class only, and `narration.word_warnings` logs a count. The deployed CMD runs
  uvicorn with `--no-access-log`. The gap is the session id (H7), not the text.
- **No script injection.** chat.js puts every question, answer and place label on the page through `textContent` or
  `esc`.
- **The review.** Both endpoints need a reviewer token. A reviewer's sentence is held to the turn's validator and
  checker before the client reads it. Opens and edits are `reviews` rows with `turn_id`, and the chart is excluded
  from the blind set. turns.jsonl carries the route, both answers and the removed sentences.
- **Ledger and migrations.** Each turn gets one ledger row (`kind: "turn"`), the backfill covers turns, and
  `/costs/daily` counts turns apart. Alembic 0004 and 0005 apply, and the drift test passes.
- **Spelling and dates.** The tolerance rule reads "challanges", "marraige", "carrer", "dificult" and "strenghts",
  and NOT_A_TYPO keeps "rather", "horse" and "honey" out. `is_minor` is right at the birthday boundary.
- **Erasure.** For a subject who does exist, `erase` removes their sessions, turns and the turns' reviews.
- **The spec notes.** They state the shortfalls honestly: "within seconds" not met, the removed share, the "weak"
  refusals and what is not built.

---

## Appendix: the routing probe

These were run on the reference chart (`assess(…, true_node=False)`): first cold, then after the challenges turn
(whose route is father, children, gains, against). "→ fixed" means `off_limits` returned that kind.

| message | cold | after the challenges turn |
| --- | --- | --- |
| I can't go on this trip because of work, will my career suffer? | → fixed distress | → fixed distress |
| I cannot go on vacation this year, is that bad for my marriage? | → fixed distress | → fixed distress |
| I can’t go on like this anymore | career, marriage, longevity | same |
| I don’t want to live anymore | career, marriage, longevity | same |
| I’d be better off dead | → fixed death | → fixed death |
| mujhe marna hai, kuch accha nahi ho raha | career, marriage, longevity | same |
| jeena nahi chahta ab | career, marriage, longevity | follow-up: father, children, gains, against |
| I feel hopeless, nothing works | career | career, against |
| My father died last year. How is my career looking? | → fixed death | → fixed death |
| my mother passed away, will my home life settle? | mother_home | mother_home |
| after my brother's death I feel lost, what about my mind | → fixed death | → fixed death |
| my job feels like a dead end | → fixed death | → fixed death |
| is my career dead? | → fixed death | → fixed death |
| meri mrityu kab hogi | career, marriage, longevity | follow-up: father, children, gains |
| will I die early? | → fixed death | → fixed death |
| My Moon is in Cancer, what does that mean for my mind? | → fixed illness | → fixed illness |
| I'm a Cancer rising, how is my personality? | → fixed illness | → fixed illness |
| I'm sick of my job, should I change careers? | → fixed illness | → fixed illness |
| I'm a surgeon, how is my career? | career | career |
| I failed the vehicle inspection, what about property? | → fixed illness | → fixed illness |
| how is my health? | health | health, against carried |
| will my medication work? | career, spirituality | same, against |
| my trade is carpentry, will my business grow? | → fixed trade | → fixed trade |
| I work in trade finance, is my career good? | → fixed trade | → fixed trade |
| should I invest time in this relationship? | → fixed trade | → fixed trade |
| my partner shares my values, is marriage good? | → fixed trade | → fixed trade |
| is changing careers a gamble? | → fixed trade | → fixed trade |
| should I buy a house this year? | → fixed trade | → fixed trade |
| kya mujhe share bazaar mein paisa lagana chahiye | career, marriage, longevity | same |
| will they hire me after the interview? | → fixed other_person | → fixed other_person |
| will they accept my visa application for abroad? | → fixed other_person | → fixed other_person |
| will she marry me? | → fixed other_person | → fixed other_person |
| my wife's career is affecting mine, what does my chart say? | → fixed other_person | → fixed other_person |
| how is my son's future? this is his chart | → fixed other_person | → fixed other_person |
| I'm worried about my mother's health | → fixed other_person | → fixed other_person |
| shaadi kab hogi? | career, marriage, longevity | follow-up: father, children, gains |
| naukri mein kya problem hai | weakest: father, children, gains | same, carried |
| paisa kab aayega | career, marriage, longevity | follow-up: father, children, gains |
| meri carrer kaisi hai | career | career, against |
| I want to learn about my chart | wealth | wealth |
| for example, how is my marriage? | marriage, intellect | same, against |
| I can't sleep properly, why? | mother_home | mother_home, against |
| my friend Mary asked me to ask about love | marriage, gains | marriage, gains |
| tell me about my love life | career, marriage, longevity | follow-up: father, children, gains |
| what's bad in my chart? | career, marriage, longevity | follow-up: father, children, gains |
| what should I be careful about? | career, marriage, longevity | follow-up: father, children, gains |
| any doshas in my chart? | career, marriage, longevity | follow-up: father, children, gains |
| what are my negatives? | career, marriage, longevity | follow-up: father, children, gains |
| what are the challenges in my career and where am I strong | career, both | career, both |
| challenges? | weakest | follow-up, weakest |
| what about kids | children | children, against |
| when will I get a job? | career, when | career, against, when |
| why? | career, marriage, longevity | follow-up: father, children, gains, why |
| what are my strengths | career, marriage, longevity, for | follow-up: **father, children, gains**, for |

With `minor=True`:

| message | route |
| --- | --- |
| tell me about my chart | → fixed minor (top areas) |
| what are his strengths | → fixed minor |
| what are the challenges | → fixed minor (weakest areas) |
| how is my son's chart | → fixed other_person |
| how is his education | intellect, answered |
| what about his marriage | → fixed minor |
| how is my studies | intellect, answered |
| when? | → fixed minor |
