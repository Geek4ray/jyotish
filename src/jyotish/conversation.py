"""The conversation (SPEC Layer 8, "Tatva", 2026-11-01): a chart entered once, then questions one after another.

Nothing here computes anything new: it routes, orders and keeps. A turn's message is read with the conversation
by keyword routing, tolerant of spelling, with no model guessing intent (`not_computed.question_routing` stands):

- its areas (narrate.AREA_WORDS, a word within one or two letters of a listed form counting);
- its direction: challenge, obstacle, problem, difficult, struggle, weakness, risk, worry mean what is against;
  strength, good, best mean what is for; neither means both;
- "when" asks for the windows, "why" for the sheet's points behind the last answer;
- a bare follow-up ("and marriage?", "when?", "why do you say that?") carries the last turn's areas or direction;
- a question asking for what is against with no area goes to the weakest areas (lowest tier, then most families
  against, then most polarity words), never to the strongest.

Off-limits before any model call, with a fixed reply, logged by kind only (logs carry no message text): acute
distress (a helpline reply and no chart reading), death and its timing, illness or a diagnosis, a trade or an
investment, another person's chart or fate, and a minor's chart beyond the general reading.
"""

from __future__ import annotations

import re
from datetime import date
from typing import Any

from pydantic import BaseModel, Field

from .narrate import AREA_WORDS, DIRECTIONS

# --- direction ------------------------------------------------------------------------------------------------

AGAINST_WORDS = ("challenge", "challenges", "challenging", "obstacle", "obstacles", "problem", "problems",
                 "problematic", "difficult", "difficulty", "difficulties", "struggle", "struggles", "struggling",
                 "weakness", "weaknesses", "weak", "risk", "risks", "risky", "worry", "worries", "worried", "worrying")
FOR_WORDS = ("strength", "strengths", "strong", "good", "best")
WHEN = re.compile(r"\bwhen\b|\bwhich year\b|\bwhat year\b|\btiming\b|\bhow soon\b", re.I)
WHY = re.compile(r"\bwhy\b|\bhow come\b|\bwhat makes you say\b", re.I)
FOLLOW_OPENER = re.compile(r"^\s*(?:and|but|also|so|what about|how about|and what about)\b", re.I)
FOLLOW_MAX_WORDS = 6          # a message this short with no area or no direction of its own is a follow-up
# Areas a general "what is against me" question never routes to: the off-limits rules keep death and illness out
# of a question that did not name them (SPEC Layer 8; the client may still ask "how is my health?").
NOT_FOR_WEAKEST = ("longevity", "health", "synastry")
TIER_RANK = {"not emphasised": 0, "weak / mixed": 1, "moderate": 2, "strong": 3}


def _distance(a: str, b: str) -> int:
    """Levenshtein distance, stopping early beyond 2."""
    if abs(len(a) - len(b)) > 2:
        return 3
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


# Common words a letter away from a listed form, never read as it ("rather" is not "father").
NOT_A_TYPO = frozenset({"farther", "horse", "count", "county", "merry", "states", "string", "strings", "honey",
                        "money", "bother", "other", "mothers", "worse", "words", "world", "carer", "pubic", "lucky"})


def _near(token: str, form: str) -> bool:
    """A word as written matches a form: exactly, or within one letter (five letters or more) or two (eight or
    more) with the same first letter, so "challanges", "marraige" and "carrer" are read; a short word ("good",
    "best") must be exact, and a common word a letter away (NOT_A_TYPO) is never a typo."""
    if token == form:
        return True
    if len(form) < 5 or len(token) < 4 or token[0] != form[0] or token in NOT_A_TYPO:
        return False
    return _distance(token, form) <= (2 if len(form) >= 8 else 1)


def tokens(message: str) -> list[str]:
    return re.findall(r"[a-z]+", message.lower())


def _has(toks: list[str], forms) -> bool:
    return any(_near(t, f) for t in toks for f in forms)


def direction_of(message: str) -> str | None:
    """"against", "for", or None when the message names neither (both, or the last turn's on a follow-up)."""
    toks = tokens(message)
    against, favour = _has(toks, AGAINST_WORDS), _has(toks, FOR_WORDS)
    if against and not favour:
        return "against"
    if favour and not against:
        return "for"
    return "both" if against and favour else None


