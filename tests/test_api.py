"""The reading service (jyotish.api), offline: the model is replayed from the hand-edited
fixture, the database is a temporary SQLite file."""

import json
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from jyotish.api import Base, ChartRow, ReadingRow, create_app
from jyotish.narrate import Reading
from jyotish.reference import REFERENCE_LAT, REFERENCE_LON

FIXTURES = Path(__file__).parent / "fixtures"
EDITED = str(FIXTURES / "narration_career_edited.json")
QUESTION = "How will my career go, and when is the best time for a job change?"
BODY = {"date": "2001-03-12", "time": "10:10:25", "tz": "Asia/Kolkata", "lat": REFERENCE_LAT, "lon": REFERENCE_LON,
        "node": "mean", "place": "Rewari, Haryana", "question": QUESTION, "as_of": "2026-10-21"}


def wait(client, reading_id, timeout=90):
    t = time.monotonic()
    while time.monotonic() - t < timeout:
        r = client.get(f"/readings/{reading_id}").json()
        if r["status"] in ("done", "failed"):
            return r
        time.sleep(0.05)
    raise AssertionError(f"reading {reading_id} still {r['status']} after {timeout} s")


@pytest.fixture(scope="module")
def app(tmp_path_factory):
    db = tmp_path_factory.mktemp("api") / "jyotish.db"
    return create_app(f"sqlite:///{db}", model_fixture=EDITED)


@pytest.fixture(scope="module")
def client(app):
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def done(client):
    r = client.post("/readings", json=BODY)
    assert r.status_code == 202 and r.json()["status"] == "queued"
    rid = r.json()["id"]
    assert r.json()["url"] == f"/readings/{rid}"
    return wait(client, rid)


def test_post_then_get_returns_the_reading_and_page(done):
    assert done["status"] == "done", done.get("error")
    reading = Reading(**done["reading"])
    assert [a.name for a in reading.areas] == ["career", "marriage", "longevity"]
    assert reading.summary.timing_line.startswith("Best window for career")
    assert done["page"].startswith(f"# Reading: {QUESTION}") and "**When (engine):**" in done["page"]
    assert reading.chart["command"].startswith("jyotish read --date 2001-03-12")


def test_progress_runs_chart_score_draft_check_done(done):
    assert done["progress"]["stage"] == "done" and done["progress"]["attempts"] == 1
    assert done["progress"]["log"] == ["chart", "score", "draft 1", "check 1", "done"]


def test_same_reading_as_the_cli(done, tmp_path):
    from jyotish.cli import main
    out = tmp_path / "cli"
    args = ["read", "--date", BODY["date"], "--time", BODY["time"], "--tz", BODY["tz"], "--lat", str(BODY["lat"]),
            "--lon", str(BODY["lon"]), "--node", "mean", "--place", BODY["place"], "--question", QUESTION,
            "--as-of", BODY["as_of"], "--out", str(out), "--model-fixture", EDITED]
    with pytest.raises(SystemExit) as e:
        main(args)
    assert e.value.code == 0
    assert Reading(**done["reading"]) == Reading(**json.loads(out.with_suffix(".json").read_text()))
    assert done["page"] == out.with_suffix(".md").read_text()


def test_chart_and_reading_are_stored_as_documents(app, done):
    with app.state.Session() as s:
        chart = s.get(ChartRow, done["chart_id"])
        row = s.get(ReadingRow, done["id"])
        assert chart.document["scored"]["areas"]["career"]["tier"] == "moderate"
        assert chart.birth["lat"] == REFERENCE_LAT and len(chart.id) == 64
        assert row.document["summary"]["timing_line"] == done["reading"]["summary"]["timing_line"]
        assert row.page == done["page"] and row.chart_id == chart.id


def test_second_question_on_the_same_chart_uses_the_cache(client, done):
    r = client.post("/readings", json=dict(BODY, question="How will my career go?"))
    second = wait(client, r.json()["id"])
    assert second["status"] == "done" and second["chart_id"] == done["chart_id"]
    assert second["reading"]["summary"].get("timing_line") is None          # not a "when" question


def test_failure_is_reported_with_the_validator_errors(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'f.db'}", model_fixture=str(FIXTURES / "narration_career_opus55_r1.json"))
    with TestClient(app) as c:
        r = wait(c, c.post("/readings", json=BODY).json()["id"])
    assert r["status"] == "failed" and "reading" not in r and "page" not in r
    assert r["progress"]["log"] == ["chart", "score", "draft 1", "draft 2", "draft 3", "failed"]
    assert any("unknown finding id 'yoga.ruchaka@lagna'" in e for e in r["error"]["errors"])


def test_requests_carry_no_key_and_unknown_ids_are_404(client):
    r = client.post("/readings", json=dict(BODY, api_key="sk-ant-test"))
    assert r.status_code == 422                                   # unknown fields refused
    assert "sk-ant-test" not in r.text                            # and never echoed back
    assert r.json()["detail"][0]["loc"] == ["body", "api_key"]
    assert client.post("/readings", json={k: v for k, v in BODY.items() if k != "lat"}).status_code == 422
    assert client.get("/readings/nope").status_code == 404


def test_document_columns_are_jsonb_under_postgres():
    from sqlalchemy.dialects import postgresql, sqlite
    from sqlalchemy.schema import CreateTable
    pg = str(CreateTable(ReadingRow.__table__).compile(dialect=postgresql.dialect()))
    assert pg.count("JSONB") == 4                                 # request, progress, document, error
    assert "JSONB" in str(CreateTable(ChartRow.__table__).compile(dialect=postgresql.dialect()))
    assert "JSON" in str(CreateTable(ChartRow.__table__).compile(dialect=sqlite.dialect()))
    assert set(Base.metadata.tables) == {"charts", "readings"}
