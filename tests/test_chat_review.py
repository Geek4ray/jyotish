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
         "node": "mean", "place": "Rewari, Haryana"}         # the date is the server's (review M2): `today` below


def carry(old, new):
    """The browser's cookies (the conversations' secrets) kept across a restart of the service."""
    for cookie in old.cookies.jar:
        new.cookies.jar.set_cookie(cookie)
    return new


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
    with TestClient(create_app(db, today=lambda: AS_OF, turn_writer=OfflineTurnWriter,
                               turn_checker=lambda: passes)) as before:
        sids = [before.post("/sessions", json=BIRTH).json()["id"] for _ in range(2)]
    fresh = create_app(db, today=lambda: AS_OF, workers=1, turn_writer=OfflineTurnWriter,
                       turn_checker=lambda: passes)
    with carry(before, TestClient(fresh)) as c:
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
    app = create_app(db, today=lambda: AS_OF, turn_writer=OfflineTurnWriter, turn_checker=lambda: passes)
    with TestClient(app) as before:
        sid = before.post("/sessions", json=BIRTH).json()["id"]
    stuck = [_stuck(app, sid, "running")]
    fresh = create_app(db, today=lambda: AS_OF, turn_writer=OfflineTurnWriter,          # the restart
                       turn_checker=lambda: passes)
    with carry(before, TestClient(fresh)) as c:
        assert c.get(f"/sessions/{sid}/turns/{stuck[0]}").json()["status"] == "failed"
        r = c.post(f"/sessions/{sid}/turns", json={"message": "and marriage?"})
        assert r.status_code == 202
        assert wait_turn(c, f"/sessions/{sid}/turns/{r.json()['n']}") == "done"