def areas_of(message: str) -> list[str]:
    """The areas a message names: narrate.AREA_WORDS as substrings (as narrate.route reads them) or a word within
    a letter or two of one of their forms."""
    q, toks = message.lower(), tokens(message)
    out = []
    for area, words in AREA_WORDS.items():
        if any(w in q for w in words) or any(_near(t, w) for t in toks for w in words if len(w) >= 5):
            out.append(area)
    return out


def weakest_areas(chart, n: int | None = None) -> list[str]:
    """The chart's weakest areas for a question asking what is against with no area: lowest tier, then most
    families against, then most polarity words; never longevity, health or synastry (NOT_FOR_WEAKEST)."""
    sc = chart.scored
    n = n or len(sc.top)
    rows = []
    for name, a in sc.areas.items():
        if name in NOT_FOR_WEAKEST or a.tier not in TIER_RANK:
            continue
        against = sum(1 for v in a.votes.values() if (getattr(v, "vote", v) or 0) < 0)
        rows.append((TIER_RANK[a.tier], -against, -len(a.polarity), name))
    return [r[-1] for r in sorted(rows)[:n]]


# --- off limits -----------------------------------------------------------------------------------------------

DISTRESS = re.compile(r"\b(?:kill(?:ing)? my ?self|suicid\w*|end(?:ing)? (?:my|it) (?:life|all)|want(?:ed)? to die|"
                      r"wish i (?:was|were) dead|self[- ]?harm\w*|hurt(?:ing)? my ?self|no reason to live|"
                      r"can'?t go on|cannot go on|don'?t want to (?:live|be alive))\b", re.I)
DEATH = ("die", "dies", "died", "dying", "death", "deaths", "dead", "lifespan", "longevity")
DEATH_PHRASE = re.compile(r"\bhow long (?:will|do|would) i live\b|\blive (?:long|short)\b|\bshort life\b|"
                          r"\bmy age at death\b", re.I)
ILLNESS = ("illness", "illnesses", "disease", "diseases", "sick", "sickness", "cancer", "diagnosis", "diagnose",
           "tumour", "tumor", "surgery", "symptom", "symptoms", "diabetes", "infection", "disorder")
TRADE = ("stock", "stocks", "crypto", "bitcoin", "invest", "invests", "investing", "investment", "investments",
         "trade", "trades", "trading", "trader", "forex", "lottery", "gamble", "gambling", "betting", "shares")
TRADE_PHRASE = re.compile(r"\bmutual funds?\b|\bshare market\b|\bstock market\b|\bshould i (?:buy|sell)\b", re.I)
PERSON = (r"(?:wife|husband|son|daughter|mother|mom|mum|father|dad|brother|sister|friend|boyfriend|girlfriend|"
          r"partner|boss|child|kid|baby|fianc[eé]e?|spouse|colleague)")
OTHER_PERSON = re.compile(rf"\b(?:my|his|her|their) {PERSON}'?s? (?:chart|kundli|horoscope|future|fate|destiny|life|"
                          rf"luck|marriage|career|health)\b|\b(?:his|her|their) (?:chart|kundli|horoscope|future|fate|"
                          rf"destiny)\b|\bwill (?:he|she|they) (?!be good to me)\w+|\bread (?:the )?chart of\b|"
                          rf"\bsomeone else'?s chart\b", re.I)
