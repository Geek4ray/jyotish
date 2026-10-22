"""The review step (SPEC Layer 6b item 3), offline: the model replayed from the edited
fixture, edited sentences checked by a stub checker, a reviewer token from the app's config."""

import json
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from jyotish.api import ExclusionRow, ReadingRow, ReviewRow, create_app, excluded_charts
from jyotish.narrate import CheckResult, Proposition, Reading
from jyotish.reference import REFERENCE_LAT, REFERENCE_LON

FIXTURES = Path(__file__).parent / "fixtures"
EDITED = str(FIXTURES / "narration_career_edited.json")
BODY = {"date": "2001-03-12", "time": "10:10:25", "tz": "Asia/Kolkata", "lat": REFERENCE_LAT, "lon": REFERENCE_LON,
        "node": "mean", "place": "Rewari, Haryana", "question": "How will my career go?", "as_of": "2026-10-21",
        "depth": "astrologer"}
AUTH = {"Authorization": "Bearer test-token-1"}


class Checker:
    """Supports every proposition, except in a sentence containing REJECTED."""
    def __init__(self):
        self.calls = []

    def __call__(self, sentence, derivation):
        self.calls.append((sentence, derivation))
        if "REJECTED" in sentence:
            return CheckResult(propositions=[Proposition(text="REJECTED", supported=False, evidence="not in the data")])
        return CheckResult(propositions=[Proposition(text=sentence, supported=True, evidence="stub")])


@pytest.fixture(scope="module")
def setup(tmp_path_factory):
    checker = Checker()
    app = create_app(f"sqlite:///{tmp_path_factory.mktemp('review') / 'r.db'}", model_fixture=EDITED,
                     reviewers={"test-token-1": "judge-1"}, review_checker=checker)
    with TestClient(app) as c:
        rid = c.post("/readings", json=BODY).json()["id"]
        for _ in range(400):
            s = c.get(f"/readings/{rid}").json()
            if s["status"] in ("done", "failed"):
                break
            time.sleep(0.05)
        assert s["status"] == "done"
        yield app, c, rid, checker


def test_a_new_reading_is_a_draft_and_says_nothing_of_review(setup):
    _, c, rid, _ = setup
    s = c.get(f"/readings/{rid}").json()
    assert s["review_status"] == "draft" and s["reading"]["review"] == {"status": "draft"}
    assert "Reviewed by" not in s["page"]


def test_reviewer_needs_the_token(setup):
    _, c, rid, _ = setup
    assert c.get(f"/readings/{rid}/review").status_code == 401
    assert c.get(f"/readings/{rid}/review", headers={"Authorization": "Bearer wrong"}).status_code == 401
    assert c.post(f"/readings/{rid}/review/approve").status_code == 401
    assert c.get("/readings/nope/review", headers=AUTH).status_code == 404


def test_opening_lists_every_sentence_and_excludes_the_chart(setup):
    app, c, rid, _ = setup
    v = c.get(f"/readings/{rid}/review", headers=AUTH).json()
    reading = Reading(**v["reading"])
    targets = [u["target"] for u in v["units"]]
    assert targets[0] == "summary:0" and f"claim:career:vote:career.house" in targets
    assert sum(t.startswith("claim:career:") for t in targets) == len(reading.areas[0].claims)
    assert v["history"][-1]["action"] == "open" and v["history"][-1]["reviewer"] == "judge-1"
    with app.state.Session() as s:
        ex = s.get(ExclusionRow, v["chart_id"])
        assert ex is not None and ex.reviewer_id == "judge-1" and ex.reading_id == rid
        assert v["chart_id"] in excluded_charts(s)                      # the learning set leaves it out
        opened = s.query(ReviewRow).filter_by(reading_id=rid, action="open").first()
        assert opened.chart_id == v["chart_id"] and opened.created_at is not None


