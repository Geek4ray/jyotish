"""The conversation's service (SPEC Layer 8, 2026-11-01; jyotish.api, jyotish.conversation): a session takes the
birth data once and shows the check line; each turn is queued, answered and streamed, and stored with the birth
key, its route, both answers, every removed sentence with its reasons, its cost and its timeline; the writer is
given the accepted text of earlier turns only; the ledger prices a turn. Offline: the writer is
conversation.OfflineTurnWriter, the checker a stub."""

import json
import time

import pytest
from fastapi.testclient import TestClient

from jyotish.api import create_app
from jyotish.conversation import OfflineTurnWriter
from jyotish.narrate import CheckResult, Proposition
from jyotish.reference import REFERENCE_LAT, REFERENCE_LON

BIRTH = {"date": "2001-03-12", "time": "10:10:25", "tz": "Asia/Kolkata", "lat": REFERENCE_LAT, "lon": REFERENCE_LON,
         "node": "mean", "place": "Rewari, Haryana", "as_of": "2026-10-21"}


class Writer(OfflineTurnWriter):
    """The offline writer, keeping every message it was sent."""
    seen: list = []

    def __call__(self, system, user, errors):
        Writer.seen.append(json.loads(user))
        return super().__call__(system, user, errors)


def passes(sentence, data):
    return CheckResult(propositions=[Proposition(text=sentence, supported=True, evidence="stub")])


def wait_turn(client, sid, n, timeout=90):
    t = time.monotonic()
    while time.monotonic() - t < timeout:
        r = client.get(f"/sessions/{sid}/turns/{n}").json()
        if r["status"] in ("done", "failed"):
            return r
        time.sleep(0.05)
    raise AssertionError(f"turn {n} still {r['status']}")


@pytest.fixture(scope="module")
def app(tmp_path_factory):
    db = tmp_path_factory.mktemp("sessions") / "jyotish.db"
    return create_app(f"sqlite:///{db}", turn_writer=Writer, turn_checker=lambda: passes)


@pytest.fixture(scope="module")
def client(app):
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def session(client):
    r = client.post("/sessions", json=BIRTH)
    assert r.status_code == 201, r.text
    return r.json()


def ask(client, sid, message):
    r = client.post(f"/sessions/{sid}/turns", json={"message": message})
    assert r.status_code == 202, r.text
    return wait_turn(client, sid, r.json()["n"])


@pytest.fixture(scope="module")
def two_turns(client, session):
    return ask(client, session["id"], "what are the challanges in my life"), ask(client, session["id"], "and marriage?")


def test_a_session_shows_the_check_line_before_any_question(session):
    assert session["check"] == {"lagna": "Taurus", "moon_sign": "Libra", "moon_nakshatra": "Chitra",
                                "words": "Taurus rising · Moon in Libra, Chitra"}
    assert session["chart_svg"] == f"/sessions/{session['id']}/chart.svg" and session["as_of"] == "2026-10-21"
    assert "chart_id" not in session                                          # a hash of birth data (review H7)


def test_a_turn_is_answered_and_the_client_sees_only_its_shown_text(two_turns):
    first, second = two_turns
    assert first["status"] == "done" and first["n"] == 1 and second["n"] == 2
    assert first["answer"] and not any("[vote:" in x or "[rule:" in x for x in first["answer"])
    assert set(first) == {"n", "question", "status", "answer", "paragraphs", "events"}    # nothing of the working


def test_each_turn_is_stored_with_its_route_both_answers_removed_sentences_cost_and_timeline(app, two_turns, session):
    from jyotish.db import LedgerRow, SessionRow, TurnRow
    with app.state.Session() as s:
        srow = s.get(SessionRow, session["id"])
        rows = s.query(TurnRow).filter_by(session_id=session["id"]).order_by(TurnRow.n).all()
        assert [r.birth_key for r in rows] == [srow.birth_key] * 2 and srow.birth_key
        first = rows[0]
        assert first.route["areas"] == ["father", "reputation", "siblings"] and first.route["direction"] == "against"
        assert rows[1].route["areas"] == ["marriage"] and rows[1].route["carried"] == ["direction"]
        doc = first.document
        assert doc["source"] == "writer" and doc["engine"]["sentences"] and doc["shown"]
        assert all(set(x) == {"sentence", "reasons", "attempt"} for x in doc["removed"])
        assert {"engine", "first_verified", "done"} <= set(doc["timeline"])
        ledger = s.get(LedgerRow, first.id)
        assert ledger is not None and ledger.kind == "turn" and ledger.writer_calls == 1


def test_the_writer_is_given_the_accepted_text_of_earlier_turns_only(two_turns):
    second = Writer.seen[1]
    assert second["earlier_turns"] == [{"question": "what are the challanges in my life",
                                        "answer": " ".join(two_turns[0]["answer"])}]
    assert "[vote:" not in json.dumps(second["earlier_turns"])          # the shown text, never a tagged draft


def test_the_events_stream_the_client_screen(client, session, two_turns):
    r = client.get(f"/sessions/{session['id']}/turns/1/live")
    kinds = [e["type"] for e in r.json()["events"]]
    assert kinds[0] == "light" and kinds[-1] == "done" and "text" in kinds
    with client.stream("GET", f"/sessions/{session['id']}/turns/1/events") as s:
        body = "".join(s.iter_text())
    assert "event: text" in body and "event: done" in body and "[vote:" not in body


def test_an_off_limits_turn_gets_its_fixed_reply_with_no_model_call(client, session, two_turns):
    before = len(Writer.seen)
    turn = ask(client, session["id"], "will I die early?")
    assert turn["answer"][0].startswith("Tatva does not answer questions about death")
    assert len(Writer.seen) == before


def test_one_turn_at_a_time_and_unknown_sessions(client, session, app):
    from jyotish.db import TurnRow
    assert client.get("/sessions/nope").status_code == 404
    assert client.post("/sessions/nope/turns", json={"message": "hi"}).status_code == 404
    with app.state.Session.begin() as s:
        s.add(TurnRow(id="x" * 32, session_id=session["id"], n=99, question="q", status="running"))
    try:
        assert client.post(f"/sessions/{session['id']}/turns", json={"message": "hi"}).status_code == 409
    finally:
        with app.state.Session.begin() as s:
            s.delete(s.get(TurnRow, "x" * 32))


def test_a_minors_session_is_marked(client):
    r = client.post("/sessions", json=dict(BIRTH, date="2015-06-01"))
    assert r.status_code == 201
    turn = ask(client, r.json()["id"], "when will I marry")
    assert turn["answer"][0].startswith("This chart belongs to someone under eighteen")


def test_the_whole_answer_failing_falls_back_to_the_engines_own(tmp_path):
    def refuses(sentence, data):
        return CheckResult(propositions=[Proposition(text=sentence, supported=False, evidence="stub")])
    app = create_app(f"sqlite:///{tmp_path / 'f.db'}", turn_writer=OfflineTurnWriter, turn_checker=lambda: refuses)
    with TestClient(app) as c:
        sid = c.post("/sessions", json=BIRTH).json()["id"]
        turn = ask(c, sid, "how is my career")
    from jyotish.db import TurnRow
    with app.state.Session() as s:
        doc = s.query(TurnRow).filter_by(session_id=sid).one().document
    assert doc["source"] == "engine" and doc["attempts"] == 3
    assert turn["answer"] == [x["text"] for x in doc["engine"]["sentences"]]
    assert all("the checker found it unsupported" in x["reasons"][0] for x in doc["removed"] if x["sentence"]
               and "[vote:" in x["sentence"])