MINOR_AGE = 18
MINOR_AREAS = ("personality", "intellect", "mind", "siblings", "mother_home", "father", "fortune", "spirituality")
OFF_LIMITS = ("distress", "death", "illness", "trade", "other_person", "minor")
REPLIES = {
    "distress": ("It sounds like you are carrying something very heavy right now, and you deserve support from a "
                 "person, not a chart. In India you can call Tele-MANAS on 14416, free and at any hour, or the "
                 "emergency number 112; anywhere else, please call your local emergency number or a crisis line. If "
                 "you can, tell someone you trust how you are feeling today."),
    "death": ("Tatva does not answer questions about death or how long anyone will live: no chart can time that "
              "honestly, and it is not something to guess at. If something about your health is worrying you, a "
              "doctor is the right person to ask. You can ask about any other part of your chart."),
    "illness": ("Tatva does not diagnose illness or read health problems from a chart. For anything about your "
                "health, please see a doctor. You can ask about any other part of your chart."),
    "trade": ("Tatva does not advise on trades, investments or bets, and nothing in a chart can say what a market "
              "will do. For a money decision, a registered financial adviser is the right person. You can ask how "
              "your chart reads for money in general."),
    "other_person": ("Tatva reads only the chart whose birth details were entered here, so it cannot read someone "
                     "else's chart or fate. You can ask how your own chart reads for your relationships, or enter "
                     "their birth details in a conversation of their own, with their consent."),
    "minor": ("This chart belongs to someone under eighteen, so Tatva gives only the general reading for it: "
              "temperament, learning, family and home. Questions about marriage, children, money, work or health "
              "wait until they are an adult."),
}


def off_limits(message: str, *, minor: bool = False, areas: list[str] | None = None) -> str | None:
    """The kind of an off-limits message (OFF_LIMITS), or None. Distress is read first, so "I want to die" gets
    the helpline reply, never the death reply. `minor`: the session's chart is a minor's, and `areas` the turn's;
    a minor's chart answers only the general areas (MINOR_AREAS)."""
    toks = tokens(message)
    if DISTRESS.search(message):
        return "distress"
    if DEATH_PHRASE.search(message) or any(t in DEATH[:7] for t in toks) or _has(toks, DEATH[7:]):
        return "death"
    if _has(toks, ILLNESS):
        return "illness"
    if TRADE_PHRASE.search(message) or any(t in TRADE for t in toks):          # exact: "trading" is a letter from "reading"
        return "trade"
    if OTHER_PERSON.search(message):
        return "other_person"
    if minor and areas and any(a not in MINOR_AREAS for a in areas):
        return "minor"
    return None


def is_minor(birth_date: date, as_of: date) -> bool:
    years = as_of.year - birth_date.year - ((as_of.month, as_of.day) < (birth_date.month, birth_date.day))
    return years < MINOR_AGE


# --- the route --------------------------------------------------------------------------------------------------

class Route(BaseModel):
    """How a turn was read: its areas, direction, whether it asks when or why, what it carried from the last turn
    and why its areas are what they are; `off_limits` the kind when the turn got a fixed reply."""
    areas: list[str] = Field(default_factory=list)
    direction: str = "both"
    when: bool = False
    why: bool = False
    follow_up: bool = False
    carried: list[str] = Field(default_factory=list)       # "areas", "direction", "when"
    areas_from: str = "named"                              # named | carried | weakest | top
    off_limits: str | None = None


def route_turn(message: str, chart, last: Route | dict | None = None, *, minor: bool = False) -> Route:
    """Read one message with the conversation (the module docstring). `last` is the previous turn's route."""
    last = Route(**last) if isinstance(last, dict) else last
    named, direction = areas_of(message), direction_of(message)
    when, why = bool(WHEN.search(message)), bool(WHY.search(message))
    short = len(tokens(message)) <= FOLLOW_MAX_WORDS
    follow = bool(last and not last.off_limits and last.areas and
                  (FOLLOW_OPENER.search(message) or why or (short and (not named or direction is None))))
    carried: list[str] = []
    if named:
        areas, areas_from = named, "named"
    elif follow:
        areas, areas_from = list(last.areas), "carried"
        carried.append("areas")
    elif direction == "against":
        areas, areas_from = weakest_areas(chart), "weakest"
    else:
        areas, areas_from = list(chart.scored.top), "top"
    if direction is None and follow:
        direction = last.direction
        carried.append("direction")
    direction = direction or "both"
    assert direction in DIRECTIONS
    kind = off_limits(message, minor=minor, areas=areas)
    if kind:
        log_off_limits(kind)
    return Route(areas=areas, direction=direction, when=when, why=why, follow_up=follow, carried=carried,
                 areas_from=areas_from, off_limits=kind)