def test_an_edit_that_passes_the_validator_and_checker_replaces_the_sentence(setup):
    app, c, rid, checker = setup
    target = "claim:career:vote:career.house"
    text = "The house vote is for career, though the 10th house from the lagna is the lowest in strength [vote:career.house]."
    n = len(checker.calls)
    r = c.post(f"/readings/{rid}/review/edit", headers=AUTH, json={"target": target, "text": text}).json()
    assert r["accepted"] and r["errors"] == [] and len(checker.calls) == n + 1
    assert '"finding_id": "vote:career.house"' in checker.calls[-1][1]          # checked against its derivation
    reading = Reading(**r["review"]["reading"])
    claim = next(x for x in reading.areas[0].claims if x.finding_id == "vote:career.house")
    assert claim.text == text and claim.cites == ["vote:career.house"] and claim.edited["by"] == "judge-1"
    page = c.get(f"/readings/{rid}").json()["page"]
    assert "though the 10th house from the lagna is the lowest in strength[^" in page   # the client sees it (tag as footnote)
    with app.state.Session() as s:
        row = s.query(ReviewRow).filter_by(reading_id=rid, action="edit").order_by(ReviewRow.id.desc()).first()
        assert (row.target, row.accepted, row.after, row.reviewer_id) == (target, True, text, "judge-1")
        assert row.before.startswith("The house vote is for career: the 10th from lagna")


@pytest.mark.parametrize("target,text,needle", [
    ("claim:career:vote:career.house", "The house vote is for career.", "claim without a tag"),
    ("claim:career:vote:career.house", "The house vote will likely help [vote:career.house].", "probability"),
    ("claim:career:vote:career.house", "The house vote is for career [rule:yoga.ruchaka].", "not offered"),
    ("summary:0", "Career is strong here [rule:yoga.kendra_trikona_raja].", "tier language"),
    ("claim:career:vote:career.house", "The house vote REJECTED is for career [vote:career.house].", "unsupported"),
])
def test_an_edit_that_fails_a_check_is_refused_and_logged(setup, target, text, needle):
    app, c, rid, _ = setup
    before = c.get(f"/readings/{rid}").json()["reading"]
    r = c.post(f"/readings/{rid}/review/edit", headers=AUTH, json={"target": target, "text": text}).json()
    assert r["accepted"] is False and any(needle in e for e in r["errors"]), r["errors"]
    assert c.get(f"/readings/{rid}").json()["reading"] == before                  # nothing changed
    with app.state.Session() as s:
        row = s.query(ReviewRow).filter_by(reading_id=rid, action="edit").order_by(ReviewRow.id.desc()).first()
        assert row.accepted is False and row.after == text and row.errors


def test_a_reference_to_another_sentence_has_its_own_plain_reason():
    from jyotish.narrate import validate
    from jyotish.review import plain_reasons
    e = validate("The same conjunction forms Budhaditya yoga [rule:yoga.budhaditya].", {"rule:yoga.budhaditya"})
    assert plain_reasons(e) == [{"code": "reference", "detail": "The same"}]
    assert plain_reasons(["refers to another claim ('again'): a claim stands alone and is checked against its finding only: 'x'"]) \
        == [{"code": "reference", "detail": "again"}]


def test_unknown_targets_are_refused(setup):
    _, c, rid, _ = setup
    assert c.post(f"/readings/{rid}/review/edit", headers=AUTH, json={"target": "claim:career:nope", "text": "x"}).status_code == 404
    assert c.post(f"/readings/{rid}/review/note", headers=AUTH, json={"area": "nowhere", "text": "x"}).status_code == 422


def test_the_astrologers_note_is_stored_and_shown_apart(setup):
    _, c, rid, _ = setup
    text = "In my practice this placement shows late but lasting recognition.\nSecond line."
    v = c.post(f"/readings/{rid}/review/note", headers=AUTH, json={"area": "career", "text": text}).json()
    note = Reading(**v["reading"]).areas[0].astrologer_note
    assert note["text"] == text and note["by"] == "judge-1"
    page = c.get(f"/readings/{rid}").json()["page"]
    assert "> **The astrologer's note** (judge-1," in page and "not checked by the engine)" in page
    assert "> In my practice this placement shows late but lasting recognition." in page
    assert v["history"][-1]["action"] == "note" and v["history"][-1]["target"] == "note:career"


def test_approval_makes_the_reading_reviewed_and_the_page_says_by_whom(setup):
    _, c, rid, _ = setup
    assert "Reviewed by" not in c.get(f"/readings/{rid}").json()["page"]
    v = c.post(f"/readings/{rid}/review/approve", headers=AUTH).json()
    assert v["review_status"] == "reviewed"
    s = c.get(f"/readings/{rid}").json()
    assert s["review_status"] == "reviewed" and s["reading"]["review"]["reviewed_by"] == "judge-1"
    assert "**Reviewed by judge-1**" in s["page"]
    assert [h["action"] for h in v["history"]].count("approve") == 1