def test_h6_a_turn_past_the_limit_is_failed_and_the_conversation_goes_on(tmp_path):
    from fastapi.testclient import TestClient
    from jyotish.api import create_app
    app = create_app(f"sqlite:///{tmp_path / 'h6b.db'}", today=lambda: AS_OF,
                     turn_writer=OfflineTurnWriter, turn_checker=lambda: passes,
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


# --- H7: a conversation has a secret and an end ----------------------------------------------------------------------

@pytest.fixture()
def h7(tmp_path):
    from fastapi.testclient import TestClient
    from jyotish.api import create_app
    app = create_app(f"sqlite:///{tmp_path / 'h7.db'}", today=lambda: AS_OF,
                     turn_writer=OfflineTurnWriter, turn_checker=lambda: passes,
                     reviewers={"rtok": "ray"})
    with TestClient(app) as c:
        r = c.post("/sessions", json=BIRTH)
        yield app, c, r


def test_h7_the_secret_is_an_httponly_cookie_never_in_the_body_or_the_url(h7):
    app, c, r = h7
    sid = r.json()["id"]
    cookies = r.headers.get_list("set-cookie")
    mine = next(x for x in cookies if x.startswith(f"tatva_{sid}="))
    assert "HttpOnly" in mine and "SameSite=strict" in mine and "Path=/sessions" in mine and "Max-Age=15552000" in mine
    secret = mine.split("=", 1)[1].split(";")[0]
    assert len(secret) >= 40 and secret not in r.text and "chart_id" not in r.json()
    assert r.json()["chart_svg"] == f"/sessions/{sid}/chart.svg" and "/charts/" not in r.text
    from jyotish.db import SessionRow
    with app.state.Session() as s:
        row = s.get(SessionRow, sid)
        assert row.secret_hash and secret not in row.secret_hash
    assert c.get("/sessions/current").json()["id"] == sid
    page = (ROOT / "web" / "js" / "chat.js").read_text()
    assert "?s=" not in page and "history.replaceState" not in page and "/charts/" not in page


def test_h7_every_client_route_needs_the_secret(h7):
    from fastapi.testclient import TestClient
    app, c, r = h7
    sid = r.json()["id"]
    n = c.post(f"/sessions/{sid}/turns", json={"message": "how is my career"}).json()["n"]
    assert wait_turn(c, f"/sessions/{sid}/turns/{n}") == "done"
    routes = [f"/sessions/{sid}", f"/sessions/{sid}/turns/{n}", f"/sessions/{sid}/turns/{n}/live",
              f"/sessions/{sid}/tables.json", f"/sessions/{sid}/chart.svg"]
    assert [c.get(u).status_code for u in routes] == [200] * 5
    with TestClient(app) as stranger:                                   # the link without the cookie
        assert [stranger.get(u).status_code for u in routes] == [404] * 5
        assert stranger.post(f"/sessions/{sid}/turns", json={"message": "hi"}).status_code == 404
        assert stranger.get(f"/sessions/{sid}/turns/{n}/events").status_code == 404
        assert stranger.delete(f"/sessions/{sid}").status_code == 404
        stranger.cookies.set(f"tatva_{sid}", "a-guess", path="/sessions")
        assert stranger.get(f"/sessions/{sid}").status_code == 404
    # The reviewer's routes take a reviewer token, not the secret.
    with TestClient(app) as reviewer:
        assert reviewer.get(f"/sessions/{sid}/review", headers={"Authorization": "Bearer rtok"}).status_code == 200


def test_h7_the_session_id_is_masked_in_the_logs_and_not_logged_at_creation(h7, caplog):
    import logging
    from jyotish import logs
    assert logs.safe_path("/sessions/0123abcd/turns/2/events") == "/sessions/<session>/turns/2/events"
    assert logs.safe_path("/review/sessions/0123abcd") == "/review/sessions/<session>"
    assert logs.safe_path("/sessions/current") == "/sessions/current"
    app, c, _ = h7
    logger = logging.getLogger(logs.LOGGER)
    logger.propagate = True
    try:
        with caplog.at_level(logging.INFO, logger=logs.LOGGER):
            sid = c.post("/sessions", json=BIRTH).json()["id"]
            c.get(f"/sessions/{sid}")
    finally:
        logger.propagate = False
    text = json.dumps([getattr(x, "fields", {}) for x in caplog.records])
    assert "session.created" in [x.getMessage() for x in caplog.records] and sid not in text


def test_h7_a_conversation_ends_180_days_after_its_last_turn(h7):
    from datetime import datetime, timedelta, timezone
    from jyotish.db import SessionRow, TurnRow
    app, c, r = h7
    sid = r.json()["id"]
    now = datetime.now(timezone.utc)
    with app.state.Session.begin() as s:
        s.get(SessionRow, sid).created_at = now - timedelta(days=400)
        s.add(TurnRow(id="t" * 32, session_id=sid, n=1, question="q", status="done", created_at=now - timedelta(days=179)))
    assert c.get(f"/sessions/{sid}").status_code == 200
    with app.state.Session.begin() as s:
        s.get(TurnRow, "t" * 32).created_at = now - timedelta(days=181)
    assert c.get(f"/sessions/{sid}").status_code == 404
    assert c.post(f"/sessions/{sid}/turns", json={"message": "hi"}).status_code == 404


def test_h7_forget_this_conversation_erases_it_and_keeps_a_reviewed_turns_judgement(h7):
    from jyotish.api import ErasureRow, ReviewRow
    from jyotish.db import SessionRow, TurnRow
    app, c, r = h7
    sid = r.json()["id"]
    n = c.post(f"/sessions/{sid}/turns", json={"message": "how is my career"}).json()["n"]
    wait_turn(c, f"/sessions/{sid}/turns/{n}")
    assert c.get(f"/sessions/{sid}/review", headers={"Authorization": "Bearer rtok"}).status_code == 200
    with app.state.Session.begin() as s:
        tid = s.query(TurnRow).filter_by(session_id=sid).one().id
        s.add(ReviewRow(turn_id=tid, reviewer_id="ray", action="edit", target="answer:0", before="a", after="b",
                        accepted=True))
    gone = c.delete(f"/sessions/{sid}")
    assert gone.status_code == 200 and any(x.startswith(f"tatva_{sid}=") and "Max-Age=0" in x
                                           for x in gone.headers.get_list("set-cookie"))
    with app.state.Session() as s:
        assert s.get(SessionRow, sid) is None and not s.query(TurnRow).filter_by(session_id=sid).count()
        kept = s.query(ReviewRow).filter_by(action="edit", reviewer_id="ray").one()
        assert (kept.turn_id, kept.chart_id, kept.after) == (None, None, "b")
        assert s.query(ReviewRow).filter(ReviewRow.target == f"session:{sid}").count() == 0
        erasure = s.query(ErasureRow).one()
        assert erasure.erased_by == "client" and erasure.counts["sessions"] == 1 and erasure.counts["turns"] == 1
    assert c.get(f"/sessions/{sid}").status_code == 404
    html = (ROOT / "web" / "chat.html").read_text()
    assert 'id="forget"' in html and "Forget this conversation" in (ROOT / "web" / "js" / "strings.js").read_text()


# --- H5: the payloads held are bounded, and POST /sessions is rate-limited --------------------------------------------

def test_h5_the_payloads_held_are_bounded(tmp_path):
    from fastapi.testclient import TestClient
    from jyotish.api import create_app
    app = create_app(f"sqlite:///{tmp_path / 'h5.db'}", today=lambda: AS_OF,
                     turn_writer=OfflineTurnWriter, turn_checker=lambda: passes,
                     payloads_held=2)
    with TestClient(app) as c:
        sids = [c.post("/sessions", json=BIRTH).json()["id"] for _ in range(4)]
        assert list(app.state.payloads) == sids[-2:]                     # the two most recent only
        n = c.post(f"/sessions/{sids[0]}/turns", json={"message": "how is my career"}).json()["n"]
        assert wait_turn(c, f"/sessions/{sids[0]}/turns/{n}") == "done"  # a payload let go is made again
        assert len(app.state.payloads) == 2 and list(app.state.payloads)[-1] == sids[0]


def test_h5_post_sessions_is_rate_limited(tmp_path):
    from fastapi.testclient import TestClient
    from jyotish.api import create_app
    app = create_app(f"sqlite:///{tmp_path / 'h5b.db'}", today=lambda: AS_OF, rate=(2, 100))
    with TestClient(app) as c:
        assert [c.post("/sessions", json=BIRTH).status_code for _ in range(2)] == [201, 201]
        r = c.post("/sessions", json=BIRTH)
        assert r.status_code == 429 and int(r.headers["Retry-After"]) > 0


# --- H2: "challenges" are where the chart leans against -------------------------------------------------------------

def test_h2_the_weakest_areas_are_ranked_by_adverse_direction_first(charts):
    from jyotish.conversation import weakest_areas
    for name, chart in charts.items():
        sc = chart.scored
        weak = weakest_areas(chart)
        assert len(weak) == 3 and not {"longevity", "health", "synastry"} & set(weak)
        adverse = [n for n, a in sc.areas.items() if a.direction == "adverse" and n not in ("longevity", "health")]
        # every adverse area comes before any area that is not
        assert weak[:min(3, len(adverse))] == [w for w in weak if w in adverse][:3], name
    weak = weakest_areas(charts["synthetic-3"])
    assert weak == ["personality", "wealth", "children"]                     # the three adverse areas there
    assert all(charts["synthetic-3"].scored.areas[w].direction == "adverse" for w in weak)


def test_h2_when_no_area_leans_against_the_answer_says_so_and_gives_each_areas_lean(chart):
    route = route_turn("what are the challanges in my life", chart)
    doc = answer_turn(chart, "what are the challanges in my life", route, as_of=AS_OF, drafter=OfflineTurnWriter(),
                      checker=passes)
    engine = [s["text"] for s in doc["engine"]["sentences"]]
    assert engine[0].startswith("No part of your chart leans against you on balance; the parts it supports least are")
    for area in route.areas:                              # each area's overall lean beside what opposes it
        assert any("on balance" in s and "lean favourably" in s for s in engine)
    from jyotish.conversation import TURN_PROMPT
    assert "never call a part the chart supports a challenge" in TURN_PROMPT


def test_h2_an_adverse_area_is_named_as_leaning_against(charts):
    chart = charts["synthetic-3"]
    b = next(x for x in BIRTHS if x["name"] == "synthetic-3")
    ans = engine_reading(chart, "q", "against", ["personality", "wealth", "children"], as_of=as_of(b), weakest=True)
    assert ans.sentences[0].text == ("On balance, your chart leans against you in yourself and your temperament, "
                                     "money and children.")


def test_h2_the_writers_material_carries_no_tier_word(chart):
    from jyotish.conversation import _material
    from jyotish.narrate import TIER_WORDS
    for message in ("what are the challanges in my life", "how is my career", "and marriage?"):
        route = route_turn(message, chart)
        engine = engine_reading(chart, message, route.direction, route.areas, as_of=AS_OF,
                                weakest=route.areas_from == "weakest")
        user = _material(chart, message, route, engine, [], AS_OF)[0]
        assert not TIER_WORDS.search(user) and not re.search(r"strongest|weakest|strongly|moderately", user), message


# --- M2: a minor's chart and the session's date ----------------------------------------------------------------------

@pytest.mark.parametrize("message", ["tell me about my chart", "what are his strengths", "what are the challenges",
                                     "when?", "how is my son's chart", "how is my son's future? this is his chart",
                                     "how is his education", "how is my studies", "what are her strengths"])
def test_m2_a_minors_general_questions_are_answered_from_the_general_areas(chart, message):
    from jyotish.conversation import MINOR_AREAS
    route = route_turn(message, chart, minor=True)
    assert route.off_limits is None, (message, route.off_limits)
    assert route.areas and set(route.areas) <= set(MINOR_AREAS)


@pytest.mark.parametrize("message,kind", [("what about his marriage", "minor"), ("when will he get a job", "minor"),
                                          ("what is my wife's future", "other_person"), ("will he die early", "death")])
def test_m2_a_minors_chart_still_refuses_the_rest(chart, message, kind):
    assert route_turn(message, chart, minor=True).off_limits == kind


def test_m2_the_sessions_date_is_the_servers(tmp_path):
    from fastapi.testclient import TestClient
    from jyotish.api import create_app
    app = create_app(f"sqlite:///{tmp_path / 'm2.db'}", reviewers={"rtok": "ray"}, today=lambda: AS_OF)
    with TestClient(app) as c:
        assert c.post("/sessions", json=BIRTH).json()["as_of"] == AS_OF.isoformat()
        # A client cannot move the date (a minor's chart made an adult's); a reviewer can.
        assert c.post("/sessions", json=dict(BIRTH, as_of="2040-01-01")).status_code == 401
        r = c.post("/sessions", json=dict(BIRTH, as_of="2040-01-01"), headers={"Authorization": "Bearer rtok"})
        assert r.status_code == 201 and r.json()["as_of"] == "2040-01-01"
        assert c.post("/sessions", json=dict(BIRTH, date="2030-01-01")).status_code == 422     # born after today
    from jyotish.db import SessionRow
    with app.state.Session() as s:
        assert not any(r.minor for r in s.query(SessionRow))


# --- M3: a short message is a follow-up only with neither an area nor a direction of its own --------------------------

def test_m3_what_are_my_strengths_after_an_against_turn_is_a_question_of_its_own(chart):
    from jyotish.conversation import top_areas
    first = route_turn("what are the challanges in my life", chart)
    r = route_turn("what are my strengths", chart, first)
    assert (r.follow_up, r.carried, r.direction, r.areas, r.areas_from) == (False, [], "for", top_areas(chart), "top")
    health = route_turn("how is my health?", chart, first)
    assert (health.follow_up, health.direction, health.areas) == (False, "both", ["health"])
    # A bare follow-up still carries ("and marriage?", "when?", "why?").
    assert route_turn("when?", chart, first).carried == ["areas", "direction"]
    assert route_turn("and marriage?", chart, first).carried == ["direction"]
    assert route_turn("tell me more", chart, first).carried == ["areas", "direction"]


# --- M4: the routing vocabulary --------------------------------------------------------------------------------------

def _route_words(r):
    if r.off_limits:
        return f"off:{r.off_limits}"
    return " ".join([",".join(r.areas), r.direction] + (["when"] if r.when else []) + (["why"] if r.why else [])
                    + (["follow"] if r.follow_up else []))


TOP, WEAK = "career,marriage,debts_enemies", "father,reputation,siblings"
APPENDIX = [   # the review's routing probe (its appendix): (message, cold, after the challenges turn)
    ("I can't go on this trip because of work, will my career suffer?", "career both", "career both"),
    ("I cannot go on vacation this year, is that bad for my marriage?", "marriage against", "marriage against"),
    ("I can’t go on like this anymore", "off:distress", "off:distress"),
    ("I don’t want to live anymore", "off:distress", "off:distress"),
    ("I’d be better off dead", "off:distress", "off:distress"),
    ("mujhe marna hai, kuch accha nahi ho raha", "off:distress", "off:distress"),
    ("jeena nahi chahta ab", "off:distress", "off:distress"),
    ("I feel hopeless, nothing works", "off:distress", "off:distress"),
    ("My father died last year. How is my career looking?", "career,father both", "career,father both"),
    ("my mother passed away, will my home life settle?", "mother_home both", "mother_home both"),
    ("after my brother's death I feel lost, what about my mind", "siblings,mind both", "siblings,mind both"),
    ("my job feels like a dead end", "career both", "career both"),
    ("is my career dead?", "career both", "career both"),
    ("meri mrityu kab hogi", "off:death", "off:death"),
    ("will I die early?", "off:death", "off:death"),
    ("My Moon is in Cancer, what does that mean for my mind?", "mind both", "mind both"),
    ("I'm a Cancer rising, how is my personality?", "personality both", "personality both"),
    ("I'm sick of my job, should I change careers?", "career both", "career both"),
    ("I'm a surgeon, how is my career?", "career both", "career both"),
    ("I failed the vehicle inspection, what about property?", "mother_home both", "mother_home both"),
    ("how is my health?", "health both", "health both"),
    ("will my medication work?", "off:illness", "off:illness"),
    ("my trade is carpentry, will my business grow?", "career both", "career both"),
    ("I work in trade finance, is my career good?", "career,wealth for", "career,wealth for"),
    ("should I invest time in this relationship?", "marriage both", "marriage both"),
    ("my partner shares my values, is marriage good?", "marriage for", "marriage for"),
    ("is changing careers a gamble?", "career both", "career both"),
    ("should I buy a house this year?", "mother_home both", "mother_home both"),
    ("kya mujhe share bazaar mein paisa lagana chahiye", "off:trade", "off:trade"),
    ("will they hire me after the interview?", "career both", "career both"),
    ("will they accept my visa application for abroad?", "foreign both", "foreign both"),
    ("will she marry me?", "marriage both", "marriage both"),
    ("my wife's career is affecting mine, what does my chart say?", "off:other_person", "off:other_person"),
    ("how is my son's future? this is his chart", "off:other_person", "off:other_person"),
    ("I'm worried about my mother's health", "off:other_person", "off:other_person"),
    ("shaadi kab hogi?", "marriage both when", "marriage both when"),
    ("naukri mein kya problem hai", "career against", "career against"),
    ("paisa kab aayega", "wealth both when", "wealth both when"),
    ("meri carrer kaisi hai", "career both", "career both"),
    ("I want to learn about my chart", f"{TOP} both", f"{TOP} both"),
    ("for example, how is my marriage?", "marriage both", "marriage both"),
    ("I can't sleep properly, why?", f"{TOP} both why", f"{WEAK} against why follow"),
    ("my friend Mary asked me to ask about love", "marriage both", "marriage both"),
    ("tell me about my love life", "marriage both", "marriage both"),
    ("what's bad in my chart?", f"{WEAK} against", f"{WEAK} against"),
    ("what should I be careful about?", f"{WEAK} against", f"{WEAK} against"),
    ("any doshas in my chart?", f"{WEAK} against", f"{WEAK} against"),
    ("what are my negatives?", f"{WEAK} against", f"{WEAK} against"),
    ("what are the challenges in my career and where am I strong", "career both", "career both"),
    ("challenges?", f"{WEAK} against", f"{WEAK} against"),
    ("what about kids", "children both", "children against follow"),
    ("when will I get a job?", "career both when", "career both when"),
    ("why?", f"{TOP} both why", f"{WEAK} against why follow"),
    ("what are my strengths", f"{TOP} for", f"{TOP} for"),
]


@pytest.mark.parametrize("message,cold,after", APPENDIX)
def test_m4_the_reviews_routing_probe(chart, message, cold, after):
    first = route_turn("what are the challanges in my life", chart)
    assert (_route_words(route_turn(message, chart)), _route_words(route_turn(message, chart, first))) == (cold, after)


@pytest.mark.parametrize("message,areas,direction,when", [
    ("shaadi kab hogi", ["marriage"], None, True), ("naukri kab milegi", ["career"], None, True),
    ("sehat kaisi rahegi", ["health"], None, False), ("bacche kab honge", ["children"], None, True),
    ("videsh jaane ka yog", ["foreign"], None, False), ("ghar kab banega", ["mother_home"], None, True),
    ("padhai mein dikkat", ["intellect"], "against", False), ("kismat achhi hai kya", ["fortune"], "for", False),
    ("मेरी शादी कब होगी", ["marriage"], None, True), ("नौकरी में समस्या", ["career"], "against", False),
    ("पैसा कब आएगा", ["wealth"], None, True), ("love marriage hogi ya arrange", ["marriage"], None, False),
    ("is my career good", ["career"], "for", False), ("any issues with money", ["wealth"], "against", False),
    ("is it hard to find a job", ["career"], "against", False), ("I worry about my exams", ["intellect"], "against", False),
])
def test_m4_hindi_hinglish_and_the_grown_lists(message, areas, direction, when):
    from jyotish.conversation import WHEN, areas_of, direction_of, normalise
    assert areas_of(message) == areas
    assert direction_of(message) == direction
    assert bool(WHEN.search(normalise(message))) == when


@pytest.mark.parametrize("message", ["I want to learn about my chart", "for example, how is my life", "I can't sleep properly",
                                     "will my medicine work", "my friend Mary is here", "tell me something"])
def test_m4_no_substring_or_common_word_names_an_area(message):
    from jyotish.conversation import areas_of
    assert areas_of(message) == []


# --- M5: a turn retries its failed sentences alone; the splitter; the turn's benchmark rows --------------------------

class OneWeak(OfflineTurnWriter):
    """Writes three tagged sentences, the second with a tier word; asked again, rewrites only that one."""
    def __init__(self):
        self.calls = []

    def __call__(self, system, user, errors):
        from jyotish.conversation import TurnDraft
        from jyotish.narrate import RETRY_HEAD
        self.calls.append(errors)
        body = json.loads(user)
        said = [x for x in body["engine_answer"] if x["tags"]][:3]
        self.last_meta = {"kind": "writer", "replayed": True}
        if errors and errors[0].startswith(RETRY_HEAD):
            return TurnDraft(answer=f"{said[1]['text'][:-1]} [{said[1]['tags'][0]}].")
        out = [f"{x['text'][:-1]} [{x['tags'][0]}]." for x in said]
        out[1] = out[1].replace("lean", "are weak and lean", 1)
        return TurnDraft(answer=" ".join(out))


def test_m5_a_turn_retries_its_failed_sentence_alone_and_it_stands_in_its_place(chart):
    from jyotish.narrate import RETRY_HEAD
    writer = OneWeak()
    route = route_turn("how is my career", chart)
    doc = answer_turn(chart, "how is my career", route, as_of=AS_OF, drafter=writer, checker=passes)
    assert len(writer.calls) == 2 and doc["attempts"] == 2 and doc["source"] == "writer"
    retry = writer.calls[1][0]
    assert retry.startswith(RETRY_HEAD) and "Held: 1 (" in retry and "3 (" in retry and "- sentence 2 (" in retry
    assert "tier language ('weak')" in retry
    assert [x["sentence"] for x in doc["removed"]] and "weak" in doc["removed"][0]["sentence"]
    assert len(doc["shown"]) == 3 and "weak" not in " ".join(doc["shown"])
    body = json.loads(__import__("jyotish.conversation", fromlist=["x"])._material(
        chart, "how is my career", route, engine_reading(chart, "how is my career", route.direction, route.areas,
                                                         as_of=AS_OF), [], AS_OF)[0])
    said = [x["text"] for x in body["engine_answer"] if x["tags"]][:3]
    assert doc["shown"] == said                          # the rewrite stands where its sentence was


def test_m5_a_retry_that_sends_the_wrong_count_is_not_placed(chart):
    class Whole(OneWeak):
        def __call__(self, system, user, errors):
            from jyotish.conversation import TurnDraft
            from jyotish.narrate import RETRY_HEAD
            draft = super().__call__(system, user, [] if errors and errors[0].startswith(RETRY_HEAD) else errors)
            return TurnDraft(answer=draft.answer + " " + draft.answer) if len(self.calls) > 1 else draft
    route = route_turn("how is my career", chart)
    doc = answer_turn(chart, "how is my career", route, as_of=AS_OF, drafter=Whole(), checker=passes)
    assert doc["attempts"] == 3 and len(doc["shown"]) == 2
    assert any("send exactly one sentence for each sentence listed" in r for x in doc["removed"] for r in x["reasons"])


@pytest.mark.parametrize("text,parts", [
    ("Mars is in Gemini [vote:father.varga]Your children carry their own [vote:children.karaka].",
     ["Mars is in Gemini [vote:father.varga]", "Your children carry their own [vote:children.karaka]."]),
    ("For purpose. [vote:father.varga]Your area [vote:x.y].", ["For purpose. [vote:father.varga]", "Your area [vote:x.y]."]),
    ("A [vote:x.y] [vote:z.w]. Then B [vote:a.b].", ["A [vote:x.y] [vote:z.w].", "Then B [vote:a.b]."]),
    ("A [vote:x.y]. b continues [vote:a.b].", ["A [vote:x.y]. b continues [vote:a.b]."]),
    ("A [tradition:BPHS 24]. Then B.", ["A [tradition:BPHS 24].", "Then B."]),
])
def test_m5_the_splitter_splits_after_a_tag_followed_by_a_capital(text, parts):
    from jyotish.narrate import sentences
    assert sentences(text) == parts


def test_m5_turn_sentences_are_a_benchmark_category():
    import importlib.util
    spec = importlib.util.spec_from_file_location("checker_bench", ROOT / "scripts" / "checker_bench.py")
    cb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cb)
    rows = [r for r in cb.load() if r["where"] == "answer"]
    assert len(rows) >= 15 and {r["label"] for r in rows} == {"accept", "reject"}
    cats = {r["category"] for r in rows}
    assert {"tier_word", "wrong_dignity", "unstated_claim", "leans_on_another_sentence", "unsupported_clause",
            "untagged"} <= cats
    pred = cb.run_validator(rows)
    assert all(pred[r["id"]][0] for r in rows if r["category"] in cb.WORDING)
    assert not any(pred[r["id"]][0] for r in rows if r["label"] == "accept")