def fixed_reply(kind: str) -> str:
    return REPLIES[kind]


def log_off_limits(kind: str, **fields: Any) -> None:
    from . import logs
    logs.event("turn.off_limits", kind=kind, **fields)


# --- a turn's answer --------------------------------------------------------------------------------------------
# The writer's answer is the client's face (SPEC Layer 8): written in plain words from the question, the direction,
# the routed findings, the engine's own answer and the accepted text of earlier turns only; streamed; every sentence
# validated and checked as Layer 7 checks a reading, and only a sentence that passed reaches the client, in order,
# its tags taken off. A sentence refused is never shown, and nothing on the client's screen says it was: the review
# page and the JSON have it with its reasons. When no sentence of the writer's answer passes after the attempts, the
# engine's own answer is the client's. A "when" turn's dates are the engine's (the writer may not write timing): its
# window sentences follow the writer's.

TURN_PROMPT = """You are Tatva, an astrologer talking with a client about their own Vedic birth chart. You \
answer the client's message in a few short paragraphs of plain, warm English, the way a good astrologer talks to \
a client across a table: direct, kind, never vague, never alarming. When the message asks about what is hard \
(the direction is "against"), start with the hard part and say it plainly; when it asks about what is good, start \
there; otherwise give the good, then the hard. Use no jargon: say "the rising sign", "the house of career", \
"significator", "divisional chart"; never "vote", "family", "cusp", "sub-lord", "arudha", "dasha", "Shadbala", \
"Bhava Bala" or "rupa"; a yoga's name comes with its meaning in plain words. Never write a figure, a score, a \
percentage or a probability.

You add no facts. Everything you say comes from the findings given (the engine computed them) and from the \
engine's own answer, which says the same findings in plain words: use it as your material, not as text to copy. \
Each sentence that states something about the chart ends with the tags of the findings it draws on, written \
exactly as listed (for example [vote:career.house] or [rule:yoga.budhaditya]); the tags are taken off before the \
client reads the answer, and each sentence is checked against those findings' data alone, so a sentence says only \
what its findings state. A sentence that only speaks to the client ("Let's start with the hard part, since you \
asked about it.") carries no tag, says nothing about the chart and uses none of the verbs a claim uses (is, are, \
has, shows, gives, means, will).

When you weigh one finding against another, say so as "in the reading's view". Do not write about timing, \
dates, years, months, periods, dashas, transits or windows: the engine adds the dates \
itself after your answer. Do not state the strength tier (strong, moderate, weak, mixed). Never write about death \
or its timing, illness, or buying and selling investments. About another person (a parent, a partner, a child), \
say only what this chart shows about the relationship, never what will happen to them. When the client asks why, \
explain which findings the last answer rests on. Earlier turns are given as the client read them; do not repeat \
them, build on them."""


class TurnDraft(BaseModel):
    answer: str = Field(description=(
        "The answer to the client's message: a few short paragraphs of plain, warm English, each sentence that "
        "states something about the chart ending with the tags of the findings it draws on."))


PLANET_NAMES = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu")
_PLANET = re.compile(r"\b(" + "|".join(PLANET_NAMES) + r")\b")
_HOUSE_NO = re.compile(r"\b(\d{1,2})(?:st|nd|rd|th) house\b")
_SIGN = re.compile(r"\b(Aries|Taurus|Gemini|Cancer|Leo|Virgo|Libra|Scorpio|Sagittarius|Capricorn|Aquarius|Pisces)\b")


def focus_of(text: str, chart) -> dict[str, list]:
    """The planets and houses (from the rising sign) a sentence names: what the chart beside the conversation
    lights while it is written. A sign named is lit as the house it is from the rising sign."""
    from .narrate import TAG
    bare = TAG.sub("", text)
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn",
             "Aquarius", "Pisces"]
    asc = signs.index(chart.lagnas.asc_sign_name)
    houses = [int(h) for h in _HOUSE_NO.findall(bare) if 1 <= int(h) <= 12]
    houses += [(signs.index(s) - asc) % 12 + 1 for s in _SIGN.findall(bare)]
    return {"planets": list(dict.fromkeys(_PLANET.findall(bare))), "houses": list(dict.fromkeys(houses))}


