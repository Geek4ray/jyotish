"""The conversation (SPEC Layer 8, "Tatva", 2026-11-01): a chart entered once, then questions one after another.

Nothing here computes anything new: it routes, orders and keeps. A turn's message is read with the conversation
by keyword routing, tolerant of spelling, with no model guessing intent (`not_computed.question_routing` stands):

- its areas (AREA_VOCAB: whole words, listed stems, Hinglish and Hindi; a word within one or two letters of a
  listed form counting);
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

from .narrate import DIRECTIONS

# --- direction ------------------------------------------------------------------------------------------------

# The against list grew after the review (SPEC Layer 8, M4: bad, negative, careful, dosha, issue, trouble, hard, worry),
# and Hindi and Hinglish are read for directions, "when" and "why" (the answers in English until v2).
AGAINST_WORDS = ("challenge", "challenges", "challenging", "obstacle", "obstacles", "problem", "problems",
                 "problematic", "difficult", "difficulty", "difficulties", "struggle", "struggles", "struggling",
                 "weakness", "weaknesses", "weak", "risk", "risks", "risky", "worry", "worries", "worried", "worrying",
                 "bad", "negative", "negatives", "careful", "caution", "dosha", "doshas", "dosh", "issue", "issues",
                 "trouble", "troubles", "hard", "hardship", "hardships", "danger", "warning", "warnings",
                 "dikkat", "dikkatein", "pareshani", "pareshaniyan", "mushkil", "mushkilein", "samasya", "kharab",
                 "kamzori", "kamjori", "rukawat", "badha")
FOR_WORDS = ("strength", "strengths", "strong", "good", "best", "positive", "positives", "accha", "achha", "acha",
             "achchha", "behtar", "shubh", "taakat")
AGAINST_HI = re.compile(r"समस्या|परेशानी|दिक्कत|मुश्किल|कमजोरी|कमज़ोरी|दोष|खराब|ख़राब")
FOR_HI = re.compile(r"अच्छा|अच्छी|शुभ|ताकत|ताक़त")
WHEN = re.compile(r"\bwhen\b|\bwhich year\b|\bwhat year\b|\btiming\b|\bhow soon\b|\bkab\b|\bkis saal\b|कब", re.I)
WHY = re.compile(r"\bwhy\b|\bhow come\b|\bwhat makes you say\b|\bkyun\b|\bkyon\b|\bkyu\b|क्यों|क्यूं", re.I)
FOLLOW_OPENER = re.compile(r"^\s*(?:and|but|also|so|what about|how about|and what about|aur)\b", re.I)
FOLLOW_MAX_WORDS = 6          # a message this short with neither an area nor a direction of its own is a follow-up
                              # (SPEC Layer 8, review M3: "what are my strengths" is a question of its own)
# Areas no default route goes to, top or weakest (SPEC Layer 8, decided after the review of chat v1, C1): long life
# and health reach the client only when the client names them ("how is my health?"), and synastry needs two charts.
NOT_DEFAULT = ("longevity", "health", "synastry")
NOT_FOR_WEAKEST = NOT_DEFAULT
TIER_RANK = {"not emphasised": 0, "weak / mixed": 1, "moderate": 2, "strong": 3}
DEFAULT_AREAS = 3              # areas a question with none of its own goes to (as many as scoring's top areas)


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
                        "money", "bother", "other", "mothers", "worse", "words", "world", "carer", "pubic", "lucky",
                        "properly", "medication", "mary", "friend"})


def _near(token: str, form: str) -> bool:
    """A word as written matches a form: exactly, or within one letter (five letters or more) or two (eight or
    more) with the same first letter, so "challanges", "marraige" and "carrer" are read; a short word ("good",
    "best") must be exact, and a common word a letter away (NOT_A_TYPO) is never a typo."""
    if token == form:
        return True
    if len(form) < 5 or len(token) < 4 or token[0] != form[0] or token in NOT_A_TYPO:
        return False
    return _distance(token, form) <= (2 if len(form) >= 8 else 1)


# Apostrophes as phones type them (’ ‘ ʼ ′ ` ´), read as ' before every pattern (SPEC Layer 8, review C2).
APOSTROPHES = str.maketrans({"\u2019": "'", "\u2018": "'", "\u02bc": "'", "\u2032": "'", "`": "'", "\u00b4": "'"})


def normalise(message: str) -> str:
    """A message as every pattern reads it: Unicode composed (NFKC), apostrophes straight, lower case, spaces
    collapsed. Devanagari is kept as written."""
    import unicodedata
    return " ".join(unicodedata.normalize("NFKC", message).translate(APOSTROPHES).lower().split())


def tokens(message: str) -> list[str]:
    return re.findall(r"[a-z]+", normalise(message))


def _has(toks: list[str], forms) -> bool:
    return any(_near(t, f) for t in toks for f in forms)


def direction_of(message: str) -> str | None:
    """"against", "for", or None when the message names neither (both, or the last turn's on a follow-up)."""
    toks, text = tokens(message), normalise(message)
    against = _has(toks, AGAINST_WORDS) or bool(AGAINST_HI.search(text))
    favour = _has(toks, FOR_WORDS) or bool(FOR_HI.search(text))
    if against and not favour:
        return "against"
    if favour and not against:
        return "for"
    return "both" if against and favour else None


# The conversation's words for each area (SPEC Layer 8, decided after the review of chat v1, M4): whole words, a
# listed stem (a word starting with it), Hinglish in Latin script and Hindi in Devanagari; never a substring
# ("learn" is not wealth, "example" not intellect). A Latin word within a letter or two of a word of five letters or
# more counts (_near), except the common words in NOT_A_TYPO ("properly" is not property). "Love" is marriage, and
# "will they hire me" a career question (H1). The readings' router (narrate.route) is unchanged.
AREA_VOCAB: dict[str, dict[str, tuple[str, ...]]] = {
    "career": {"words": ("career", "careers", "job", "jobs", "profession", "promotion", "promotions", "business",
                         "status", "office", "hire", "hired", "hiring", "interview", "employer", "employment",
                         "naukri", "naukari", "vyapar", "vyapaar", "dhandha", "kaam"),
               "stems": ("promot", "employ"), "hindi": ("नौकरी", "करियर", "व्यापार", "काम")},
    "marriage": {"words": ("marriage", "marry", "married", "spouse", "partner", "wedding", "relationship",
                           "relationships", "love", "romance", "romantic", "husband", "wife", "shaadi", "shadi",
                           "vivah", "rishta", "rishte", "pyar", "pyaar", "prem", "patni", "pati"),
                 "stems": ("marri",), "hindi": ("शादी", "विवाह", "रिश्ता", "प्रेम", "प्यार")},
    "wealth": {"words": ("wealth", "money", "income", "finance", "finances", "financial", "earn", "earning",
                         "earnings", "salary", "savings", "rich", "paisa", "paise", "paisaa", "dhan", "daulat"),
               "stems": (), "hindi": ("पैसा", "पैसे", "धन")},
    "health": {"words": ("health", "healthy", "illness", "vitality", "disease", "fitness", "sehat", "swasthya",
                         "tabiyat"),
               "stems": (), "hindi": ("सेहत", "स्वास्थ्य")},
    "children": {"words": ("child", "children", "kid", "kids", "progeny", "baby", "babies", "bacche", "bachche",
                           "bacha", "baccha", "santan", "aulad"),
                 "stems": (), "hindi": ("बच्चे", "संतान", "औलाद")},
    "mother_home": {"words": ("mother", "mom", "mum", "home", "house", "property", "properties", "vehicle", "car",
                              "land", "flat", "apartment", "ghar", "makaan", "makan", "maa", "mata", "gaadi"),
                    "stems": (), "hindi": ("घर", "माँ", "मां", "माता", "मकान")},
    "intellect": {"words": ("education", "study", "studies", "studying", "exam", "exams", "learning", "school",
                            "college", "university", "degree", "padhai", "padhaai", "pariksha"),
                  "stems": (), "hindi": ("पढ़ाई", "शिक्षा", "परीक्षा")},
    "foreign": {"words": ("abroad", "foreign", "travel", "visa", "overseas", "immigration", "videsh"),
                "stems": ("relocat",), "hindi": ("विदेश",)},
    "spirituality": {"words": ("spiritual", "spirituality", "moksha", "meditation", "god", "adhyatm"),
                     "stems": (), "hindi": ("आध्यात्म", "अध्यात्म")},
    "father": {"words": ("father", "dad", "papa", "pita", "pitaji"), "stems": (), "hindi": ("पिता", "पापा")},
    "siblings": {"words": ("sibling", "siblings", "brother", "brothers", "sister", "sisters", "courage", "bhai",
                           "behen", "bahen"),
                 "stems": (), "hindi": ("भाई", "बहन")},
    "reputation": {"words": ("reputation", "fame", "famous", "public", "izzat", "sammaan", "samman"),
                   "stems": (), "hindi": ("इज्जत", "इज़्ज़त", "प्रतिष्ठा")},
    "fortune": {"words": ("fortune", "luck", "lucky", "dharma", "kismat", "kismet", "bhagya", "naseeb"),
                "stems": (), "hindi": ("किस्मत", "भाग्य")},
    "mind": {"words": ("mind", "emotion", "emotions", "emotional", "mental", "feelings"), "stems": (),
             "hindi": ("दिमाग",)},
    "gains": {"words": ("gains", "network", "friends", "friendship", "friendships", "profit", "profits", "labh",
                        "laabh"),
              "stems": (), "hindi": ("लाभ",)},
    "debts_enemies": {"words": ("debt", "debts", "enemies", "enemy", "litigation", "court", "loan", "loans",
                                "rivals", "dispute", "disputes", "karz", "karza", "karja", "dushman"),
                      "stems": (), "hindi": ("कर्ज", "क़र्ज़", "दुश्मन")},
    "personality": {"words": ("personality", "self", "temperament", "nature", "character", "swabhav"),
                    "stems": (), "hindi": ("स्वभाव",)},
    "longevity": {"words": ("longevity",), "stems": (), "hindi": ()},
}
# "Work" is the client's work only as "my work", "at work", "work life" (review M4: "will my medication work?").
CAREER_WORK = re.compile(r"\b(?:my|at|from|for|in|of|to|with) work\b|\bwork ?(?:life|place|load)\b|\bworking\b")


def areas_of(message: str) -> list[str]:
    """The areas a message names (AREA_VOCAB): a listed word, a word starting with a listed stem, a Latin word
    within a letter or two of a listed word of five letters or more, or a listed Hindi word."""
    text, toks = normalise(message), tokens(message)
    out = []
    for area, v in AREA_VOCAB.items():
        if any(t in v["words"] for t in toks) or any(t.startswith(st) for t in toks for st in v["stems"]) or \
                any(_near(t, w) for t in toks for w in v["words"] if len(w) >= 5) or \
                any(h in text for h in v["hindi"]) or (area == "career" and CAREER_WORK.search(text)):
            out.append(area)
    return out


def top_areas(chart, n: int | None = None, among=None) -> list[str]:
    """The chart's strongest areas for a question with no area and no "against": the scored top areas (scoring's
    emphasis order) without longevity, health or synastry (NOT_DEFAULT), filled from the other emphasised areas by
    tier, then score. `among`: the areas allowed (a minor's chart: MINOR_AREAS), filled from any of them by tier
    and score when too few are emphasised."""
    sc = chart.scored
    n = n or DEFAULT_AREAS
    ok = lambda a: a not in NOT_DEFAULT and (among is None or a in among)
    out = [a for a in sc.top if ok(a)]
    rest = sorted((a for a, x in sc.areas.items() if (x.emphasised or among is not None) and ok(a) and a not in out
                   and x.tier in TIER_RANK),
                  key=lambda a: (not sc.areas[a].emphasised, -TIER_RANK[sc.areas[a].tier], -(sc.areas[a].score_classical or 0), a))
    return (out + rest)[:n]


def weakest_areas(chart, n: int | None = None, among=None) -> list[str]:
    """The areas a question asking what is against, with no area, goes to: "challenges" are where the chart leans
    against (SPEC Layer 8, decided after the review of chat v1, H2), so the areas whose overall direction is adverse
    first, then the most families against, then the most polarity flags (delay, intensity, volatility), then the
    lowest tier; never longevity, health or synastry (NOT_FOR_WEAKEST). When none is adverse these are the areas
    the chart supports least, and the engine's answer says so (narrate.engine_reading, `weakest`)."""
    sc = chart.scored
    n = n or DEFAULT_AREAS
    rows = []
    for name, a in sc.areas.items():
        if name in NOT_FOR_WEAKEST or a.tier not in TIER_RANK or (among is not None and name not in among):
            continue
        against = sum(1 for v in a.votes.values() if (getattr(v, "vote", v) or 0) < 0)
        rows.append((a.direction != "adverse", -against, -len(a.polarity), TIER_RANK[a.tier], name))
    return [r[-1] for r in sorted(rows)[:n]]


# --- off limits -----------------------------------------------------------------------------------------------

# Acute distress, read first and widest (SPEC Layer 8, review C2), on the normalised message: in English, then in
# Hinglish (Latin script) and Hindi (Devanagari). The Hindi and Hinglish forms are the review's and their common
# variants; no published Tele-MANAS phrase list was found (2026-11-01), so a Hindi-speaking clinician or the helpline
# has yet to read this list (docs/spec_notes_2026-11-01.md).
DISTRESS_EN = (r"kill(?:ing)? my ?self|suicid\w*|end(?:ing)? (?:my|it) (?:life|all)|(?:want|going|plan(?:ning)?) to end it|"
               r"want(?:ed)? to die|wanna die|wish i (?:was|were|could be) dead|wish i could die|"
               r"wish i (?:was|were|had) never (?:been )?born|self[- ]?harm\w*|hurt(?:ing)? my ?self|cut(?:ting)? my ?self|"
               r"no reason to (?:live|go on)|nothing (?:left )?to live for|(?:no|not any) point (?:in )?(?:living|life|"
               r"going on|being alive)|life (?:is|isn't) (?:not )?worth living|not worth living|better off dead|"
               r"better off without me|tired of (?:living|life|being alive)|(?:don't|do not|dont) want to (?:live|be alive|"
               r"exist|wake up)|can't take (?:it|this) any ?more|cannot take (?:it|this) any ?more|"
               r"(?:can't|cannot|cant) go on(?= *(?:$|[.!?,]|any ?more|any longer|like this|living|with (?:life|this)))|"
               r"give up on (?:life|living)|hopeless\w*|no hope (?:left|anymore)|worthless")
DISTRESS_HI_LATIN = (r"marn[ae] (?:hai|h|chahta|chahti|chahte|chahiye)|mar ja(?:u|un|unga|ungi|oon|na|ana|yenge)|"
                     r"mar(?:ne)? ka (?:mann?|dil) |marne ki (?:icchha|ichha|iccha|soch)|"
                     r"jee?na nahi(?:n)? (?:chahta|chahti|chahte|hai)|jee?ne ka (?:mann?|dil) nahi|"
                     r"jee?ne ki (?:icchha|ichha|iccha|wajah) nahi|zindagi (?:khatam|khatm|se tang|bekaar|bekar)|"
                     r"jindagi (?:khatam|khatm|se tang|bekaar|bekar)|khud ?khushi|khud ?kushi|a{1,2}tm?a?hatya|"
                     r"jaan de (?:du|dun|doon|dunga|dungi)|apni jaan|khud ko (?:khatam|maar|nuksan|nuksaan)|"
                     r"sab khatam kar (?:du|dun|doon|dunga|dungi)|koi umeed nahi|ummeed nahi")
DISTRESS_HI = (r"मरना|मर जा(?:ऊं|ऊँ|ऊ|ना|एंगे)|मरने का मन|जीना नहीं|जीने का मन नहीं|जीने की इच्छा नहीं|आत्महत्या|"
               r"ख़ुदकुशी|खुदकुशी|जान दे दू|ज़िंदगी खत्म|जिंदगी खत्म|ज़िन्दगी खत्म|जिन्दगी खत्म|ख़ुद को ख़त्म|खुद को खत्म|"
               r"कोई उम्मीद नहीं|निराश")
DISTRESS = re.compile(rf"(?:\b(?:{DISTRESS_EN}|{DISTRESS_HI_LATIN})|{DISTRESS_HI})")
# Off limits are phrases, not words (SPEC Layer 8, decided after the review of chat v1, H1), read on the normalised
# message. Death: the client's own death or lifespan ("a death in the family" is an ordinary message). Illness: a
# diagnosis or a disease asked about ("Cancer" the sign, "sick of my job" and "a surgeon" are ordinary). A trade: a
# market instrument or a bet ("my trade is carpentry", "should I buy a house" are ordinary). Another person: a
# question about that person's own chart, fate, health, career or future; "will she marry me" and "will they hire me"
# are the client's own marriage and career, answered from the client's chart with THIRD_PARTY_LINE.
DEATH = re.compile(r"\b(?:(?:will|shall|am|do|would) i (?:die|be dead|going to die)|when (?:will|do|would|shall) i die|"
                   r"i(?:'ll| will) die|die (?:young|early|soon|before)|my (?:own )?(?:death|lifespan|life span|"
                   r"longevity|age at death|life expectancy)|(?:early|untimely|premature|sudden) death|"
                   r"how long (?:will|do|would|shall|can) i (?:live|survive)|(?:will|do) i live (?:long|short)|"
                   r"(?:a |my )?short life|how many years (?:will|do|have) i (?:have left|live|got)|"
                   r"life expectancy|lifespan|longevity|age (?:of|at) death|"
                   r"(?:meri|mera) (?:mrityu|mirtyu|maut|aayu|ayu|umar|umr)|(?:mrityu|maut) kab|kab (?:marunga|marungi|"
                   r"maroonga)|kitni (?:umar|umr|aayu)|kitne saal (?:jiyunga|jiyungi|jeeunga))\b"
                   r"|मेरी मृत्यु|मृत्यु कब|मेरी मौत|मौत कब|मेरी आयु|कितनी उम्र|कब मरूंगा|कब मरूँगा|कब मरूंगी")
ILLNESS_WORD = r"(?:cancer|tumou?r|diabetes|disease|illness|infection|disorder|sickness|stroke|heart attack|tb|tuberculosis)"
ILLNESS = re.compile(rf"\b(?:(?:do|will|would|could|might|shall|am) i (?:\w+ ){{0,2}}(?:have|get|got|develop|suffer from|"
                     rf"catch|be diagnosed with|getting) (?:an? |any |some )?(?:\w+ )?{ILLNESS_WORD}|"
                     rf"(?:have|has|got|get|getting|develop|diagnosed with|suffering from|cure for|treatment for|"
                     rf"chance of|risk of) (?:an? |any |some )?{ILLNESS_WORD}|"
                     rf"(?:what|which|any|kind of|type of) (?:\w+ )?(?:disease|illness|sickness|health problems?|"
                     rf"disorder)s?|my (?:cancer(?! (?:rising|moon|sun|sign|ascendant|lagna))|tumou?r|disease|illness|"
                     rf"diagnosis|surgery|operation|symptoms?|infection|medication|medicines?|treatment)|diagnos(?:e|is|ed|ing)|(?:will|do|am) i "
                     rf"(?:get|fall|be|going to (?:get|fall|be)) (?:sick|ill)|health problems?|"
                     rf"(?:will|is) (?:my )?(?:surgery|operation) (?:go|be|succeed|work)|"
                     rf"(?:kaunsi|kya|koi) (?:bimari|beemari|rog)|(?:bimari|beemari) (?:hogi|hai|ho)|"
                     rf"mujhe (?:\w+ )?(?:bimari|beemari))\b|बीमारी|रोग होगा")
TRADE = re.compile(r"\b(?:stocks?|crypto\w*|bitcoin|ethereum|forex|intraday|options trading|futures trading|"
                   r"mutual funds?|ipos?|share market|stock market|share bazaa?r|sensex|nifty|lottery|casino|"
                   r"gambling|betting|satta|(?:place|make) a bet|should i (?:bet|gamble)|day trading|"
                   r"(?:buy|sell|invest in|trade|trading|purchase)(?: \w+){0,2} shares|"
                   r"invest(?:ing)? (?:my |some |the )?(?:money|savings|salary|now|today|this year)|"
                   r"(?:should|can|shall) i invest(?:\?|$| now| in (?:gold|property|real estate|the market|stocks|"
                   r"shares|crypto|bonds|funds))|paisa (?:lagana|lagau|lagaun|invest))\b|शेयर|सट्टा")
PERSON = (r"(?:wife|husband|son|daughter|mother|mom|mum|father|dad|brother|sister|friend|boyfriend|girlfriend|"
          r"partner|boss|child|kid|baby|fianc[eé]e?|spouse|colleague)")
OTHER_PERSON = re.compile(rf"\b(?:my|his|her|their) {PERSON}'?s? (?:chart|kundli|horoscope|future|fate|destiny|life|"
                          rf"luck|marriage|career|health|job)\b|\b(?:his|her|their) (?:chart|kundli|horoscope|"
                          rf"future|fate|destiny)\b|\bwill my {PERSON} (?:get|have|become|marry|pass|recover|succeed|"
                          rf"find|live|die|earn)\b(?! me\b)|\bread (?:the )?chart of\b|\bsomeone else'?s chart\b")
# On a minor's chart the person asking is a parent and the chart is the child's: "my son's chart", "his future" and
# "her studies" are about the chart entered, not another person (review M2).
CHILD = re.compile(r"\bmy (?:son|daughter|child|kid|baby)'?s?\b|\b(?:his|her)\b")


# The client's own question about what another will do ("will she marry me", "will they hire me"): answered from the
# client's chart, with this line after it.
THIRD_PARTY = re.compile(rf"\bwill (?:he|she|they|my {PERSON}|the (?:company|employer|interviewer|embassy|"
                         rf"university|college))\b")
THIRD_PARTY_LINE = ("This is read from your own chart, so it describes your side of it; it cannot say what another "
                    "person will decide.")
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
              "temperament, learning, brothers and sisters, home and parents. Questions about marriage, children, "
              "money, work or health wait until they are an adult."),
}


