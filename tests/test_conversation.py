"""The seven-turn conversation on the reference chart (SPEC Layer 8, tests before the build is done, and Ray's two
questions of 2026-11-02): "what are the challanges in my life", "and marriage?", "when?", "why do you say that?",
"will I die early?", "how much money will i earn in my life, will i be rich", "whan and how". Each turn's route is
asserted and the engine's own answer frozen; the fifth gets the fixed reply with no model call. Then the same seven
turns through the service, offline (conversation.OfflineTurnWriter, a stub checker)."""

import time
from datetime import date

import pytest

from jyotish.conversation import OfflineTurnWriter, answer_turn, fixed_reply, route_turn
from jyotish.narrate import CheckResult, Proposition, engine_reading
from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
from jyotish.uncertainty import assess

AS_OF = date(2026, 10, 21)
MARRIAGE_TIER = "For marriage, most of what the chart shows agrees, and on balance it leans favourably."
MARRIAGE_AGAINST = ("The signs that show how others see marriage, Gemini, Cancer and Leo, lean unfavourably: "
                    "Rahu sits there, with no helpful planet beside.")
MONEY = "how much money will i earn in my life, will i be rich"
MONEY_TIER = "For money, most of what the chart shows agrees, and on balance it leans favourably."
TURNS = [
    ("what are the challanges in my life",
     dict(areas=["father", "reputation", "siblings"], direction="against", when=False, why=False, how=False, follow_up=False, carried=[],
          areas_from="weakest", off_limits=None, third_party=False, explains=None),
     None),                                          # frozen in tests/test_engine_reading.py (CHALLENGES)
    ("and marriage?",
     dict(areas=["marriage"], direction="against", when=False, why=False, how=False, follow_up=True, carried=["direction"],
          areas_from="named", off_limits=None, third_party=False, explains=None),
     [MARRIAGE_TIER, MARRIAGE_AGAINST]),
    ("when?",
     dict(areas=["marriage"], direction="against", when=True, why=False, how=False, follow_up=True, carried=["areas", "direction"],
          areas_from="carried", off_limits=None, third_party=False, explains=None),
     ["A chart gives no date for an event; what it shows are the stretches it reads as more and less favourable for "
      "marriage.",                                   # the question as asked (2026-11-02)
      MARRIAGE_TIER,                                 # the hard part was said in the last turn: left out (2026-11-02)
      "The least favourable stretch for marriage, as the chart reads it, runs from August 2029 to October 2029.",
      "The most favourable stretch runs from January 2030 to October 2031.",
      "Neither stretch is a prediction of when you will act."]),
    ("why do you say that?",
     dict(areas=["marriage"], direction="against", when=False, why=True, how=False, follow_up=True, carried=["areas", "direction"],
          areas_from="carried", off_limits=None, third_party=False, explains=None),
     ["Here is what in your chart lies behind it.",  # what the last turns said is left out (2026-11-02)
      MARRIAGE_TIER,
      "Taken together, the houses that govern marriage lean favourably, though the main one, the 7th house from your "
      "rising sign, in Scorpio, is less supported than most of your twelve houses.",
      "The planets that rule the houses of marriage lean favourably; Mars, which rules the 7th house, sits in Scorpio in "
      "your 7th house, in its own sign.",
      "The planets that signify marriage lean favourably; the main one, Venus, sits in Pisces in your 11th house, "
      "exalted, where it is at its best.",
      "The divisional chart for marriage leans favourably; there Saturn falls in Capricorn, in its own sign.",
      "The reading of the exact start of each house leans favourably for marriage.",
      "Mars, a ruler of the day you were born, leans favourably for marriage."]),
    ("will I die early?",
     dict(areas=["marriage"], direction="against", when=False, why=False, how=False, follow_up=True, carried=["areas", "direction"],
          areas_from="carried", off_limits="death", third_party=False, explains=None),
     None),
    (MONEY,
     dict(areas=["wealth"], direction="both", when=False, why=False, how=False, follow_up=False, carried=[],
          areas_from="named", off_limits=None, third_party=False, explains=None),
     ["A chart gives no amount and makes no promise; what it shows is how well it supports money.",
      MONEY_TIER,
      "Taken together, the houses that govern money lean favourably: the main one, the 2nd house from your rising "
      "sign, in Gemini, is better supported than most of your twelve houses.",
      "The planets that rule the houses of money lean favourably; Mercury, which rules the 2nd house, sits in Aquarius "
      "in your 10th house, in a neutral sign.",
      "The planets that signify money lean favourably; the main one, Jupiter, sits in Taurus in your 1st house, in an "
      "unfriendly sign.",
      "The rulers of the day you were born, Mars and the Moon, lean favourably for money.",
      "The signs that show how others see money, Libra and Cancer, lean unfavourably: the Moon sits there, with no "
      "helpful planet beside."]),
    ("whan and how",
     dict(areas=["wealth"], direction="both", when=True, why=False, how=True, follow_up=True,
          carried=["areas", "direction"], areas_from="carried", off_limits=None, third_party=False, explains=None),
     ["A chart gives no date for an event; what it shows are the stretches it reads as more and less favourable for "
      "money.",
      "What lies behind it is what the answer before set out; the chart has no further reason to add.",
      MONEY_TIER,
      "The most favourable stretch for money, as the chart reads it, runs from October 2029 to June 2032.",
      "The least favourable stretch runs from November 2028 to October 2029.",
      "Neither stretch is a prediction of when you will act."]),
]