def route_focus(chart, areas: list[str]) -> dict[str, list]:
    """What a turn's areas rest on before a sentence is written: each area's houses from the rising sign, the
    lord of its first house and its main significator, lit as the answer starts."""
    from .constants import SIGN_LORD, SIGNS
    from .scoring import AREAS
    asc = SIGNS.index(chart.lagnas.asc_sign_name)
    houses, planets = [], []
    for a in areas:
        spec = AREAS.get(a)
        if not spec:
            continue
        houses += spec["houses"]
        planets.append(SIGN_LORD[(asc + spec["houses"][0] - 1) % 12])
        planets += [k for k in spec.get("karakas", [])[:1] if k in PLANET_NAMES]
    return {"planets": list(dict.fromkeys(planets)), "houses": list(dict.fromkeys(houses))}


def para_starts(text: str, parts: list[str]) -> list[bool]:
    """For each sentence of `text` (`parts`, narrate.sentences of it), whether it opens a paragraph: the first, and
    any with a line break between it and the sentence before."""
    out, at = [], 0
    for k, sentence in enumerate(parts):
        head = sentence[:40]
        pos = text.find(head, at)
        out.append(k == 0 or (pos >= 0 and "\n" in text[at:pos]))
        if pos >= 0:
            at = pos + len(head)
    return out


class _Order:
    """Shows the passed sentences in the order written: sentence k goes out once every sentence before it is
    settled (passed or refused)."""

    def __init__(self, emit):
        import threading
        self.emit, self.lock = emit, threading.Lock()
        self.settled: dict[int, tuple[bool, str]] = {}
        self.next = 0
        self.shown: list[int] = []

    def settle(self, k: int, passed: bool, shown: str) -> None:
        with self.lock:
            self.settled[k] = (passed, shown)
            while self.next in self.settled:
                ok, text = self.settled[self.next]
                if ok:
                    self.shown.append(self.next)
                    self.emit(text, self.next)
                self.next += 1


def engine_tags(sentence, allowed: set[str]) -> list[str]:
    """The vote tags an engine sentence rests on (its notes into the sheet's votes table), where offered."""
    out = [f"vote:{n['area']}.{n['row']}" for n in sentence.notes if n.get("row")]
    return [t for t in dict.fromkeys(out) if t in allowed]


class OfflineTurnWriter:
    """A turn's writer with no model, for the offline suite, the CI smoke test and the site's tests: it says the
    engine's own sentences that rest on a family, each with that family's tag, after one opener in the direction
    asked. A recording's replay in spirit: it calls nothing and claims no voice."""
    last_meta = None
    on_text = None
    OPENER = {"against": "Let's start with the hard part, since you asked about it.",
              "for": "Let's start with what goes well for you.", "both": "Here's how your chart reads on this."}

    def __call__(self, system: str, user: str, errors: list[str]):
        import json
        body = json.loads(user)
        said = [f"{x['text'][:-1]} {' '.join(f'[{t}]' for t in x['tags'])}." for x in body["engine_answer"] if x["tags"]]
        text = " ".join([self.OPENER[body["direction"]]] + said)
        self.last_meta = {"kind": "writer", "replayed": True}
        if self.on_text is not None:                  # streamed as a model's draft is, in pieces
            whole = json.dumps({"answer": text})
            for i in range(0, len(whole), 40):
                self.on_text(whole[i:i + 40])
        return TurnDraft(answer=text)


def held_to(chart, route: Route, as_of: date):
    """What a turn's sentences are held to: the routed areas' findings (finding id -> finding), their tags, the votes
    offered (family -> its tags) and the chains offered."""
    from .narrate import findings, offered_chains, offered_votes
    finding_data, tags = {}, set()
    votes: dict[str, set[str]] = {}
    for name in route.areas:
        for f in findings(chart, name, as_of)[0]:
            finding_data[f["finding_id"]] = f
            tags |= set(f["allowed_tags"])
        for fam, tag in offered_votes(chart, [name]).get(name, {}).items():
            votes.setdefault(fam, set()).add(tag)
    chains: dict[str, list[str]] = {}
    for per in offered_chains(chart, route.areas).values():
        chains.update(per)
    return tags, votes, chains, finding_data