def off_limits(message: str, *, minor: bool = False, areas: list[str] | None = None) -> str | None:
    """The kind of an off-limits message (OFF_LIMITS), or None. Distress is read first, so "I want to die" gets
    the helpline reply, never the death reply. `minor`: the session's chart is a minor's, and `areas` the turn's;
    a minor's chart answers only the general areas (MINOR_AREAS)."""
    text = normalise(message)
    if DISTRESS.search(text):
        return "distress"
    if DEATH.search(text):
        return "death"
    if ILLNESS.search(text):
        return "illness"
    if TRADE.search(text):
        return "trade"
    if OTHER_PERSON.search(CHILD.sub("the chart's", text) if minor else text):
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
    third_party: bool = False                              # "will she marry me": THIRD_PARTY_LINE follows the answer
    explains: str | None = None                            # "why?" after a fixed reply: the kind it explains (L1)


def route_turn(message: str, chart, last: Route | dict | None = None, *, minor: bool = False,
               refused: str | None = None) -> Route:
    """Read one message with the conversation (the module docstring). `last` is the route of the last turn that
    was answered from the chart; `refused` the off-limits kind of the turn just before, when it got a fixed reply:
    a "why?" after it asks why that question was not answered (review L1), and gets WHY_REPLIES. Nothing is logged
    here: the service logs an off-limits turn when it answers one (review L1)."""
    last = Route(**last) if isinstance(last, dict) else last
    if off_limits(message) == "distress":         # before a follow-up can carry anything (review C2)
        return Route(areas=[], direction="both", off_limits="distress")
    named, direction = areas_of(message), direction_of(message)
    when, why = bool(WHEN.search(message)), bool(WHY.search(message))
    if refused and why and not named and len(tokens(message)) <= FOLLOW_MAX_WORDS:
        return Route(areas=[], direction="both", why=True, follow_up=True, explains=refused)
    short = len(tokens(message)) <= FOLLOW_MAX_WORDS
    follow = bool(last and not last.off_limits and last.areas and
                  (FOLLOW_OPENER.search(message) or why or (short and not named and direction is None)))
    carried: list[str] = []
    if named:
        areas, areas_from = named, "named"
    elif follow:
        areas, areas_from = list(last.areas), "carried"
        carried.append("areas")
    elif direction == "against":                    # a minor's defaults come from the general areas (review M2)
        areas, areas_from = weakest_areas(chart, among=MINOR_AREAS if minor else None), "weakest"
    else:
        areas, areas_from = top_areas(chart, among=MINOR_AREAS if minor else None), "top"
    if direction is None and follow:
        direction = last.direction
        carried.append("direction")
    direction = direction or "both"
    assert direction in DIRECTIONS
    kind = off_limits(message, minor=minor, areas=areas)
    return Route(areas=areas, direction=direction, when=when, why=why, follow_up=follow, carried=carried,
                 areas_from=areas_from, off_limits=kind, third_party=bool(THIRD_PARTY.search(normalise(message))))