@pytest.fixture(scope="module")
def chart():
    return assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)


def passes(sentence, data):
    return CheckResult(propositions=[Proposition(text=sentence, supported=True, evidence="stub")])


@pytest.fixture(scope="module")
def conversation(chart):
    """The seven turns, each answered with the offline writer, the earlier turns' shown text given to the next."""
    out, last, history = [], None, []

    class Writer(OfflineTurnWriter):
        calls = 0

        def __call__(self, system, user, errors):
            Writer.calls += 1
            return super().__call__(system, user, errors)
    for message, _, _ in TURNS:
        route = route_turn(message, chart, last)
        before = Writer.calls
        doc = answer_turn(chart, message, route, as_of=AS_OF, history=list(history), drafter=Writer(), checker=passes)
        out.append((route, doc, Writer.calls - before))
        history.append({"question": message, "answer": " ".join(doc["shown"])})
        if not route.off_limits:
            last = route
    return out


@pytest.mark.parametrize("k", range(len(TURNS)))
def test_each_turns_route(conversation, k):
    route, _, _ = conversation[k]
    assert route.model_dump() == TURNS[k][1]


@pytest.mark.parametrize("k", [1, 2, 3, 5, 6])
def test_each_turns_engine_answer_is_frozen(conversation, k):
    _, doc, _ = conversation[k]
    assert [s["text"] for s in doc["engine"]["sentences"]] == TURNS[k][2]


def test_the_first_turn_is_the_frozen_challenges_answer(conversation):
    from test_engine_reading import CHALLENGES
    assert [s["text"] for s in conversation[0][1]["engine"]["sentences"]] == CHALLENGES


def test_the_fifth_turn_gets_the_fixed_reply_with_no_model_call(conversation):
    route, doc, calls = conversation[4]
    assert doc["source"] == "fixed" and doc["shown"] == [fixed_reply("death")] and calls == 0 and doc["engine"] is None


def test_a_when_turn_ends_with_the_engines_dates_and_the_why_turn_rests_on_both_sides(conversation):
    _, when, _ = conversation[2]
    assert when["shown"][-3:] == TURNS[2][2][-3:]                # the writer writes no date; the engine's follow
    _, why, _ = conversation[3]
    assert any("favourably" in s and "unfavourably" not in s for s in why["shown"])


def test_rays_two_turns_open_on_the_question_as_asked(conversation):
    from jyotish.conversation import opens_on
    (_, money, _), (_, how, _) = conversation[5], conversation[6]
    assert money["kinds"] == ["amount"] and how["kinds"] == ["when", "why"]
    assert money["shown"][0] == TURNS[5][2][0] and opens_on(money["shown"][0], money["kinds"])
    assert money["opened_by"] == "writer" and how["opened_by"] == "writer"
    assert how["shown"][0] == TURNS[6][2][0] and how["shown"][-1] == "Neither stretch is a prediction of when you will act."
    assert not set(how["shown"][1:]) & set(money["shown"])            # restates nothing of the money answer


def test_the_engine_answer_is_the_same_as_engine_reading_called_directly(chart, conversation):
    route, doc, _ = conversation[1]
    direct = engine_reading(chart, "and marriage?", route.direction, route.areas, as_of=AS_OF, when=route.when)
    assert doc["engine"] == direct.model_dump()


def test_the_seven_turns_through_the_service(tmp_path):
    from fastapi.testclient import TestClient
    from jyotish.api import create_app
    from jyotish.db import TurnRow
    app = create_app(f"sqlite:///{tmp_path / 'c.db'}", turn_writer=OfflineTurnWriter, turn_checker=lambda: passes,
                     today=lambda: AS_OF)
    birth = {"date": "2001-03-12", "time": "10:10:25", "tz": "Asia/Kolkata", "lat": REFERENCE_LAT, "lon": REFERENCE_LON,
             "node": "mean", "place": "Rewari, Haryana"}         # the date is the server's (`today`, review M2)
    with TestClient(app) as c:
        sid = c.post("/sessions", json=birth).json()["id"]
        for message, _, _ in TURNS:
            n = c.post(f"/sessions/{sid}/turns", json={"message": message}).json()["n"]
            t = time.monotonic()
            while c.get(f"/sessions/{sid}/turns/{n}").json()["status"] not in ("done", "failed"):
                assert time.monotonic() - t < 90
                time.sleep(0.05)
        session = c.get(f"/sessions/{sid}").json()
    assert [t["status"] for t in session["turns"]] == ["done"] * len(TURNS)
    assert session["turns"][4]["answer"] == [fixed_reply("death")]
    with app.state.Session() as s:
        rows = s.query(TurnRow).filter_by(session_id=sid).order_by(TurnRow.n).all()
        assert [r.route for r in rows] == [t[1] for t in TURNS]
        for r, (_, _, engine) in [*zip(rows[1:4], TURNS[1:4]), *zip(rows[5:], TURNS[5:])]:
            assert [x["text"] for x in r.document["engine"]["sentences"]] == engine
