"""The service as deployed (docs/deploy.md): tokens in the credentials table (`jyotish reviewer add`,
hashes only, revocable), the old environment variables as a logged local fallback, the rate limit on
POST /readings, the per-reading cost ledger and the owner's daily totals, and logs with no birth data."""

import json
import logging
import subprocess
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from jyotish.api import create_app
from jyotish.db import CredentialRow, LedgerRow, ReadingRow, migrate
from jyotish.reference import REFERENCE_LAT, REFERENCE_LON

ROOT = Path(__file__).resolve().parents[1]
EDITED = str(ROOT / "tests" / "fixtures" / "narration_career_edited.json")
QUESTION = "How will my career go, and when is the best time for a job change?"
BODY = {"date": "2001-03-12", "time": "10:10:25", "tz": "Asia/Kolkata", "lat": REFERENCE_LAT, "lon": REFERENCE_LON,
        "node": "mean", "place": "Rewari, Haryana", "question": QUESTION, "as_of": "2026-10-21", "depth": "astrologer"}
JY = str(ROOT / ".venv" / "bin" / "jyotish")


class Collect(logging.Handler):
    """The service's log lines as the JSON objects they are written as."""

    def __init__(self):
        super().__init__()
        from jyotish.logs import JsonLines
        self.setFormatter(JsonLines())
        self.lines: list[dict] = []

    def emit(self, record):
        self.lines.append(json.loads(self.format(record)))


@pytest.fixture
def logged():
    h = Collect()
    logging.getLogger("jyotish").addHandler(h)
    yield h.lines
    logging.getLogger("jyotish").removeHandler(h)


def wait(client, rid, headers=None):
    for _ in range(900):
        r = client.get(f"/readings/{rid}", headers=headers or {}).json()
        if r["status"] in ("done", "failed"):
            return r
        time.sleep(0.1)
    raise AssertionError(rid)


def cli(*args):
    return subprocess.run([JY, *args], capture_output=True, text=True)


def test_a_token_is_printed_once_stored_as_a_hash_and_revocable(tmp_path):
    db = f"sqlite:///{tmp_path / 'c.db'}"
    out = cli("reviewer", "add", "judge-1", "--database", db)
    assert out.returncode == 0 and "shown once" in out.stdout
    token = out.stdout.strip().splitlines()[-1]
    assert len(token) >= 40
    with sessionmaker(migrate(db))() as s:
        row = s.query(CredentialRow).one()
        assert (row.kind, row.name, row.revoked_at) == ("reviewer", "judge-1", None) and token not in row.token_hash
    assert cli("reviewer", "add", "judge-1", "--database", db).returncode == 2          # one active token per name
    app = create_app(db, model_fixture=EDITED, reviewers={}, clerks={})
    with TestClient(app) as c:
        rid = c.post("/readings", json=BODY).json()["id"]
        assert wait(c, rid)["status"] == "done"
        ok = c.get(f"/readings/{rid}/review", headers={"Authorization": f"Bearer {token}"})
        assert ok.status_code == 200 and ok.json()["reviewer"] == "judge-1"           # acts under its name
        assert c.get(f"/readings/{rid}/review", headers={"Authorization": "Bearer nope"}).status_code == 401
        assert c.post("/outcomes", json={"rows": []}, headers={"Authorization": f"Bearer {token}"}).status_code == 401
        assert c.get("/costs/daily", headers={"Authorization": f"Bearer {token}"}).status_code == 401   # not the owner
        assert cli("reviewer", "revoke", "judge-1", "--database", db).returncode == 0
        assert c.get(f"/readings/{rid}/review", headers={"Authorization": f"Bearer {token}"}).status_code == 401
    listed = cli("reviewer", "list", "--database", db).stdout
    assert "judge-1\trevoked" in listed
    again = cli("reviewer", "add", "judge-1", "--database", db)
    assert again.returncode == 0 and again.stdout.strip().splitlines()[-1] != token