def fixed_reply(kind: str) -> str:
    return REPLIES[kind]


# "Why?" after a fixed reply: why that question is not answered (review L1), in the client's words.
WHY_REPLIES = {
    "distress": ("Because what you wrote sounded like you are carrying a lot of pain right now, and that matters more "
                 "than any chart. Please talk to someone today: in India, Tele-MANAS on 14416, free and at any hour, or "
                 "the emergency number 112; anywhere else, your local emergency number or a crisis line."),
    "death": ("Tatva leaves out questions about death and how long anyone will live because no chart can time them "
              "honestly, and a guess could frighten or mislead you. Anything else in your chart is open to ask about."),
    "illness": ("Tatva leaves out illness and diagnosis because a chart cannot see what a doctor sees, and a wrong word "
                "about health can do real harm. Anything else in your chart is open to ask about."),
    "trade": ("Tatva leaves out trades, investments and bets because a chart cannot see what a market will do, and money "
              "lost on a chart's word is real money. You can still ask how your chart reads for money in general."),
    "other_person": ("Tatva reads only the chart whose birth details were entered here: another person's chart, fate or "
                     "future is theirs, and reading it without them would be guessing. You can ask how your own chart "
                     "reads for the relationship."),
    "minor": ("This chart belongs to someone under eighteen, so questions about marriage, children, money, work or "
              "health wait until they are an adult; temperament, learning, brothers and sisters, home and parents are "
              "open to ask about now."),
}


