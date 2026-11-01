"""The independent review of chat v1 (docs/review_2026-11-01_chat.md), each finding's test, as SPEC Layer 8 (rev 130,
"Decided after the independent review") settles it."""

import json
import re
from datetime import date, datetime
from pathlib import Path

import pytest

from jyotish.conversation import OfflineTurnWriter, answer_turn, route_turn
from jyotish.narrate import CheckResult, Proposition, engine_reading
from jyotish.uncertainty import assess

ROOT = Path(__file__).resolve().parents[1]
AS_OF = date(2026, 10, 21)
BIRTHS = json.loads((ROOT / "tests" / "fixtures" / "births.json").read_text())["births"]


def _chart(b):
    return assess(datetime.fromisoformat(b["utc"]), b["lat"], b["lon"], true_node=False, seed=0)


@pytest.fixture(scope="module")
def charts():
    return {b["name"]: _chart(b) for b in BIRTHS}


@pytest.fixture(scope="module")
def chart(charts):
    return charts["reference"]


def as_of(b) -> date:
    """The session's date for a birth: AS_OF, or thirty years after a synthetic birth drawn after it (synthetic-3,
    2036), since a conversation is about a life already begun."""
    born = datetime.fromisoformat(b["utc"]).date()
    return AS_OF if born < AS_OF else born.replace(year=born.year + 30)


def passes(sentence, data):
    return CheckResult(propositions=[Proposition(text=sentence, supported=True, evidence="stub")])


def chips() -> list[str]:
    """Every chip the conversation page offers (web/js/strings.js, chat.chip.*)."""
    text = (ROOT / "web" / "js" / "strings.js").read_text()
    return re.findall(r'"chat\.chip\.[\w.]+":\s*"([^"]+)"', text)


def first_chips() -> list[str]:
    text = (ROOT / "web" / "js" / "strings.js").read_text()
    return re.findall(r'"chat\.chip\.first\.[\w.]+":\s*"([^"]+)"', text)


# --- C1: long life and health are never a default route, and no stretch about them reaches the client --------------

LONG_LIFE = re.compile(r"long life|longevity|lifespan|\bhealth\b|\blive\b", re.I)


def test_c1_a_chip_before_the_first_question_names_an_area():
    from jyotish.conversation import areas_of
    assert len(first_chips()) == 3
    for chip in first_chips():
        assert areas_of(chip), chip


@pytest.mark.parametrize("message", sorted(set(chips()) | {"when?", "why?", "what are my strengths"}))
def test_c1_no_first_turn_mentions_long_life_or_health(charts, message):
    for b in BIRTHS:
        name, chart = b["name"], charts[b["name"]]
        route = route_turn(message, chart)
        assert not {"longevity", "health"} & set(route.areas), (name, message, route.areas)
        if route.off_limits:
            continue
        doc = answer_turn(chart, message, route, as_of=as_of(b), drafter=OfflineTurnWriter(), checker=passes)
        said = doc["shown"] + [s["text"] for s in doc["engine"]["sentences"]]
        assert not [s for s in said if LONG_LIFE.search(s)], (name, message)


def test_c1_no_stretch_for_long_life_or_health_on_any_route(chart):
    ans = engine_reading(chart, "when will my health improve", "both", ["health", "longevity", "career"], as_of=AS_OF,
                         when=True)
    stretches = [s.text for s in ans.sentences if "stretch" in s.text]
    assert stretches and not [s for s in stretches if LONG_LIFE.search(s)]
    route = route_turn("when will my health improve", chart)
    assert route.areas == ["health"] and route.when
    doc = answer_turn(chart, "when will my health improve", route, as_of=AS_OF, drafter=OfflineTurnWriter(),
                      checker=passes)
    assert not [s for s in doc["shown"] if "stretch" in s]


# --- C2: distress is read first and widest, before a follow-up can carry anything ------------------------------------