def test_a_clerks_token_enters_outcomes_under_its_name(tmp_path):
    db = f"sqlite:///{tmp_path / 'c.db'}"
    token = cli("clerk", "add", "clerk-1", "--database", db).stdout.strip().splitlines()[-1]
    app = create_app(db, model_fixture=EDITED, reviewers={}, clerks={})
    with TestClient(app) as c:
        r = c.post("/outcomes", json={"rows": []}, headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200 and r.json()["accepted"] == 0


def test_the_environment_variables_still_work_and_the_log_says_so(tmp_path, monkeypatch, logged):
    monkeypatch.setenv("JYOTISH_REVIEWERS", "judge-9:local-token")
    app = create_app(f"sqlite:///{tmp_path / 'e.db'}", model_fixture=EDITED)
    warn = [x for x in logged if x["event"] == "credentials.environment"]
    assert warn and warn[0]["variable"] == "JYOTISH_REVIEWERS" and warn[0]["names"] == ["judge-9"]
    assert "local-token" not in json.dumps(logged)
    with TestClient(app) as c:
        rid = c.post("/readings", json=BODY).json()["id"]
        assert wait(c, rid)["status"] == "done"
        assert c.get(f"/readings/{rid}/review", headers={"Authorization": "Bearer local-token"}).status_code == 200


def test_post_readings_is_rate_limited_per_client_and_per_day(tmp_path, logged):
    app = create_app(f"sqlite:///{tmp_path / 'r.db'}", model_fixture=EDITED, rate=(2, 3))
    with TestClient(app) as c:
        codes = [c.post("/readings", json=BODY).status_code for _ in range(3)]
        assert codes == [202, 202, 429]
        r = c.post("/readings", json=BODY)
        assert r.status_code == 429 and int(r.headers["Retry-After"]) > 0
    from jyotish.api import RateLimit
    lim = RateLimit(5, 3)
    assert [lim.check(x) for x in ("a", "b", "c")] == [None, None, None] and lim.check("d") is not None   # the day's cap
    assert any(x["event"] == "readings.rate_limited" for x in logged)


def test_the_ledger_and_the_owners_daily_totals(tmp_path):
    db = f"sqlite:///{tmp_path / 'l.db'}"
    owner = cli("owner", "add", "ray", "--database", db).stdout.strip().splitlines()[-1]
    app = create_app(db, model_fixture=EDITED, reviewers={}, clerks={})
    with TestClient(app) as c:
        assert c.get("/costs/daily").status_code == 401
        rid = c.post("/readings", json=BODY).json()["id"]
        assert wait(c, rid)["status"] == "done"
        days = c.get("/costs/daily", headers={"Authorization": f"Bearer {owner}"}).json()
        assert len(days) == 1 and days[0]["readings"] == 1 and days[0]["replayed"] == 1 and days[0]["cost_usd"] == 0
        rows = c.get(f"/costs/readings?day={days[0]['day']}", headers={"Authorization": f"Bearer {owner}"}).json()
        assert [r["reading_id"] for r in rows] == [rid] and rows[0]["writer_model"] == "claude-opus-5-5"


def test_a_reading_finished_before_the_ledger_gets_its_row_priced_from_its_usage(tmp_path):
    from jyotish.costs import cost
    engine = migrate(f"sqlite:///{tmp_path / 'b.db'}")
    usage = {"writer": {"calls": 1, "input_tokens": 1000, "output_tokens": 2000, "cache_read_input_tokens": 10_000,
                        "cache_creation_input_tokens": 0},
             "checker": {"calls": 3, "input_tokens": 3000, "output_tokens": 600}, "wall_seconds": 12.0}
    doc = {"writer": {"model": "claude-opus-5-5"}, "checker": {"model": "claude-opus-5-5"}, "usage": usage, "depth": "full"}
    with sessionmaker(engine).begin() as s:
        s.add(ReadingRow(id="r" * 32, question="q", request={}, status="done", progress={}, document=doc))
    migrate(engine)
    with sessionmaker(engine)() as s:
        row = s.get(LedgerRow, "r" * 32)
        want = cost("claude-opus-5-5", usage["writer"]) + cost("claude-opus-5-5", usage["checker"])
        assert row.cost_usd == pytest.approx(want) and row.cost_usd == pytest.approx(0.004 + 0.04 + 0.002 + 0.012 + 0.012)
        assert row.writer_calls == 1 and row.checker_calls == 3 and row.seconds == 12.0 and not row.replayed
    assert cost("a-model-without-a-price", usage["writer"]) is None


def test_the_logs_carry_no_birth_data(tmp_path, logged):
    app = create_app(f"sqlite:///{tmp_path / 'g.db'}", model_fixture=EDITED)
    with TestClient(app) as c:
        rid = c.post("/readings", json=BODY).json()["id"]
        done = wait(c, rid)
        c.get("/places?q=Rewari")
        c.get(f"/charts/{done['chart_id']}/tables.json")
    # The log lines' text without their own timestamp (it can read 10:10 by the clock: review R14) and without
    # numbers (a request's 28.19 ms matched the latitude 28.1989 as text, CI 2026-10-27); numbers are compared as
    # numbers below, so a coordinate logged as one is still caught.
    text = json.dumps([{k: v for k, v in x.items() if k != "ts" and not isinstance(v, (int, float))} for x in logged])
    numbers = [v for x in logged for v in x.values() if isinstance(v, float)]
    assert not [v for v in numbers for c in (REFERENCE_LAT, REFERENCE_LON) if abs(v - c) < 0.01], numbers
    events = {x["event"] for x in logged}
    assert {"http.request", "reading.queued", "reading.done"} <= events
    for secret in ("Rewari", "Haryana", "28.19", "76.61", "2001-03-12", "10:10", "Asia/Kolkata", "job change",
                   done["chart_id"], "q="):
        assert secret not in text, secret
    paths = {x["path"] for x in logged if x["event"] == "http.request"}
    assert "/charts/<chart>/tables.json" in paths and "/places" in paths