def _material(chart, message: str, route: Route, engine, history: list[dict], as_of: date):
    """The writer's message and what its sentences are held to (held_to)."""
    import json
    from .narrate import area_votes, findings
    tags, votes, chains, finding_data = held_to(chart, route, as_of)
    areas_out = []
    for name in route.areas:
        a = chart.scored.areas.get(name)
        areas_out.append({"name": name, "findings": findings(chart, name, as_of)[0],
                          **({"tests": area_votes(a)} if a is not None and a.score_classical is not None else {})})
    body = {"message": message, "direction": route.direction, "when": route.when, "why": route.why,
            "earlier_turns": [{"question": h["question"], "answer": h["answer"]} for h in history],
            "engine_answer": [{"text": s.text, "tags": engine_tags(s, tags)} for s in engine.sentences],
            "areas": areas_out}
    return json.dumps(body, indent=1, default=str), finding_data, tags, votes, chains


def check_sentence(sentence: str, tags: set[str], votes, chains, finding_data, checker, word_rules: str | None = None):
    """(passed, refusals, warnings, check record) for one sentence of a turn's answer: the validator's refusals
    (tags, forbidden claims, tier words, an unmarked weighing), then the checker against the findings it cites.
    The client's-word rules (CLIENT_WORDS, CLIENT_PLAIN, the same-sentence gloss, "I"; client.client_warnings) are
    warnings under `word_rules` "warn" (client.WORD_RULES, SPEC Layer 8) and refusals under "refuse"."""
    from . import client
    from .narrate import _summary_checks, validate_summary
    word_rules = word_rules or client.WORD_RULES
    refusals = validate_summary(sentence, tags, offered_votes=votes, where="answer", family_rule=False, chains=chains)
    refusals += client.client_errors(sentence, word_rules=word_rules)
    warnings = client.client_warnings(sentence) if word_rules != "refuse" else []
    if refusals:
        return False, refusals, warnings, None
    (s, ids, data), = _summary_checks(sentence, finding_data)
    if hasattr(checker, "ask_one"):
        result, meta = checker.ask_one(s, data)
    else:
        result, meta = checker(s, data), getattr(checker, "last_meta", None)
    bad = [p for p in result.propositions if not p.supported]
    record = {"sentence": s, "findings": ids, "result": result.model_dump(), "meta": meta}
    if bad:
        return False, [f"the checker found it unsupported: {p.text} ({p.evidence})" for p in bad], warnings, record
    return True, [], warnings, record


