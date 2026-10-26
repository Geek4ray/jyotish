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
        "node": "mean", "place": "Rewari, Haryana", "question": QUESTION, "as_of": "2026-10-21",
        "depth": "astrologer"}             # the fixtures are astrologer drafts; curious is tested on its own


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
    assert done["progress"]["log"] == ["chart", "score", "instant", "draft 1", "check 1", "done"]


def test_same_reading_as_the_cli(done, tmp_path):
    from jyotish.cli import main
    out = tmp_path / "cli"
    args = ["read", "--date", BODY["date"], "--time", BODY["time"], "--tz", BODY["tz"], "--lat", str(BODY["lat"]),
            "--lon", str(BODY["lon"]), "--node", "mean", "--place", BODY["place"], "--question", QUESTION,
            "--as-of", BODY["as_of"], "--depth", BODY["depth"], "--out", str(out), "--model-fixture", EDITED]
    with pytest.raises(SystemExit) as e:
        main(args)
    assert e.value.code == 0
    api, cli = Reading(**done["reading"]), Reading(**json.loads(out.with_suffix(".json").read_text()))
    # `usage` holds measured seconds, which no two runs share; its call counts are the same.
    assert api.model_dump(exclude={"usage"}) == cli.model_dump(exclude={"usage"})
    assert [api.usage[k]["calls"] for k in ("writer", "checker")] == [cli.usage[k]["calls"] for k in ("writer", "checker")]
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


def test_narration_that_never_passes_is_done_with_gaps(tmp_path):
    # The frozen first recording fails the validator on every attempt: the job is done, not
    # failed, with the engine's summary and the findings it could not narrate listed.
    app = create_app(f"sqlite:///{tmp_path / 'f.db'}", model_fixture=str(FIXTURES / "narration_career_opus55_r1.json"))
    with TestClient(app) as c:
        r = wait(c, c.post("/readings", json=BODY).json()["id"])
    assert r["status"] == "done" and r["progress"]["narration_complete"] is False
    assert r["progress"]["log"] == ["chart", "score", "instant", "draft 1", "draft 2", "draft 3", "check 3", "done"]
    reading = Reading(**r["reading"])
    assert reading.summary.source == "engine" and not reading.narration_complete
    gaps = {g["finding_id"]: g for a in reading.areas for g in a.narration_gaps}
    assert "yoga.ruchaka@lagna+sun" in gaps and "could not be written within the checks." in r["page"]
    assert gaps["yoga.ruchaka@lagna+sun"]["last_error"] not in r["page"]          # the error is the JSON's


def test_progress_shows_the_chart_line_and_a_failed_job_keeps_the_header(client, done, tmp_path):
    # After the chart step the lagna, the Moon's sign and nakshatra and the UTC moment are in
    # the progress, so a wrong timezone shows at once.
    c = done["progress"]["chart"]
    assert (c["lagna"], c["moon_sign"], c["moon_nakshatra"], c["birth_utc"]) == \
        ("Taurus", "Libra", "Chitra", "2001-03-12T04:40:25+00:00")
    # A job that fails after the chart (here: a fixture that does not exist) keeps both.
    app = create_app(f"sqlite:///{tmp_path / 'g.db'}", model_fixture=str(tmp_path / "missing.json"))
    with TestClient(app) as c:
        r = wait(c, c.post("/readings", json=BODY).json()["id"])
    assert r["status"] == "failed" and r["progress"]["log"][-1] == "failed"
    assert r["progress"]["chart"]["lagna"] == "Taurus"
    assert r["progress"]["header"]["local_time"] == "10:10:25" and r["progress"]["header"]["place"] == "Rewari, Haryana"
    assert r["progress"]["header"]["command"].startswith("jyotish read --date 2001-03-12")


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
    assert set(Base.metadata.tables) == {"charts", "readings", "reviews", "exclusions", "consents", "subjects", "events",
                                         "erasures", "comparisons", "credentials", "ledger"}


def test_places_endpoint(client):
    r = client.get("/places", params={"q": "rewari"}).json()
    assert r[0]["label"] == "Rewāri, Haryana, India" and r[0]["timezone"] == "Asia/Kolkata"
    assert len(client.get("/places", params={"q": "san", "limit": 500}).json()) == 20    # capped
    assert client.get("/places", params={"q": "x"}).json() == []