DISTRESS_SET = [
    # the review's table
    "I can’t go on like this anymore", "I don’t want to live anymore", "I’d be better off dead",
    "mujhe marna hai, kuch accha nahi ho raha", "jeena nahi chahta ab", "I feel hopeless, nothing works",
    # the same with other apostrophes, case and spacing
    "I can't go on like this anymore", "I CAN‘T GO ON", "I dont want to live", "i do not want to be alive",
    "Id be better off dead", "everyone is better off without me", "I’m better off dead tbh",
    # their kin in English
    "there is no point living", "no point in living anymore", "what is the point of living, no point in life",
    "I have nothing to live for", "life is not worth living", "I’m so tired of living", "I want to end it all",
    "I'm going to end it", "I can’t take it anymore", "I wish I was never born", "I feel worthless",
    "I have been cutting myself", "I want to kill myself", "thinking about suicide",
    # Hinglish in Latin script
    "marna chahta hu", "main mar jaun to accha", "mar jana chahti hoon", "jeena nahi chahti", "jeene ka mann nahi karta",
    "zindagi khatam kar dunga", "khudkushi ke baare mein soch raha hoon", "aatmahatya", "atmahatya kar lunga",
    "apni jaan de dunga", "koi umeed nahi bachi",
    # Hindi in Devanagari
    "मुझे मरना है", "मैं मर जाऊं", "अब जीना नहीं चाहता", "जीने का मन नहीं करता", "आत्महत्या के बारे में सोच रहा हूँ",
    "खुदकुशी कर लूँ", "ज़िंदगी खत्म कर दूँ", "कोई उम्मीद नहीं है",
]


@pytest.mark.parametrize("message", DISTRESS_SET)
def test_c2_every_distress_message_reaches_the_helpline_cold_and_after_a_turn(chart, message):
    from jyotish.conversation import fixed_reply
    challenges = route_turn("what are the challanges in my life", chart)
    for last in (None, challenges):
        route = route_turn(message, chart, last)
        assert route.off_limits == "distress", (message, last is not None)
        assert not route.follow_up and not route.carried and not route.areas
        doc = answer_turn(chart, message, route, as_of=AS_OF)
        assert doc["source"] == "fixed" and doc["shown"] == [fixed_reply("distress")]
        assert "14416" in doc["shown"][0] and "112" in doc["shown"][0]


@pytest.mark.parametrize("message", ["how is my career", "when will I marry", "tell me about my life",
                                     "meri shaadi kab hogi", "I am a marine engineer", "is my marriage hopeful?"])
def test_c2_ordinary_messages_are_not_distress(chart, message):
    assert route_turn(message, chart).off_limits != "distress"


# --- H1: off limits are phrases, not words ---------------------------------------------------------------------------

ORDINARY = [   # the review's table: each was refused, and each is an ordinary message
    "My Moon is in Cancer, what does that mean for my mind?", "I'm a Cancer rising, how is my personality?",
    "I'm sick of my job, should I change careers?", "I failed the vehicle inspection, what about property?",
    "My father died last year. How is my career looking?", "after my brother's death I feel lost, what about my mind",
    "my job feels like a dead end", "is my career dead?", "my trade is carpentry, will my business grow?",
    "I work in trade finance, is my career good?", "should I invest time in this relationship?",
    "my partner shares my values, is marriage good?", "is changing careers a gamble?", "should I buy a house this year?",
    "will they hire me after the interview?", "will they accept my visa application for abroad?",
    "I can't go on this trip because of work, will my career suffer?",
    "I cannot go on vacation this year, is that bad for my marriage?",
    # and the appendix's other ordinary rows
    "my mother passed away, will my home life settle?", "I'm a surgeon, how is my career?", "how is my health?",
    "will she marry me?",
]


@pytest.mark.parametrize("message", ORDINARY)
def test_h1_ordinary_messages_are_answered(chart, message):
    route = route_turn(message, chart)
    assert route.off_limits is None, (message, route.off_limits)
    assert route.areas


@pytest.mark.parametrize("message,kind", [
    ("will I die early?", "death"), ("when will I die", "death"), ("how long will I live", "death"),
    ("what is my lifespan", "death"), ("tell me about my longevity", "death"), ("meri mrityu kab hogi", "death"),
    ("मेरी मृत्यु कब होगी", "death"),
    ("do I have cancer", "illness"), ("what disease will I get", "illness"), ("will I get diabetes", "illness"),
    ("will my surgery go well", "illness"), ("kya mujhe koi bimari hogi", "illness"),
    ("should I buy bitcoin", "trade"), ("is the stock market good for me", "trade"), ("should I invest now", "trade"),
    ("should I buy shares in Tata", "trade"), ("should I invest my savings", "trade"),
    ("kya mujhe share bazaar mein paisa lagana chahiye", "trade"), ("will I win the lottery", "trade"),
    ("what is my wife's future", "other_person"), ("read my husband's chart", "other_person"),
    ("will my son get a job", "other_person"), ("I'm worried about my mother's health", "other_person"),
])
def test_h1_off_limits_phrases_are_still_refused(message, kind):
    from jyotish.conversation import off_limits
    assert off_limits(message) == kind


