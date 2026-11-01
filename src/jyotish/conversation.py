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