def test_reviewers_come_from_the_environment(monkeypatch, tmp_path):
    from jyotish.api import reviewers_from_env
    monkeypatch.setenv("JYOTISH_REVIEWERS", "judge-1:abc, judge-2:def,broken")
    assert reviewers_from_env() == {"abc": "judge-1", "def": "judge-2"}


def test_an_older_database_gets_the_review_column(tmp_path):
    from sqlalchemy import create_engine, inspect, text
    db = tmp_path / "old.db"
    engine = create_engine(f"sqlite:///{db}")
    with engine.begin() as conn:                              # the readings table as it was before the review step
        conn.execute(text("CREATE TABLE readings (id VARCHAR(32) PRIMARY KEY, chart_id VARCHAR(64), question TEXT, "
                          "request JSON, status VARCHAR(16), progress JSON, document JSON, page TEXT, error JSON, "
                          "created_at DATETIME, updated_at DATETIME)"))
    create_app(f"sqlite:///{db}")
    cols = {c["name"] for c in inspect(create_engine(f"sqlite:///{db}")).get_columns("readings")}
    assert "review_status" in cols


# --- the structured verdict: judgement data, logged, never shown to the client ---------------

def test_a_verdict_is_recorded_and_the_client_sees_nothing_of_it(setup):
    app, c, rid, _ = setup
    before = c.get(f"/readings/{rid}").json()
    v = c.post(f"/readings/{rid}/review/verdict", headers=AUTH,
               json={"area": "career", "verdict": "partly", "reason": "wrong_timing"}).json()
    assert v["verdicts"]["career"]["verdict"] == "partly" and v["verdicts"]["career"]["reason"] == "wrong_timing"
    with app.state.Session() as s:
        row = s.query(ReviewRow).filter_by(reading_id=rid, action="verdict").order_by(ReviewRow.id.desc()).first()
        assert (row.area, row.verdict, row.reason, row.reviewer_id) == ("career", "partly", "wrong_timing", "judge-1")
        assert row.chart_id == before["chart_id"] and row.created_at is not None and row.target == "verdict:career"
    after = c.get(f"/readings/{rid}").json()
    assert after["reading"] == before["reading"] and after["page"] == before["page"]        # unchanged
    assert "partly" not in after["page"] and "wrong_timing" not in json.dumps(after["reading"])
    # A later verdict on the same area is the one shown to the reviewer; both are logged.
    v = c.post(f"/readings/{rid}/review/verdict", headers=AUTH, json={"area": "career", "verdict": "agree"}).json()
    assert v["verdicts"]["career"] == {**v["verdicts"]["career"], "verdict": "agree", "reason": None}
    assert [h["verdict"] for h in v["history"] if h["action"] == "verdict"][-2:] == ["partly", "agree"]


@pytest.mark.parametrize("body,status", [
    ({"area": "career", "verdict": "disagree"}, 422),                                   # not agree: needs a reason
    ({"area": "career", "verdict": "agree", "reason": "other"}, 422),                   # agree takes none
    ({"area": "career", "verdict": "maybe", "reason": "other"}, 422),
    ({"area": "career", "verdict": "partly", "reason": "bad_vibes"}, 422),
    ({"area": "nowhere", "verdict": "agree"}, 422),
])
def test_a_verdict_is_checked(setup, body, status):
    _, c, rid, _ = setup
    assert c.post(f"/readings/{rid}/review/verdict", headers=AUTH, json=body).status_code == status
    assert c.post(f"/readings/{rid}/review/verdict", json={"area": "career", "verdict": "agree"}).status_code == 401


# --- the guided review: answers logged step by step; blind mode (the judge page) ------------

CURIOUS = str(FIXTURES / "narration_curious.json")
CURIOUS_BODY = dict(BODY, question="How will my career go, and when is the best time for a job change?",
                    depth="curious", lat=28.1989, lon=76.617)
ENGINE_WORDS = __import__("re").compile(r"\b(votes?|tests?|famil(?:y|ies)|checker)\b", __import__("re").I)