@pytest.mark.parametrize("message,area", [("will she marry me?", "marriage"),
                                          ("will they hire me after the interview?", "career")])
def test_h1_another_persons_decision_is_the_clients_own_area_with_the_third_party_line(chart, message, area):
    from jyotish.conversation import THIRD_PARTY_LINE
    route = route_turn(message, chart)
    assert (route.off_limits, route.areas, route.third_party) == (None, [area], True)
    doc = answer_turn(chart, message, route, as_of=AS_OF, drafter=OfflineTurnWriter(), checker=passes)
    assert doc["shown"][-1] == THIRD_PARTY_LINE and doc["paragraphs"][-1] == len(doc["shown"]) - 1
    assert not route_turn("how is my marriage", chart).third_party


# --- H3: the client's screen is held to the client's words --------------------------------------------------------

def test_h3_every_engine_sentence_the_client_can_see_passes_the_conversations_words(chart):
    """The fallback and the "when" lines for every area and every direction, the fixed replies and the third-party
    line: no engine word, D-code, score, method name or tier word (client_warnings with the conversation's list)."""
    from jyotish.client import client_warnings
    from jyotish.conversation import REPLIES, THIRD_PARTY_LINE
    from jyotish.narrate import TIER_WORDS
    areas = [a for a in chart.scored.areas if a != "synastry"]
    said = list(REPLIES.values()) + [THIRD_PARTY_LINE]
    for direction in ("against", "for", "both"):
        said += [s.text for s in engine_reading(chart, "q", direction, areas, as_of=AS_OF, when=True).sentences]
    assert len(said) > 100
    bad = [(s, w) for s in said for w in client_warnings(s, conversation=True)]
    assert not bad, bad[:3]
    assert not [s for s in said if TIER_WORDS.search(s) or re.search(r"strongest|weakest|\bscor(?:e|es|ed|ing)\b", s, re.I)]
    assert not [s for s in said if re.search(r"\bD\d|Krishnamurti", s)]


@pytest.mark.parametrize("sentence,flag", [("The D9 leans favourably.", "D9"), ("The chart scores this well.", "scores"),
                                           ("The Krishnamurti method agrees.", "Krishnamurti"),
                                           ("Your career is moderately supported.", "moderately")])
def test_h3_the_conversations_word_list_warns(sentence, flag):
    from jyotish.client import client_warnings
    assert client_warnings(sentence) == [] or flag in ("scores",)   # a reading's list is unchanged
    assert flag in client_warnings(sentence, conversation=True)[0]


def test_h3_markdown_never_reaches_the_client(chart):
    class Markdown(OfflineTurnWriter):
        def __call__(self, system, user, errors):
            body = json.loads(user)
            tagged = [x for x in body["engine_answer"] if x["tags"]][:2]
            text = "\n\n".join(f"- **{x['text'][:-1]}** [{x['tags'][0]}]." for x in tagged)
            from jyotish.conversation import TurnDraft
            return TurnDraft(answer="## Your career\n" + text)
    route = route_turn("how is my career", chart)
    doc = answer_turn(chart, "how is my career", route, as_of=AS_OF, drafter=Markdown(), checker=passes)
    assert doc["source"] == "writer" and len(doc["shown"]) >= 2
    assert not [s for s in doc["shown"] if re.search(r"\*|^\s*[-#]|`|\[", s)], doc["shown"]


# --- H4: the service never waits on itself ---------------------------------------------------------------------------

BIRTH = {"date": "2001-03-12", "time": "10:10:25", "tz": "Asia/Kolkata", "lat": 28.1989, "lon": 76.617,
         "node": "mean", "place": "Rewari, Haryana", "as_of": AS_OF.isoformat()}