def history_of(earlier: list[dict], keep: int = 3) -> list[dict]:
    """The earlier turns the writer is given: the last `keep` turns' accepted text, as the client read it (review
    L1: the whole conversation made every turn dearer than the last)."""
    return list(earlier)[-keep:] if keep else []


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

# What the writer is told the client asked about: the direction in words, never a "for" / "against" label.
ASKED = {"against": "what is hard", "for": "what is good", "both": "the good and the hard"}


TURN_PROMPT = """You are Tatva, an astrologer talking with a client about their own Vedic birth chart. You \
answer the client's message in a few short paragraphs of plain, warm English, the way a good astrologer talks to \
a client across a table: direct, kind, never vague, never alarming. When the client asked about what is hard \
(`asked_about`), start with the hard part and say it plainly; when they asked about what is good, start there; \
otherwise give the good, then the hard. Use no jargon: say "the rising sign", "the house of career", \
"significator", "divisional chart"; never "vote", "family", "cusp", "sub-lord", "arudha", "dasha", "Shadbala", \
"Bhava Bala" or "rupa"; a yoga's name comes with its meaning in plain words. Never write a figure, a score, a \
percentage or a probability.

You add no facts. Everything you say comes from the findings given, each one plain sentence of what the engine \
found and which way it leans, and from the engine's own answer: use them as your material, in your own words, not \
as text to copy. Each sentence that states something about the chart ends with the tags of the findings it draws \
on, written exactly as listed (for example [f2], or [f2] [f5] for two); the tags are taken off before the client \
reads the answer, and each sentence is checked against those findings' data alone, so a sentence says only \
what its findings state and stands on its own: no "also", "too", "as well" or "again" leaning on another sentence. A sentence that only speaks to the client ("Let's start with the hard part, since you \
asked about it.") carries no tag, says nothing about the chart and uses none of the verbs a claim uses (is, are, \
has, shows, gives, means, will).

When you weigh one finding against another, say so as "in the reading's view". Do not write about timing, \
dates, years, months, periods, dashas, transits or windows: the engine adds the dates \
itself after your answer. The words strong, moderate, weak and mixed are the engine's tier words: never use them, \
in any sense ("one of the weakest" and "difficult" are yours to use). Never write about death \
or its timing, illness, or buying and selling investments. About another person (a parent, a partner, a child), \
say only what this chart shows about the relationship, never what will happen to them. When the client asks why, \
explain which findings the last answer rests on. When the engine's answer says that no part of the chart works \
against the client, say so plainly and never call a part the chart supports a challenge. Earlier turns are given \
as the client read them; do not repeat them, build on them."""


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


