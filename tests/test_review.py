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