def wait_turn(c, url, limit=120.0):
    import time
    t = time.monotonic()
    while (st := c.get(url).json()["status"]) not in ("done", "failed"):
        assert time.monotonic() - t < limit, f"{url} still {st} after {limit} s"
        time.sleep(0.1)
    return st


def test_h4_a_turn_in_a_fresh_app_with_one_worker_finishes(tmp_path):
    """Sessions made in one app; a fresh app on the same database (a restart, another process) with one worker and
    no payload held; one question in each. Before the fix the first turn held the only worker waiting on its own
    payload job, queued behind it on the same pool, for ever (the review reproduced it)."""
    from fastapi.testclient import TestClient
    from jyotish.api import create_app
    db = f"sqlite:///{tmp_path / 'h4.db'}"
    with TestClient(create_app(db, turn_writer=OfflineTurnWriter, turn_checker=lambda: passes)) as c:
        sids = [c.post("/sessions", json=BIRTH).json()["id"] for _ in range(2)]
    fresh = create_app(db, workers=1, turn_writer=OfflineTurnWriter, turn_checker=lambda: passes)
    with TestClient(fresh) as c:
        urls = []
        for sid in sids:
            n = c.post(f"/sessions/{sid}/turns", json={"message": "how is my career"}).json()["n"]
            urls.append(f"/sessions/{sid}/turns/{n}")
        assert [wait_turn(c, u) for u in urls] == ["done", "done"]


# --- H6: a turn cut off by a restart, or past the limit, is marked failed and the conversation goes on ---------------

def _stuck(app, sid, status, minutes_ago=0):
    from datetime import datetime, timedelta, timezone
    import uuid
    from jyotish.db import SessionRow, TurnRow
    with app.state.Session.begin() as s:
        srow = s.get(SessionRow, sid)
        n = 1 + max([t.n for t in s.query(TurnRow).filter_by(session_id=sid)] or [0])
        s.add(TurnRow(id=uuid.uuid4().hex, session_id=sid, n=n, birth_key=srow.birth_key, question="how is my career",
                      status=status, created_at=datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)))
    return n


def test_h6_a_turn_cut_off_by_a_restart_is_failed_and_the_conversation_goes_on(tmp_path):
    from fastapi.testclient import TestClient
    from jyotish.api import create_app
    db = f"sqlite:///{tmp_path / 'h6.db'}"
    app = create_app(db, turn_writer=OfflineTurnWriter, turn_checker=lambda: passes)
    with TestClient(app) as c:
        sid = c.post("/sessions", json=BIRTH).json()["id"]
    stuck = [_stuck(app, sid, "running")]
    fresh = create_app(db, turn_writer=OfflineTurnWriter, turn_checker=lambda: passes)    # the restart
    with TestClient(fresh) as c:
        assert c.get(f"/sessions/{sid}/turns/{stuck[0]}").json()["status"] == "failed"
        r = c.post(f"/sessions/{sid}/turns", json={"message": "and marriage?"})
        assert r.status_code == 202
        assert wait_turn(c, f"/sessions/{sid}/turns/{r.json()['n']}") == "done"


def test_h6_a_turn_past_the_limit_is_failed_and_the_conversation_goes_on(tmp_path):
    from fastapi.testclient import TestClient
    from jyotish.api import create_app
    app = create_app(f"sqlite:///{tmp_path / 'h6b.db'}", turn_writer=OfflineTurnWriter, turn_checker=lambda: passes,
                     turn_limit=600)
    with TestClient(app) as c:
        sid = c.post("/sessions", json=BIRTH).json()["id"]
        fresh_turn = _stuck(app, sid, "queued", minutes_ago=1)
        assert c.post(f"/sessions/{sid}/turns", json={"message": "and marriage?"}).status_code == 409
        with app.state.Session.begin() as s:                  # the same turn, eleven minutes old
            from datetime import datetime, timedelta, timezone
            from jyotish.db import TurnRow
            s.query(TurnRow).filter_by(session_id=sid, n=fresh_turn).one().created_at = \
                datetime.now(timezone.utc) - timedelta(minutes=11)
        r = c.post(f"/sessions/{sid}/turns", json={"message": "and marriage?"})
        assert r.status_code == 202
        assert c.get(f"/sessions/{sid}/turns/{fresh_turn}").json()["status"] == "failed"
        assert wait_turn(c, f"/sessions/{sid}/turns/{r.json()['n']}") == "done"