def unbullet(text: str) -> str:
    """A writer's answer read before it is split into sentences (review H3): a heading line dropped, list items as
    paragraphs, bold and code marks taken off, so each item is a sentence of its own and no mark reaches the client."""
    text = re.sub(r"(?m)^[ \t]*#{1,6}[ \t]+[^\n]*\n?", "", text)
    text = re.sub(r"(?m)^[ \t]*(?:[-*•]|\d+[.)])[ \t]+", "\n", text)
    return re.sub(r"\*\*|__|`", "", text).strip()


def shown_text(sentence: str) -> str:
    """A sentence as the client reads it: its tags and any markdown taken off (review H3)."""
    from .client import plain
    from .narrate import TAG
    return plain(TAG.sub("", sentence)).replace(" .", ".")


TURN_RETRY_NOTE = ("The answer is held sentence by sentence: the held sentences stand as written, in their places, "
                   "and are not sent again. Send in `answer` only the rewritten sentences, exactly one for each "
                   "sentence listed below, in the order listed, and nothing else. Each states only what its findings "
                   "state, ends with their tags, uses none of the tier words and stands on its own (no also, too, "
                   "further, more or again).")


def turn_retry_instruction(held) -> str:
    """The writer's retry of a turn (review M5): what is held, quoted with its positions, and each failed sentence
    with the reasons it failed, as narrate.retry_instruction says them for a reading."""
    from .narrate import RETRY_HEAD
    lines = [f"{RETRY_HEAD} {TURN_RETRY_NOTE}", "", f"Held: {held.held_lines() or 'nothing yet'}.", "",
             "Rewrite only these, each for the reasons quoted:"]
    for i, _, sentence, why in held.failed():
        lines.append(f"- sentence {i} ({sentence!r}):")
        lines += [f"    - {r}" for r in why]
    return "\n".join(lines)


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
    OPENER = {ASKED["against"]: "Let's start with the hard part, since you asked about it.",
              ASKED["for"]: "Let's start with what goes well for you.", ASKED["both"]: "Here's how your chart reads on this."}

    def __call__(self, system: str, user: str, errors: list[str]):
        import json
        body = json.loads(user)
        said = [f"{x['text'][:-1]} {' '.join(f'[{t}]' for t in x['tags'])}." for x in body["engine_answer"] if x["tags"]]
        text = " ".join([self.OPENER[body["asked_about"]]] + said)
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