@pytest.mark.parametrize("change,where", [({"lat": 0, "lon": 0}, ["body"]), ({"lat": 91}, ["body", "lat"]),
                                          ({"lon": -181}, ["body", "lon"])])
def test_null_island_and_out_of_range_are_refused(client, change, where):
    r = client.post("/readings", json=dict(BODY, **change))
    assert r.status_code == 422
    assert r.json()["detail"][0]["loc"] == where
    if change.get("lat") == 0:
        assert "Gulf of Guinea" in r.json()["detail"][0]["msg"]


def test_check_line_names_the_place_and_coordinates_in_words(done):
    c = done["progress"]["chart"]
    assert c["words"] == ("Rewari, Haryana, at 28.1989° N, 76.6170° E (timezone Asia/Kolkata). Born 2001-03-12 at "
                          "10:10:25 local time, 04:40:25 UTC. Ascendant (lagna) Taurus; Moon in Libra, Chitra nakshatra.")
    assert (c["place"], c["lat"], c["lon"], c["tz"], c["node"]) == ("Rewari, Haryana", REFERENCE_LAT, REFERENCE_LON,
                                                                    "Asia/Kolkata", "mean")


def test_depth_defaults_to_curious_and_is_checked(client):
    from jyotish.api import ReadingRequest
    body = {k: v for k, v in BODY.items() if k != "depth"}
    assert ReadingRequest(**body).depth == "curious"
    r = client.post("/readings", json=dict(BODY, depth="expert"))
    assert r.status_code == 422 and r.json()["detail"][0]["loc"] == ["body", "depth"]


def test_health_reports_the_engine_and_the_database_and_never_the_url(client, app):
    from jyotish.cache import engine_hash
    from jyotish.db import head_revision
    r = client.get("/health")
    assert r.status_code == 200
    h = r.json()
    assert h["status"] == "ok" and h["engine"] == {"version": "0.1.0", "hash": engine_hash()}
    assert h["database"] == {"dialect": "sqlite", "ok": True, "revision": head_revision(), "head": head_revision()}
    assert h["narration"] == "fixture"                     # this app replays a recording
    assert "sqlite:///" not in r.text and ".db" not in r.text


def test_health_is_503_when_the_database_cannot_be_reached(tmp_path):
    from sqlalchemy import text
    app = create_app(f"sqlite:///{tmp_path / 'h.db'}", model_fixture=EDITED)
    with TestClient(app) as c:
        app.state.engine.dispose()
        with app.state.engine.begin() as conn:
            conn.execute(text("DROP TABLE alembic_version"))
            conn.execute(text("CREATE TABLE alembic_version (x INTEGER)"))   # a broken revision table
        r = c.get("/health")
    assert r.status_code == 503 and r.json()["database"]["ok"] is False and r.json()["status"] == "degraded"


def test_source_redirects_to_the_configured_url(client, monkeypatch):
    assert client.get("/source", follow_redirects=False).status_code == 404
    monkeypatch.setenv("JYOTISH_SOURCE_URL", "https://example.org/jyotish")
    r = client.get("/source", follow_redirects=False)
    assert r.status_code in (302, 307) and r.headers["location"] == "https://example.org/jyotish"


def test_a_reading_stored_before_the_sheet_gets_it_when_read(app, client, done):
    # A reading made before the technical sheet (2026-10-25) has none stored; GET gives every area one,
    # made from its chart, without writing it back.
    assert all(a["sheet"] for a in done["reading"]["areas"])
    with app.state.Session.begin() as s:
        row = s.get(ReadingRow, done["id"])
        row.document = dict(row.document, areas=[{k: v for k, v in a.items() if k != "sheet"} for a in row.document["areas"]])
    r = client.get(f"/readings/{done['id']}").json()
    assert [a["sheet"]["points"][0]["title"] for a in r["reading"]["areas"]] == ["Houses (bhava)"] * 3
    with app.state.Session() as s:
        assert all("sheet" not in a for a in s.get(ReadingRow, done["id"]).document["areas"])