def _reading(c, body=CURIOUS_BODY):
    rid = c.post("/readings", json=body).json()["id"]
    for _ in range(600):
        s = c.get(f"/readings/{rid}").json()
        if s["status"] in ("done", "failed"):
            break
        time.sleep(0.05)
    assert s["status"] == "done"
    return rid


@pytest.fixture()
def guided(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'g.db'}", model_fixture=CURIOUS,
                     reviewers={"tok-1": "judge-1", "tok-2": "judge-2"}, review_checker=Checker())
    with TestClient(app) as c:
        yield app, c, _reading(c)


J1, J2 = {"Authorization": "Bearer tok-1"}, {"Authorization": "Bearer tok-2"}


def test_each_answer_is_logged_with_step_area_answer_reviewer_and_time(guided):
    app, c, rid = guided
    v = c.get(f"/readings/{rid}/review", headers=J1).json()
    assert v["reviewer"] == "judge-1" and v["mode"] == "review" and not v["intro_done"] and v["answers"] == []
    for step, area, answer in [("intro", None, "done"), ("match", "career", "partly"),
                               ("off", "career", {"reasons": ["timing", "wording"], "line": "the 10th is underplayed"}),
                               ("sentences", "career", {"decisions": {"paragraph:career:0": "keep"}}),
                               ("note", "career", {"text": ""}),
                               ("period", "career", {"choice": "later", "from": "2030-01", "to": "2031-06"})]:
        r = c.post(f"/readings/{rid}/review/answer", headers=J1, json={"step": step, "area": area, "answer": answer})
        assert r.status_code == 200, r.text
    v = r.json()
    assert v["intro_done"] and [(a["step"], a["area"]) for a in v["answers"]][:2] == [("intro", None), ("match", "career")]
    with app.state.Session() as s:
        rows = s.query(ReviewRow).filter_by(reading_id=rid, action="answer").order_by(ReviewRow.id).all()
        assert [(r.step, r.area, r.reviewer_id, r.mode) for r in rows][-1] == ("period", "career", "judge-1", "review")
        assert rows[2].answer == {"reasons": ["timing", "wording"], "line": "the 10th is underplayed"}
        assert all(r.created_at is not None and r.chart_id == v["chart_id"] for r in rows)
        assert rows[1].verdict == "partly"                                   # step 1 is also the area's verdict
    assert c.get(f"/readings/{rid}/review", headers=J1).json()["verdicts"]["career"]["verdict"] == "partly"
    # Answers are judgement data: the client's reading and page are untouched by them.
    client = c.get(f"/readings/{rid}").json()
    assert "underplayed" not in client["page"] and "underplayed" not in json.dumps(client["reading"])
    # The introduction is once per reviewer: a second reading opens without it.
    rid2 = _reading(c)
    assert c.get(f"/readings/{rid2}/review", headers=J1).json()["intro_done"]
    assert not c.get(f"/readings/{rid2}/review", headers=J2).json()["intro_done"]


@pytest.mark.parametrize("body", [
    {"step": "guess", "area": "career", "answer": "agree"},
    {"step": "match", "area": "career", "answer": "maybe"},
    {"step": "match", "area": "nowhere", "answer": "agree"},
    {"step": "intro", "area": "career", "answer": "done"},
    {"step": "off", "area": "career", "answer": {"reasons": []}},
    {"step": "off", "area": "career", "answer": {"reasons": ["bad_vibes"]}},
    {"step": "period", "area": "career", "answer": {"choice": "earlier"}},                       # no range
    {"step": "period", "area": "career", "answer": {"choice": "earlier", "from": "2031-01", "to": "2030-01"}},
    {"step": "blind_reading", "area": "career", "answer": "promising"},                           # blind mode only
    {"step": "note", "area": "career", "answer": {"text": "x"}, "mode": "judge"},
])
def test_an_answer_is_checked(guided, body):
    _, c, rid = guided
    assert c.post(f"/readings/{rid}/review/answer", headers=J1, json=body).status_code == 422
    assert c.post(f"/readings/{rid}/review/answer", json={"step": "intro", "answer": "done"}).status_code == 401


