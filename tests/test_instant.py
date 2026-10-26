"""The instant first page (2026-10-26): every engine field of the reading before any model call,
stored as "narration pending", rendered at once by the page and the site, opened by the review step."""

import threading
import time
from datetime import date
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from jyotish import service
from jyotish.api import create_app
from jyotish.narrate import Reading, instant_reading
from jyotish.page import PENDING, PENDING_NOTICE, render
from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
from jyotish.uncertainty import assess

FIXTURES = Path(__file__).parent / "fixtures"
EDITED = str(FIXTURES / "narration_career_edited.json")
QUESTION = "How will my career go, and when is the best time for a job change?"
BODY = {"date": "2001-03-12", "time": "10:10:25", "tz": "Asia/Kolkata", "lat": REFERENCE_LAT, "lon": REFERENCE_LON,
        "node": "mean", "place": "Rewari, Haryana", "question": QUESTION, "as_of": "2026-10-21",
        "depth": "astrologer"}
AUTH = {"Authorization": "Bearer test-token-1"}
AREAS = ["career", "marriage", "longevity"]


@pytest.fixture(scope="module")
def chart():
    return assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)


@pytest.fixture(scope="module")
def first(chart):
    return instant_reading(chart, QUESTION, as_of=date(2026, 10, 21), areas=AREAS)


def test_the_instant_reading_has_every_engine_field_and_no_model_text(first):
    assert first.narration_status == "pending" and first.attempts == 0 and not first.narration_complete
    assert [a.name for a in first.areas] == AREAS
    assert first.summary.source == "engine" and first.summary.text
    assert first.summary.timing_line.startswith("Best window for career")
    career = first.areas[0]
    assert career.tier and career.windows and career.score_classical is not None
    assert not career.claims and not career.narration_gaps and not career.paragraph
    assert first.writer == {} and first.checker == {} and first.usage == {}


def test_engine_lines_are_the_engine_s_own_wording(first):
    lines = first.areas[0].engine_lines
    assert "The house vote is for career." in lines
    assert any("lord of the 2nd, is in the 10th (a draft placement, weighing nothing yet)" in x for x in lines)
    assert all(x.endswith(".") for x in lines if x)


def test_the_page_marks_every_area_pending_and_reports_no_gaps(first, chart):
    page = render(first, chart)
    assert PENDING_NOTICE in page and page.count(f"*{PENDING}*") == len(AREAS)
    assert "Narration incomplete" not in page and "No claims were drafted" not in page
    assert "- The house vote is for career." in page


@pytest.fixture
def held(tmp_path, monkeypatch):
    """A reading held between its instant page and its narration until the test lets it go."""
    gate, stored = threading.Event(), threading.Event()
    real = service.make_reading

    def make(*a, on_instant=None, **k):
        def instant(r, p):
            on_instant(r, p)
            stored.set()
            gate.wait(60)
        return real(*a, on_instant=instant, **k)
    monkeypatch.setattr(service, "make_reading", make)
    app = create_app(f"sqlite:///{tmp_path / 'i.db'}", model_fixture=EDITED, reviewers={"test-token-1": "judge-1"})
    with TestClient(app) as c:
        rid = c.post("/readings", json=BODY).json()["id"]
        assert stored.wait(60)
        yield c, rid, gate
        gate.set()


def test_post_stores_the_instant_page_while_the_narration_runs(held):
    c, rid, gate = held
    s = c.get(f"/readings/{rid}").json()
    assert s["status"] == "running" and s["progress"]["stage"] == "narration"
    assert s["progress"]["log"][-1] == "instant"
    r = Reading(**s["reading"])
    assert r.narration_status == "pending" and [a.name for a in r.areas] == AREAS
    assert all(a.sheet for a in r.areas)                       # the technical sheet is in the instant page
    assert PENDING_NOTICE in s["page"]
    gate.set()
    for _ in range(600):
        s = c.get(f"/readings/{rid}").json()
        if s["status"] == "done":
            break
        time.sleep(0.05)
    r = Reading(**s["reading"])
    assert r.narration_status == "done" and r.areas[0].claims and PENDING_NOTICE not in s["page"]
    assert 0 < r.usage["timeline"]["instant_s"] < 30


def test_the_review_step_opens_a_pending_reading(held):
    c, rid, _ = held
    r = c.get(f"/readings/{rid}/review", headers=AUTH)
    assert r.status_code == 200, r.text
    view = r.json()
    assert view["reading"]["narration_status"] == "pending"
    assert all(not a["claims"] for a in view["reading"]["areas"])        # only what passed: nothing yet