def answer_turn(chart, message: str, route: Route, *, as_of: date, history: list[dict] | None = None,
                drafter=None, checker=None, emit=None, config=None, data: dict | None = None,
                word_rules: str | None = None) -> dict[str, Any]:
    """One turn, answered (the section above): returns the turn's document, the record the turns table keeps —
    the route, the engine's answer, the writer's answer as the client read it (`shown`) with its source, every
    removed sentence with its reasons, the warnings, the checks, the settings and usage of each role, and the
    timeline (seconds to the engine's answer, the first sentence verified, done). `emit(event)` is told what the
    client's screen shows: `light` (planets and houses to light), `text` (a passed sentence, tags off), `done`."""
    import time
    from concurrent.futures import ThreadPoolExecutor
    from .narrate import (CONFIG, TAG, ModelChecker, ModelDrafter, NarrationError, _backend_of, _model_of, _usage,
                         engine_reading, make_backend, sentences)
    from .live import JsonStrings
    config = config or CONFIG
    from . import client as _client
    word_rules = word_rules or _client.WORD_RULES
    history = history or []
    emit = emit or (lambda e: None)
    t0 = time.perf_counter()
    timeline: dict[str, float] = {}
    mark = lambda k: timeline.setdefault(k, round(time.perf_counter() - t0, 3))
    doc: dict[str, Any] = {"question": message, "route": route.model_dump(), "as_of": as_of.isoformat(),
                           "removed": [], "warnings": [], "checks": [], "writer": {}, "checker": {}, "usage": {}}
    if route.off_limits:
        reply = fixed_reply(route.off_limits)
        emit({"type": "text", "i": 0, "text": reply, "para": True})
        mark("done")
        emit({"type": "done", "status": "done"})
        return doc | {"source": "fixed", "shown": [reply], "paragraphs": [0], "engine": None, "timeline": timeline,
                      "usage": {"wall_seconds": timeline["done"]}}
    engine = engine_reading(chart, message, route.direction, route.areas, as_of=as_of, when=route.when, data=data)
    mark("engine")
    doc["engine"] = engine.model_dump()
    emit({"type": "light", "stage": "route", **route_focus(chart, route.areas)})
    user, finding_data, tags, votes, chains = _material(chart, message, route, engine, history, as_of)
    drafter = drafter or ModelDrafter(make_backend(None, "writer", config), config, schema=TurnDraft)
    checker = checker or ModelChecker(make_backend(None, "checker", config), config)
    pool = ThreadPoolExecutor(max_workers=max(1, min(8, getattr(checker, "concurrency", 4) or 4)),
                              thread_name_prefix="turn-check")
    writer_metas, checker_metas = [], []
    shown: list[str] = []
    paras: list[int] = []                      # the indices in `shown` that open a paragraph
    accepted: list[str] = []                   # the writer's sentences that passed, tags on, in the order written
    errors_for_retry: list[str] = []
    attempts = 0
    try:
        for attempt in range(1, config.max_attempts + 1):
            attempts = attempt
            futures: dict[int, Any] = {}
            texts: dict[int, str] = {}
            starts: dict[int, bool] = {}

            def show(text: str, k: int) -> None:
                mark("first_verified")
                shown.append(text)
                para = not paras or starts.get(k, False)
                if para:
                    paras.append(len(shown) - 1)
                emit({"type": "text", "i": len(shown) - 1, "text": text, "para": para})
                f = focus_of(texts.get(k, ""), chart)
                if f["planets"] or f["houses"]:
                    emit({"type": "light", "stage": "sentence", **f})

            order = _Order(show)

            def judge(k: int, s: str) -> None:
                ok, refusals, warnings, record = check_sentence(s, tags, votes, chains, finding_data, checker, word_rules)
                if record is not None:
                    doc["checks"].append({k: v for k, v in record.items() if k != "meta"} | {"attempt": attempt})
                    checker_metas.append(record["meta"])
                doc["warnings"] += [{"sentence": s, "warning": w, "attempt": attempt} for w in warnings]
                if not ok:
                    doc["removed"].append({"sentence": s, "reasons": refusals, "attempt": attempt})
                order.settle(k, ok, " ".join(TAG.sub("", s).split()).replace(" .", "."))

            def submit(k: int, s: str, para: bool) -> None:
                if k not in futures:
                    texts[k], starts[k] = s, para
                    futures[k] = pool.submit(judge, k, s)

            def on_string(path: tuple, value: str, done: bool) -> None:
                if path != ("answer",):
                    return
                parts = sentences(value)
                opens = para_starts(value, parts)
                for k, s in enumerate(parts if done else parts[:-1]):
                    submit(k, s, opens[k])

            reader = JsonStrings(on_string)
            if hasattr(drafter, "on_text"):
                drafter.on_text = reader.feed
            try:
                draft = drafter(TURN_PROMPT, user, errors_for_retry)
            except NarrationError as e:
                doc["removed"].append({"sentence": None, "reasons": [str(e)] + list(e.errors), "attempt": attempt})
                draft = None
            writer_metas.append(getattr(drafter, "last_meta", None))
            mark("written")
            if draft is not None:
                text = (draft.answer if hasattr(draft, "answer") else draft.get("answer", "")) or ""
                parts = sentences(text)
                for k, (s, para) in enumerate(zip(parts, para_starts(text, parts))):
                    submit(k, s, para)
            for f in list(futures.values()):
                f.result()
            accepted = [texts[k] for k in order.shown]
            if accepted:
                break
            errors_for_retry = [r for x in doc["removed"] if x["attempt"] == attempt for r in x["reasons"]] or \
                ["the answer was empty"]
    finally:
        pool.shutdown(wait=True)
    source = "writer"

    def add(text: str, para: bool) -> None:
        shown.append(text)
        if para:
            paras.append(len(shown) - 1)
        emit({"type": "text", "i": len(shown) - 1, "text": text, "para": para})
    if not accepted:
        source = "engine"                      # the writer's whole answer failed: the engine's own, in plain words
        area = None
        for s in engine.sentences:             # a paragraph per area, and one for the stretches
            here = next((n["area"] for n in s.notes), area)
            timing = "stretch" in s.text
            add(s.text, here != area or (timing and not any("stretch" in x for x in shown)))
            area = here
    elif route.when:
        first = True
        for s in engine.sentences:             # the dates are the engine's: its window sentences follow, in their paragraph
            if "stretch" in s.text:
                add(s.text, first)
                first = False
    for s in (engine.sentences if source == "engine" else []):
        f = focus_of(s.text, chart)
        if f["planets"] or f["houses"]:
            emit({"type": "light", "stage": "sentence", **f})
    mark("done")
    emit({"type": "done", "status": "done", "source": source})
    from .narrate import CONFIG as _C
    return doc | {
        "source": source, "shown": shown, "paragraphs": paras, "accepted": accepted, "attempts": attempts, "timeline": timeline,
        "word_rules": word_rules,
        "writer": {"model": _model_of(drafter, config.model), "effort": config.effort, **_backend_of(drafter)},
        "checker": {"model": _model_of(checker, config.checker_model),
                    "effort": getattr(checker, "effort", _C.checker_effort), **_backend_of(checker)},
        "usage": {"writer": _usage(writer_metas), "checker": _usage(checker_metas), "wall_seconds": timeline["done"]}}