def test_blind_mode_withholds_each_area_until_answered_from_the_chart_alone(guided):
    app, c, rid = guided
    full = c.get(f"/readings/{rid}").json()["reading"]
    paragraph = {a["name"]: a["paragraph"] for a in full["areas"]}
    v = c.get(f"/readings/{rid}/review?mode=blind", headers=J2).json()
    text = json.dumps(v)
    assert v["mode"] == "blind" and v["shown"] == [] and v["units"] == [] and "page" not in v
    assert all(p[:60] not in text for p in paragraph.values())                     # not sent at all
    assert v["reading"]["areas"] == [{"name": "career", "has_windows": True, "hidden": True},
                                     {"name": "marriage", "has_windows": False, "hidden": True},
                                     {"name": "longevity", "has_windows": False, "hidden": True}]
    assert "summary" not in v["reading"] and "2029-10-23" not in text                   # no windows either
    with app.state.Session() as s:                                                      # opening blind is not seeing
        assert s.get(ExclusionRow, v["chart_id"]) is None
    post = lambda body, mode="blind": c.post(f"/readings/{rid}/review/answer", headers=J2, json=dict(body, mode=mode))
    assert post({"step": "match", "area": "career", "answer": "agree"}).status_code == 409
    assert c.post(f"/readings/{rid}/review/edit?mode=blind", headers=J2,
                  json={"target": "paragraph:career:0", "text": "x", "keep_tags": True}).status_code == 409
    assert c.post(f"/readings/{rid}/review/approve?mode=blind", headers=J2).status_code == 409
    assert post({"step": "blind_reading", "area": "career", "answer": "promising"}).json()["shown"] == []   # windows too
    v = post({"step": "blind_period", "area": "career", "answer": {"from": "2027-06", "to": "2028-12"}}).json()
    assert v["shown"] == ["career"]
    career = next(a for a in v["reading"]["areas"] if a["name"] == "career")
    assert career["paragraph"] == paragraph["career"] and career["windows"]
    assert {u["area"] for u in v["units"]} == {"career"}
    assert all("hidden" in a for a in v["reading"]["areas"] if a["name"] != "career")
    with app.state.Session() as s:                                                      # now the reading is seen
        assert s.get(ExclusionRow, v["chart_id"]) is not None
    # The answers from the chart alone stand: once shown, they cannot be changed.
    assert post({"step": "blind_reading", "area": "career", "answer": "difficult"}).status_code == 409
    assert post({"step": "match", "area": "career", "answer": "agree"}).status_code == 200
    # An area without windows needs only the reading from the chart alone.
    assert post({"step": "blind_reading", "area": "marriage", "answer": "mixed"}).json()["shown"] == ["career", "marriage"]
    # The review mode of the same reviewer sees everything, as before.
    assert len(c.get(f"/readings/{rid}/review", headers=J2).json()["shown"]) == 3


def test_a_rewrite_keeps_its_tags_and_a_refusal_comes_in_plain_words(guided):
    _, c, rid = guided
    v = c.get(f"/readings/{rid}/review", headers=J1).json()
    u = next(x for x in v["units"] if x["target"] == "paragraph:career:0")
    assert "[" not in u["plain"] and u["facts"] and any("Budhaditya" in f for f in u["facts"])
    assert not any(ENGINE_WORDS.search(f) for x in v["units"] for f in x["facts"])
    edit = lambda text: c.post(f"/readings/{rid}/review/edit", headers=J1,
                               json={"target": u["target"], "text": text, "keep_tags": True}).json()
    r = edit("The Sun and Mercury join in the 10th, a strong pairing forming Budhaditya yoga and a raja yoga.")
    assert not r["accepted"] and {"code": "tier", "detail": "strong"} in r["reasons"]
    r = edit("The Sun and Mercury join in the 10th.")
    assert not r["accepted"] and {x["code"] for x in r["reasons"]} == {"name"}
    r = edit("REJECTED: the Sun and Mercury form Budhaditya yoga and a raja yoga in the 10th.")
    assert not r["accepted"] and r["reasons"] == [{"code": "unsupported", "detail": "REJECTED"}]
    r = edit("The Sun and Mercury join in the 10th, forming Budhaditya yoga and a raja yoga.")
    assert r["accepted"] and r["reasons"] == []
    para = next(a for a in r["review"]["reading"]["areas"] if a["name"] == "career")["paragraph"]
    assert para.startswith("The Sun and Mercury join in the 10th, forming Budhaditya yoga and a raja yoga "
                           "[rule:yoga.budhaditya] [rule:yoga.kendra_trikona_raja].")
    assert r["review"]["history"][-1]["area"] == "career"