# --- M1: a conversation can be erased, by its id or by its birth key, and at its end -----------------------------------

def _two_conversations(tmp_path, name):
    from fastapi.testclient import TestClient
    from jyotish.api import create_app
    db = f"sqlite:///{tmp_path / name}"
    app = create_app(db, today=lambda: AS_OF, turn_writer=OfflineTurnWriter, turn_checker=lambda: passes)
    with TestClient(app) as c:
        sids = [c.post("/sessions", json=BIRTH).json()["id"] for _ in range(2)]
        other = c.post("/sessions", json=dict(BIRTH, date="1990-01-01")).json()["id"]
        for sid in sids:
            n = c.post(f"/sessions/{sid}/turns", json={"message": "how is my career"}).json()["n"]
            wait_turn(c, f"/sessions/{sid}/turns/{n}")
    return db, app, sids, other


def test_m1_jyotish_session_erase_by_id_and_by_birth_key_is_logged(tmp_path, capsys):
    from jyotish.api import ErasureRow
    from jyotish.cli import main
    from jyotish.db import SessionRow, TurnRow
    db, app, sids, other = _two_conversations(tmp_path, "m1.db")
    def run(*argv):
        with pytest.raises(SystemExit) as done:
            main(list(argv))
        assert done.value.code == 0
    run("session", "erase", sids[0], "--by", "ray", "--database", db)
    assert "erased conversation" in capsys.readouterr().out
    with app.state.Session() as s:
        assert s.get(SessionRow, sids[0]) is None and s.query(TurnRow).filter_by(session_id=sids[0]).count() == 0
        assert s.get(SessionRow, sids[1]) is not None
        bkey = s.get(SessionRow, sids[1]).birth_key
    run("session", "erase", "--birth-key", bkey, "--by", "ray", "--database", db)
    with app.state.Session() as s:
        assert s.get(SessionRow, sids[1]) is None and s.get(SessionRow, other) is not None   # another birth stays
        logged = s.query(ErasureRow).order_by(ErasureRow.id).all()
        assert [(e.subject_id, e.erased_by, e.counts["sessions"], e.counts["turns"]) for e in logged] == [
            ("conversation", "ray", 1, 1), ("conversation", "ray", 1, 1)]
        assert all("birth" not in json.dumps(e.counts) for e in logged)