# --- the writer's material, in plain words (2026-11-02) ----------------------------------------------------------
# Ray's first live turns showed the writer copying the engine's vote lines back to the client ("The image point of
# wealth is marked as against.", "The overall wealth indications are for."). So the writer is given plain words
# only: the engine's own answer and, per finding, one plain sentence of what it is and which way it leans
# ("supports" / "works against"), the planets and houses in the client's words. No vote, family or tier label, no
# derivation and no glossary; each finding is cited by a short handle ([f3]), which is put back to the finding's
# own tag before a sentence is validated and checked, so the checker still reads the finding's whole data.

HANDLE = re.compile(r"\[\s*(f\d+(?:\s*[,;]\s*f\d+)*)\s*\]")
_LORDSHIP = re.compile(r"the lord of the (\d{1,2})(?:st|nd|rd|th)")


class Handles:
    """The short handles a turn's writer cites ([f1], [f2] …) and the findings' own tags they stand for."""

    def __init__(self) -> None:
        self.real: dict[str, str] = {}             # handle -> the finding's tag
        self.of: dict[str, str] = {}               # tag -> handle

    def add(self, tag: str) -> str:
        if tag not in self.of:
            h = f"f{len(self.real) + 1}"
            self.real[h], self.of[tag] = tag, h
        return self.of[tag]

    def to_real(self, text: str) -> str:
        """The writer's text with each handle put back to its finding's tag (an unknown handle kept, and refused)."""
        def one(m):
            hs = re.split(r"\s*[,;]\s*", m.group(1))
            return " ".join(f"[{self.real[h]}]" if h in self.real else f"[{h}]" for h in hs)
        return HANDLE.sub(one, text)

    def to_handles(self, text: str) -> str:
        """Text for the writer (a retry's held and failed sentences and their reasons) with every tag as its handle."""
        for tag, h in sorted(self.of.items(), key=lambda x: -len(x[0])):
            text = text.replace(f"[{tag}]", f"[{h}]").replace(tag, h)
        return text


def _ords(ns: list[int]) -> str:
    from .narrate import _ORD, _and
    return _and([_ORD[n] for n in ns])


def finding_sentence(f: dict, area: str, label: str, data: dict, sheet: dict | None) -> str | None:
    """One plain sentence for a finding (the section above): what it is and which way it leans for the area, in
    the client's words. None for a finding with nothing plain to say."""
    from .narrate import (DIGNITY_PLAIN, _and, _cap, _family_sentence, _ORD, _the, glossary, rule_names)
    dig = lambda d: f", {DIGNITY_PLAIN[d]}" if d in DIGNITY_PLAIN else ""
    if f["kind"] == "vote":
        v = ((data.get("areas") or {}).get(area) or {}).get("votes", {}).get(f["family"])
        if not v or sheet is None:
            return None
        if v["vote"] in (1, -1):
            s = _family_sentence(f["family"], v, label, data, area, sheet, material=True)
            return s.text if s else None
        return None                                # a family that leans neither way is not given
    if f["kind"] == "chain":
        der = (f.get("derivation") or {}).get("sign") or {}
        if f["chain"] == "chart":
            ends = der.get("ends_in") or f.get("planets") or []
            return (f"The chain of sign rulers through your whole chart leads back to {_and([_the(p) for p in ends])}; "
                    f"it shows which planets the chart rests on, with no lean of its own.") if ends else None
        steps = der.get("steps") or []
        if not steps:
            return None
        m = _LORDSHIP.match(f.get("role", ""))
        role = (f"the ruler of the {_ORD[int(m.group(1))]} house" if m else f"the main planet that signifies {label}")
        path = ", then ".join(f"{_the(x['planet'])} in {x['sign']}" for x in steps)
        end = (f", which turns back on itself between {_and([_the(p) for p in der.get('loop_with', [])] + [_the(f['planet'])])}"
               if der.get("in_loop") else
               f", ending with {_and([_the(p) for p in der.get('ends_in', [])])}" if der.get("ends_in") else "")
        return (f"The chain of sign rulers from {_the(f['planet'])}, {role}, runs {path}{end}; it shows which planets "
                f"carry {label}, with no lean of its own.")
    if f["kind"] != "rule":
        return None
    pl = f.get("placement")
    if f.get("status") == "draft" or pl:
        if not pl:
            return None
        if pl.get("lagna_sign"):
            text = f"Your rising sign is {pl['lagna_sign']}"
        elif pl.get("nakshatra"):
            text = f"{_cap(_the(pl['planet']))} sits in the lunar mansion {pl['nakshatra']}"
        elif pl.get("sign"):
            text = f"{_cap(_the(pl['planet']))} sits in {pl['sign']}{dig(pl.get('dignity'))}"
        elif pl.get("lord_of"):
            n = len(pl["lord_of"])
            text = (f"{_cap(_the(pl['planet']))}, the ruler of the {_ords(pl['lord_of'])} house{'s' if n > 1 else ''}, "
                    f"sits in the {_ORD[pl['house']]} house")
        elif pl.get("house"):
            text = f"{_cap(_the(pl['planet']))} sits in the {_ORD[pl['house']]} house"
        else:
            return None
        houses = sorted({h["house"] for h in f.get("area_houses") or []})
        if houses:
            text += (f"; the {_ords(houses)} {'is a house' if len(houses) == 1 else 'are houses'} of {label}")
        return text + "; it is a placement only, with no lean of its own."
    name = rule_names(f["rule_id"])[0]
    entry = next((e for e in glossary() if f["rule_id"] in e["aliases"]), None)
    planets = [_the(p) for p in f.get("planets") or []]
    houses = sorted({h for x in f.get("fires") or [] for h in (x.get("details") or {}).get("houses", [])})
    what = f", which is {entry['definition'][0].lower()}{entry['definition'][1:].rstrip('.')}" if entry else ""
    join = f", joining the {_ords(houses)} houses" if houses else ""
    weight = sum((f.get("themes") or {}).values())
    lean = f"it supports {label}" if weight > 0 else f"it works against {label}" if weight < 0 else "with no lean of its own"
    verb = "forms" if len(planets) == 1 else "form"
    return f"{_cap(_and(planets)) if planets else 'The chart'} {verb} the {name} yoga{what}{join}; {lean}."