def test_plain_reasons_and_tags():
    from jyotish.review import plain, plain_reasons, with_tags
    assert plain_reasons(["timing language ('years') in 'x'", "untagged claim: 'x'", "untagged claim: 'y'"]) == \
        [{"code": "timing", "detail": "years"}, {"code": "other", "detail": ""}]
    assert with_tags("A sits there [rule:a.b] [vote:c.d].", "A sits here!") == "A sits here [rule:a.b] [vote:c.d]!"
    assert with_tags("A sits there [rule:a.b].", "A [rule:x.y].") == "A [rule:x.y]."
    assert with_tags("No tags.", "Mine") == "Mine"
    assert plain("A sits there [rule:a.b] [vote:c.d].") == "A sits there."


def test_the_chart_drawing_takes_a_choice_of_vargas(guided):
    _, c, rid = guided
    cid = c.get(f"/readings/{rid}").json()["chart_id"]
    svg = c.get(f"/charts/{cid}/chart.svg?vargas=D1,D9").text
    assert 'data-varga="D1"' in svg and 'data-varga="D9"' in svg and 'data-varga="D10"' not in svg
    assert c.get(f"/charts/{cid}/chart.svg?vargas=D60").status_code == 422
    assert 'data-varga="D10"' in c.get(f"/charts/{cid}/chart.svg").text


# --- comments in the reviewer's own words, and the reading as a whole ------------------------

def test_a_comment_is_stored_in_the_answer_row_and_never_reaches_the_client(guided):
    app, c, rid = guided
    before = c.get(f"/readings/{rid}").json()
    post = lambda body: c.post(f"/readings/{rid}/review/answer", headers=J1, json=body)
    v = post({"step": "match", "area": "career", "answer": "partly",
              "comment": "  The 10th lord's weakness is the story here.  "}).json()
    assert v["answers"][-1]["comment"] == "The 10th lord's weakness is the story here."
    assert post({"step": "period", "area": "career", "answer": {"choice": "yes"}, "comment": ""}).json()["answers"][-1]["comment"] is None
    with app.state.Session() as s:
        row = s.query(ReviewRow).filter_by(reading_id=rid, step="match").one()
        assert (row.comment, row.answer, row.verdict) == ("The 10th lord's weakness is the story here.", "partly", "partly")
    hist = c.get(f"/readings/{rid}/review", headers=J1).json()["history"]
    assert any(h["comment"] == "The 10th lord's weakness is the story here." for h in hist)
    after = c.get(f"/readings/{rid}").json()
    assert after["reading"] == before["reading"] and after["page"] == before["page"]           # not shown, not checked
    assert "story here" not in json.dumps(after)
    assert post({"step": "match", "area": "career", "answer": "agree", "comment": 12}).status_code == 422
    assert post({"step": "match", "area": "career", "answer": "agree", "comment": "x" * 4001}).status_code == 422


def test_the_reading_as_a_whole(guided):
    app, c, rid = guided
    post = lambda body, mode="review", tok=J1: c.post(f"/readings/{rid}/review/answer", headers=tok, json=dict(body, mode=mode))
    r = post({"step": "whole", "answer": {"text": "Balanced; the timing reads early."}, "comment": "seen in practice"})
    assert r.status_code == 200
    last = r.json()["answers"][-1]
    assert (last["step"], last["area"], last["answer"], last["comment"]) == \
        ("whole", None, {"text": "Balanced; the timing reads early."}, "seen in practice")
    assert post({"step": "whole", "area": "career", "answer": {"text": "x"}}).status_code == 422     # no area
    assert post({"step": "whole", "answer": "fine"}).status_code == 422                              # {text}
    # Blind: the whole reading is asked only once every area has been shown.
    assert post({"step": "whole", "answer": {"text": "x"}}, mode="blind", tok=J2).status_code == 409
    assert "Balanced" not in json.dumps(c.get(f"/readings/{rid}").json())