def test_m1_a_conversation_past_180_days_is_erased_at_start(tmp_path):
    from datetime import datetime, timedelta, timezone
    from fastapi.testclient import TestClient
    from jyotish.api import ErasureRow, create_app
    from jyotish.db import SessionRow, TurnRow
    db, app, sids, other = _two_conversations(tmp_path, "m1b.db")
    old = datetime.now(timezone.utc) - timedelta(days=181)
    with app.state.Session.begin() as s:
        s.get(SessionRow, sids[0]).created_at = old
        for t in s.query(TurnRow).filter_by(session_id=sids[0]):
            t.created_at = old
    with TestClient(create_app(db, today=lambda: AS_OF)) as c:                  # the service starts
        assert c.get("/health").status_code == 200
    with app.state.Session() as s:
        assert s.get(SessionRow, sids[0]) is None and s.get(SessionRow, sids[1]) is not None
        e = s.query(ErasureRow).one()
        assert (e.erased_by, e.counts["sessions"], e.counts["turns"]) == ("expiry", 1, 1)


# --- M6: scripts/live_timing.py --turn times the whole five-turn conversation --------------------------------------

def test_m6_live_timing_turn_runs_the_five_turn_conversation(monkeypatch, capsys):
    import importlib.util
    import jyotish.conversation as conv
    import jyotish.envfile
    spec = importlib.util.spec_from_file_location("live_timing", ROOT / "scripts" / "live_timing.py")
    lt = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lt)
    real = conv.answer_turn
    monkeypatch.setattr(jyotish.envfile, "load", lambda path: [])                 # no key read in the suite
    monkeypatch.setattr(conv, "answer_turn", lambda *a, **k: real(*a, **(k | {"drafter": OfflineTurnWriter(),
                                                                            "checker": passes})))
    assert lt.main(["--label", "five", "--turn", "--no-write", "--as-of", AS_OF.isoformat()]) == 0
    out = capsys.readouterr().out
    rows = [json.loads(x) for x in re.findall(r"^\{\n.*?^\}", out, re.S | re.M)]
    assert [r["question"] for r in rows] == list(lt.FIVE_TURNS) and [r["turn"] for r in rows] == [1, 2, 3, 4, 5]
    assert {r["conversation"] for r in rows} == {"five"} and rows[0]["session_s"] is not None
    assert [r["route"]["areas"] for r in rows[:4]] == [["father", "reputation", "siblings"], ["marriage"],
                                                       ["marriage"], ["marriage"]]
    assert rows[4]["source"] == "fixed" and rows[4]["route"]["off_limits"] == "death"