def _material(chart, message: str, route: Route, engine, history: list[dict], as_of: date,
              data: dict | None = None):
    """The writer's message, in plain words (the section above), what its sentences are held to (held_to) and the
    handles it cites by."""
    import json
    from .fullchart import cached_payload
    from .narrate import CLIENT_AREA, findings, full_range
    from .sheet import build
    tags, votes, chains, finding_data = held_to(chart, route, as_of)
    data = data or cached_payload(chart, as_of, *full_range(as_of), list(route.areas))
    handles = Handles()
    areas_out = []
    for name in route.areas:
        label = CLIENT_AREA.get(name, name.replace("_", " "))
        sheet = build(data, name) if name in (data.get("areas") or {}) else None
        said = []
        for f in findings(chart, name, as_of)[0]:
            text = finding_sentence(f, name, label, data, sheet)
            if text and f.get("allowed_tags"):
                said.append({"tag": handles.add(f["allowed_tags"][0]), "says": text})
        areas_out.append({"area": label, "findings": said})
    body = {"message": message, "asked_about": ASKED[route.direction], "asks_when": route.when, "asks_why": route.why,
            "earlier_turns": [{"question": h["question"], "answer": h["answer"]} for h in history],
            "engine_answer": [{"text": s.text, "tags": [handles.add(t) for t in engine_tags(s, tags)]}
                              for s in engine.sentences],
            "areas": areas_out}
    return no_tier_words(json.dumps(body, indent=1, default=str)), finding_data, tags, votes, chains, handles


# The engine's material to the writer carries no tier word (SPEC Layer 8, review H2, M5): the writer paraphrases its
# material, and the tier words are refused in what it writes. The glossary's dignity glosses are the only source left.
NO_TIER = (("at its strongest", "at its best"), ("at its weakest", "least at ease"))


def no_tier_words(text: str) -> str:
    for old, new in NO_TIER:
        text = text.replace(old, new)
    return text