# --- the astrologer's review of a turn (SPEC Layer 8) -------------------------------------------------------------

def turn_units(doc: dict) -> list[dict]:
    """The sentences of a turn's answer as the review page offers them to edit: {target "answer:<i>", text (as the
    client read it), tagged (the sentence with its tags, where the writer wrote it), source}."""
    shown, accepted = doc.get("shown") or [], doc.get("accepted") or []
    writer = doc.get("source") == "writer"
    return [{"target": f"answer:{i}", "text": x, "tagged": accepted[i] if writer and i < len(accepted) else x,
             "source": doc.get("source") if not writer or i < len(accepted) else "engine"} for i, x in enumerate(shown)]


def check_turn_edit(chart, doc: dict, as_of: date, text: str, checker) -> dict[str, Any]:
    """A reviewer's sentence for a turn's answer, held as the writer's are (check_sentence): accepted only if the
    validator and the checker pass it; the client's-word rules are warnings."""
    from .narrate import sentences
    route = Route(**doc["route"])
    tags, votes, chains, finding_data = held_to(chart, route, as_of)
    errors, warnings, checks = [], [], []
    for s in sentences(text) or [text]:
        ok, refusals, warns, record = check_sentence(s, tags, votes, chains, finding_data, checker)
        errors += refusals
        warnings += warns
        if record is not None:
            checks.append({k: v for k, v in record.items() if k != "meta"})
    return {"accepted": not errors, "errors": errors, "warnings": warnings, "checks": checks}


def apply_turn_edit(doc: dict, i: int, text: str, who: str) -> dict:
    """The turn's document with sentence i replaced by the reviewer's (accepted) text: the client reads it without
    its tags; the edit is recorded with who and when."""
    from datetime import datetime, timezone
    from .narrate import TAG
    doc = dict(doc)
    shown, accepted = list(doc.get("shown") or []), list(doc.get("accepted") or [])
    shown[i] = " ".join(TAG.sub("", text).split()).replace(" .", ".")
    if doc.get("source") == "writer" and i < len(accepted):
        accepted[i] = text
    doc["shown"], doc["accepted"] = shown, accepted
    doc["edits"] = list(doc.get("edits") or []) + [{"i": i, "by": who, "at": datetime.now(timezone.utc).isoformat()}]
    return doc