# --- L1: smaller points ----------------------------------------------------------------------------------------------

def test_l1_two_posts_at_once_give_409_never_500(tmp_path, monkeypatch):
    import threading
    import uuid as _uuid
    from fastapi.testclient import TestClient
    from jyotish import api
    app = api.create_app(f"sqlite:///{tmp_path / 'l1.db'}", today=lambda: AS_OF, turn_writer=OfflineTurnWriter,
                         turn_checker=lambda: passes)
    with TestClient(app) as c:
        sid = c.post("/sessions", json=BIRTH).json()["id"]
        gate = threading.Barrier(2)
        real = _uuid.uuid4

        def together():                               # both requests past the 409 check before either inserts
            gate.wait(5)
            return real()
        monkeypatch.setattr(api.uuid, "uuid4", together)
        out = []
        threads = [threading.Thread(target=lambda: out.append(
            c.post(f"/sessions/{sid}/turns", json={"message": "how is my career"}).status_code)) for _ in range(2)]
        [t.start() for t in threads]
        [t.join(30) for t in threads]
        monkeypatch.setattr(api.uuid, "uuid4", real)
        assert sorted(out) == [202, 409]
        wait_turn(c, f"/sessions/{sid}/turns/1")


def test_l1_the_writer_is_given_the_last_three_turns_only(tmp_path):
    from fastapi.testclient import TestClient
    from jyotish.api import create_app
    seen = []

    class Writer(OfflineTurnWriter):
        def __call__(self, system, user, errors):
            seen.append(json.loads(user))
            return super().__call__(system, user, errors)
    app = create_app(f"sqlite:///{tmp_path / 'l1b.db'}", today=lambda: AS_OF, turn_writer=Writer,
                     turn_checker=lambda: passes)
    messages = ["how is my career", "and marriage?", "what about money", "how is my mind", "and my home?"]
    with TestClient(app) as c:
        sid = c.post("/sessions", json=BIRTH).json()["id"]
        for m in messages:
            n = c.post(f"/sessions/{sid}/turns", json={"message": m}).json()["n"]
            wait_turn(c, f"/sessions/{sid}/turns/{n}")
    assert [len(x["earlier_turns"]) for x in seen] == [0, 1, 2, 3, 3]
    assert [t["question"] for t in seen[-1]["earlier_turns"]] == messages[1:4]


