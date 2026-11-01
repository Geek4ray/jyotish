"""The astrologer's review of a conversation (SPEC Layer 8, 2026-11-01): the review page lists a session's turns
beside the sheet and the engine's own answer, the sentences removed with their reasons; a reviewer's rewrite of a
sentence is held to the turn's checks and stored as a reading's edits are; jyotish export-reviews includes turns.
Offline: the writer is conversation.OfflineTurnWriter, the checker a stub."""

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
AUTH = {"Authorization": "Bearer tok-1"}


def passes(sentence, data):
    return CheckResult(propositions=[Proposition(text=sentence, supported=True, evidence="stub")])


@pytest.fixture(scope="module")
def db(tmp_path_factory):
    return tmp_path_factory.mktemp("review") / "jyotish.db"


@pytest.fixture(scope="module")
def app(db):
    return create_app(f"sqlite:///{db}", turn_writer=OfflineTurnWriter, turn_checker=lambda: passes,
                      reviewers={"tok-1": "judge-1"}, review_checker=passes)


@pytest.fixture(scope="module")
def client(app):
    with TestClient(app) as c:
        yield c


def ask(client, sid, message):
    n = client.post(f"/sessions/{sid}/turns", json={"message": message}).json()["n"]
    t = time.monotonic()
    while time.monotonic() - t < 90:
        r = client.get(f"/sessions/{sid}/turns/{n}").json()
        if r["status"] in ("done", "failed"):
            return r
        time.sleep(0.05)
    raise AssertionError("turn not answered")


@pytest.fixture(scope="module")
def sid(client):
    sid = client.post("/sessions", json=BIRTH).json()["id"]
    ask(client, sid, "what are the challanges in my life")
    ask(client, sid, "will I die early?")
    return sid


def test_the_review_needs_a_reviewer(client, sid):
    assert client.get(f"/sessions/{sid}/review").status_code == 401
    assert client.get(f"/review/sessions/{sid}").status_code == 200          # the page itself is static


def test_each_turn_is_listed_beside_the_engines_answer_and_the_sheet(client, sid, app):
    v = client.get(f"/sessions/{sid}/review", headers=AUTH).json()
    first, second = v["turns"]
    assert first["route"]["areas"] == ["father", "children", "gains"] and first["source"] == "writer"
    assert first["engine"]["sentences"][0]["text"] == ("This chart does not emphasise your father; on balance its "
                                                         "indications lean favourably.")
    assert all(n["text"] for s in first["engine"]["sentences"] for n in s["notes"])      # footnotes quote the sheet
    assert set(v["sheets"]) == {"father", "children", "gains"} and v["sheets"]["father"]["points"][0]["n"] == 1
    assert [u["target"] for u in first["units"]] == [f"answer:{i}" for i in range(len(first["units"]))]
    assert first["units"][1]["tagged"].endswith("[vote:father.house].")                # the tags stay the reviewer's
    assert first["removed"] == [] and second["source"] == "fixed" and second["route"]["off_limits"] == "death"
    from jyotish.db import ExclusionRow, ReviewRow, SessionRow
    with app.state.Session() as s:
        chart_id = s.get(SessionRow, sid).chart_id
        assert s.query(ReviewRow).filter_by(action="open", target=f"session:{sid}").count() >= 1
        assert s.get(ExclusionRow, chart_id) is not None                                  # seen in review


def test_an_accepted_rewrite_is_what_the_client_reads_and_is_stored_as_an_edit(client, sid, app):
    new = "The house of your father is among the weakest of your twelve houses."
    r = client.post(f"/sessions/{sid}/turns/1/review/edit", headers=AUTH,
                    json={"target": "answer:1", "text": new, "keep_tags": True}).json()
    assert r["accepted"], r["errors"]
    assert client.get(f"/sessions/{sid}/turns/1").json()["answer"][1] == new           # tags off for the client
    turn = r["review"]["turns"][0]
    assert turn["units"][1]["tagged"] == new[:-1] + " [vote:father.house]." and turn["edited"][0]["by"] == "judge-1"
    from jyotish.db import ReviewRow, TurnRow
    with app.state.Session() as s:
        t = s.query(TurnRow).filter_by(session_id=sid, n=1).one()
        row = s.query(ReviewRow).filter_by(turn_id=t.id, action="edit").one()
        assert row.accepted and row.reading_id is None and row.reviewer_id == "judge-1" and row.target == "answer:1"


def test_a_rewrite_that_fails_the_checks_is_refused_and_not_saved(client, sid):
    before = client.get(f"/sessions/{sid}/turns/1").json()["answer"][2]
    r = client.post(f"/sessions/{sid}/turns/1/review/edit", headers=AUTH,
                    json={"target": "answer:2", "text": "Your father's indications are weak.", "keep_tags": True}).json()
    assert not r["accepted"] and any("tier language" in e for e in r["errors"])
    assert client.get(f"/sessions/{sid}/turns/1").json()["answer"][2] == before
    # A word choice is a warning, not a refusal (SPEC Layer 8).
    w = client.post(f"/sessions/{sid}/turns/1/review/edit", headers=AUTH,
                    json={"target": "answer:2", "text": "The Sun is the main karaka of your father.", "keep_tags": True}).json()
    assert w["accepted"] and any("'karaka' has a plain phrase" in x for x in w["warnings"])
    assert client.post(f"/sessions/{sid}/turns/2/review/edit", headers=AUTH,
                       json={"target": "answer:0", "text": "x"}).status_code == 409              # a fixed reply


def test_export_reviews_includes_turns(client, sid, db, tmp_path):
    from jyotish.export import export_reviews
    n = export_reviews(f"sqlite:///{db}", tmp_path)
    turns = [json.loads(x) for x in (tmp_path / "turns.jsonl").read_text().splitlines()]
    rewrites = [json.loads(x) for x in (tmp_path / "rewrites.jsonl").read_text().splitlines()[1:]]
    assert turns[0]["kind"] == "header" and "judgements, not outcomes" in turns[0]["note"]
    assert n["turns"] == len(turns) - 1 >= 1
    t1 = next(x for x in turns[1:] if x["n"] == 1)
    assert t1["question"] == "what are the challanges in my life" and t1["engine_answer"] and t1["edits"]
    assert {r["turn_id"] for r in rewrites if r.get("turn_id")} == {t1["turn_id"]}
    assert all("birth" not in r for r in rewrites + turns[1:])                          # no birth data by default