def check_sentence(sentence: str, tags: set[str], votes, chains, finding_data, checker, word_rules: str | None = None):
    """(passed, refusals, warnings, check record) for one sentence of a turn's answer: the validator's refusals
    (tags, forbidden claims, tier words, an unmarked weighing) and what the conversation never shows
    (client.NEVER_SHOW), then the checker against the findings it cites.
    The client's-word rules (CLIENT_WORDS, CLIENT_PLAIN, the same-sentence gloss, "I"; client.client_warnings) are
    warnings under `word_rules` "warn" (client.WORD_RULES, SPEC Layer 8) and refusals under "refuse"."""
    from . import client
    from .narrate import _summary_checks, validate_summary
    word_rules = word_rules or client.WORD_RULES
    refusals = validate_summary(sentence, tags, offered_votes=votes, where="answer", family_rule=False, chains=chains)
    refusals += client.client_errors(sentence, word_rules=word_rules)
    never = client.never_show(sentence)                 # refusals in a turn, whatever word_rules says (2026-11-02)
    refusals += never
    warnings = client.client_warnings(sentence, conversation=True) if word_rules != "refuse" and not never else []
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
    from .live import HeldParagraph, JsonStrings
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
    if route.off_limits or route.explains:
        reply = fixed_reply(route.off_limits) if route.off_limits else WHY_REPLIES[route.explains]
        emit({"type": "text", "i": 0, "text": reply, "para": True})
        mark("done")
        emit({"type": "done", "status": "done"})
        return doc | {"source": "fixed", "shown": [reply], "paragraphs": [0], "engine": None, "timeline": timeline,
                      "usage": {"wall_seconds": timeline["done"]}}
    # A "why" turn's engine answer is every family behind the last answer, for and against: the sheet's points it
    # rests on (SPEC Layer 8); the writer is still told the direction asked.
    engine = engine_reading(chart, message, "both" if route.why else route.direction, route.areas, as_of=as_of,
                            when=route.when, data=data, weakest=route.areas_from == "weakest" and not route.why)
    mark("engine")
    doc["engine"] = engine.model_dump()
    emit({"type": "light", "stage": "route", **route_focus(chart, route.areas)})
    user, finding_data, tags, votes, chains, handles = _material(chart, message, route, engine, history, as_of, data)
    drafter = drafter or ModelDrafter(make_backend(None, "writer", config), config, schema=TurnDraft)
    checker = checker or ModelChecker(make_backend(None, "checker", config), config)
    pool = ThreadPoolExecutor(max_workers=max(1, min(8, getattr(checker, "concurrency", 4) or 4)),
                              thread_name_prefix="turn-check")
    writer_metas, checker_metas = [], []
    shown: list[str] = []
    paras: list[int] = []                      # the indices in `shown` that open a paragraph
    accepted: list[str] = []                   # the writer's sentences that passed, tags on, in the order written
    # The answer is held sentence by sentence (review M5), as a held paragraph is (live.HeldParagraph): a draft that
    # replaces the whole answer streams, each sentence shown once it passes; a retry rewrites only the failed
    # sentences, one for each, and a rewrite that passes is shown as it passes and stands in its sentence's place.
    held = HeldParagraph()
    opens_para: dict[str, bool] = {}           # key -> whether its sentence opens a paragraph
    errors_for_retry: list[str] = []
    attempts = 0

    def show(text: str, tagged: str, para: bool) -> None:
        mark("first_verified")
        shown.append(text)
        if para or not paras:
            paras.append(len(shown) - 1)
        emit({"type": "text", "i": len(shown) - 1, "text": text, "para": para or len(shown) == 1})
        f = focus_of(tagged, chart)
        if f["planets"] or f["houses"]:
            emit({"type": "light", "stage": "sentence", **f})

    def judge(s: str, attempt: int) -> tuple[bool, list[str]]:
        ok, refusals, warnings, record = check_sentence(s, tags, votes, chains, finding_data, checker, word_rules)
        if record is not None:
            doc["checks"].append({k: v for k, v in record.items() if k != "meta"} | {"attempt": attempt})
            checker_metas.append(record["meta"])
        doc["warnings"] += [{"sentence": s, "warning": w, "attempt": attempt} for w in warnings]
        if not ok:
            doc["removed"].append({"sentence": s, "reasons": refusals, "attempt": attempt})
        return ok, refusals

    def answer_of(draft) -> str:
        return handles.to_real(unbullet((draft.answer if hasattr(draft, "answer") else draft.get("answer", "")) or ""))

    try:
        for attempt in range(1, config.max_attempts + 1):
            attempts = attempt
            open_ = held.open()
            if open_ is None:                  # nothing held yet: the whole answer, streamed
                futures: dict[int, Any] = {}
                texts: dict[int, str] = {}
                starts: dict[int, bool] = {}
                order = _Order(lambda text, k: show(text, texts.get(k, ""), starts.get(k, False)))

                def run(k: int, s: str, attempt=attempt) -> tuple[bool, list[str]]:
                    ok, why = judge(s, attempt)
                    order.settle(k, ok, shown_text(s))
                    return ok, why

                def submit(k: int, s: str, para: bool) -> None:
                    if k not in futures:
                        texts[k], starts[k] = s, para
                        futures[k] = pool.submit(run, k, s)

                def on_string(path: tuple, value: str, done: bool) -> None:
                    if path != ("answer",):
                        return
                    value = handles.to_real(unbullet(value))
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
                text = answer_of(draft) if draft is not None else ""
                parts = sentences(text)
                for k, (s, para) in enumerate(zip(parts, para_starts(text, parts))):
                    submit(k, s, para)
                results = {k: f.result() for k, f in futures.items()}
                for key, s in held.place(text):
                    k = int(key) - 1
                    opens_para[key] = starts.get(k, k == 0)
                    ok, why = results.get(k) or judge(s, attempt)
                    held.hold(key) if ok else held.fail(key, why)
                if not held.held:
                    errors_for_retry = [handles.to_handles(r) for x in doc["removed"] if x["attempt"] == attempt
                                        for r in x["reasons"]] or ["the answer was empty"]
            else:                              # some held: only the failed sentences, one for each
                if hasattr(drafter, "on_text"):
                    drafter.on_text = None
                try:
                    draft = drafter(TURN_PROMPT, user, [handles.to_handles(turn_retry_instruction(held))])
                except NarrationError as e:
                    doc["removed"].append({"sentence": None, "reasons": [str(e)] + list(e.errors), "attempt": attempt})
                    draft = None
                writer_metas.append(getattr(drafter, "last_meta", None))
                placed = held.place(answer_of(draft)) if draft is not None else []
                if held.refusal:
                    doc["removed"].append({"sentence": answer_of(draft), "reasons": [held.refusal], "attempt": attempt})
                for key, s in placed:
                    base = key.split(".")[0]
                    opens_para.setdefault(key, opens_para.get(base, False) if key != base else False)
                    if (i := held.repeats(s)) is not None:
                        why = [f"it restates held sentence {i} in other words: write the sentence asked for"]
                        doc["removed"].append({"sentence": s, "reasons": why, "attempt": attempt})
                        held.fail(key, why)
                        continue
                    ok, why = pool.submit(judge, s, attempt).result()
                    if ok:
                        held.hold(key)
                        show(shown_text(s), s, opens_para.get(key, False))
                    else:
                        held.fail(key, why)
            if held.complete():
                break
    finally:
        pool.shutdown(wait=True)
    # The answer as it stands: the held sentences in their places (a rewrite where its sentence was).
    keys = [k for k in held.keys() if k in held.held]
    accepted = [held.slots[k] for k in keys]
    shown = [shown_text(x) for x in accepted]
    paras = [i for i, k in enumerate(keys) if i == 0 or opens_para.get(k, False)]
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
    if route.third_party:
        add(THIRD_PARTY_LINE, True)
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
    shown[i] = shown_text(text)
    if doc.get("source") == "writer" and i < len(accepted):
        accepted[i] = text
    doc["shown"], doc["accepted"] = shown, accepted
    doc["edits"] = list(doc.get("edits") or []) + [{"i": i, "by": who, "at": datetime.now(timezone.utc).isoformat()}]
    return doc