def test_l1_why_after_a_fixed_reply_explains_the_refusal(chart):
    from jyotish.client import client_warnings
    from jyotish.conversation import REPLIES, WHY_REPLIES
    first = route_turn("how is my career", chart)
    refused = route_turn("will I die early?", chart, first)
    why = route_turn("why?", chart, first, refused=refused.off_limits)
    assert (why.explains, why.off_limits, why.areas) == ("death", None, [])
    doc = answer_turn(chart, "why?", why, as_of=AS_OF)
    assert doc["source"] == "fixed" and doc["shown"] == [WHY_REPLIES["death"]]
    # After an answered turn, "why?" still explains the last answer.
    assert route_turn("why?", chart, first).areas == first.areas
    assert set(WHY_REPLIES) == set(REPLIES)
    assert not [w for r in WHY_REPLIES.values() for w in client_warnings(r, conversation=True)]
    assert "14416" in WHY_REPLIES["distress"]


def test_l1_why_after_a_fixed_reply_through_the_service(tmp_path):
    from fastapi.testclient import TestClient
    from jyotish.api import create_app
    from jyotish.conversation import WHY_REPLIES
    app = create_app(f"sqlite:///{tmp_path / 'l1c.db'}", today=lambda: AS_OF, turn_writer=OfflineTurnWriter,
                     turn_checker=lambda: passes)
    with TestClient(app) as c:
        sid = c.post("/sessions", json=BIRTH).json()["id"]
        for m in ("how is my career", "should I buy bitcoin", "why?"):
            n = c.post(f"/sessions/{sid}/turns", json={"message": m}).json()["n"]
            wait_turn(c, f"/sessions/{sid}/turns/{n}")
        assert c.get(f"/sessions/{sid}/turns/3").json()["answer"] == [WHY_REPLIES["trade"]]


def test_l1_off_limits_is_logged_by_the_service_not_by_routing(tmp_path, chart, caplog):
    import logging
    from fastapi.testclient import TestClient
    from jyotish import logs
    from jyotish.api import create_app
    logs.setup()
    logger = logging.getLogger(logs.LOGGER)
    logger.propagate = True
    try:
        with caplog.at_level(logging.INFO, logger=logs.LOGGER):
            route_turn("should I buy bitcoin", chart)
            assert not [r for r in caplog.records if r.getMessage() == "turn.off_limits"]
            app = create_app(f"sqlite:///{tmp_path / 'l1d.db'}", today=lambda: AS_OF)
            with TestClient(app) as c:
                sid = c.post("/sessions", json=BIRTH).json()["id"]
                n = c.post(f"/sessions/{sid}/turns", json={"message": "should I buy bitcoin"}).json()["n"]
                wait_turn(c, f"/sessions/{sid}/turns/{n}")
    finally:
        logger.propagate = False
    rec = [r for r in caplog.records if r.getMessage() == "turn.off_limits"]
    assert rec and all(r.fields == {"kind": "trade"} for r in rec)          # by kind only, never the message
