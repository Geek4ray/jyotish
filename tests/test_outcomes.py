"""Outcome capture (SPEC Layer 6, outcome dataset; outcomes.py): the vocabulary and outcome map,
rule testability, the clerk's sheet over the CLI and POST /outcomes with every refusal, the after
flag, and erasure. The template's subject is fictional."""

import subprocess
import time
from datetime import date
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from jyotish import outcomes as oc
from jyotish.api import ChartRow, ConsentRow, ErasureRow, EventRow, ReadingRow, ReviewRow, SubjectRow, create_app

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "docs" / "intake_template.csv"
TODAY = date(2026, 10, 22)


def test_the_map_covers_the_areas_and_the_rules():
    from jyotish.rules import load_rules
    from jyotish.scoring import AREAS
    m = oc.outcome_map()
    assert set(m["areas"]) == set(AREAS) - {"synastry"} and len(m["areas"]) == 18
    used = {o for r in load_rules() for o in r.data.get("outcomes", [])}
    assert used <= set(m["rule_outcomes"])                                  # every rule outcome is mapped
    assert set(oc.EVENT_TYPES) == {"first_marriage", "divorce", "first_child", "occupation", "tenure_change",
                                   "first_relocation_abroad", "major_surgery", "chronic_diagnosis", "parental_loss",
                                   "property_purchase"}
    assert oc.area_events("career") == ["occupation", "tenure_change"] and oc.area_events("personality") == []


def test_a_rule_whose_outcomes_map_to_nothing_is_not_testable_yet():
    t = oc.rule_testability()
    assert t["place.moon_in_libra"]["status"] == "not_testable_yet"         # temperament_profile: not measured
    assert t["yoga.ruchaka"]["status"] == "testable" and "occupation" in t["yoga.ruchaka"]["events"]
    assert all(v["unmapped_outcomes"] == [] for v in t.values())
    assert sum(v["status"] == "not_testable_yet" for v in t.values()) > 0


@pytest.fixture()
def Session(tmp_path):
    return oc.sessionmaker_for(f"sqlite:///{tmp_path / 'o.db'}")


def _rows():
    return oc.read_sheet(TEMPLATE)


def test_the_template_imports(Session):
    with Session.begin() as s:
        oc.add_consent(s, "C-0001", "S-0001", "v1", "backlog", "clerk-1")
        res = oc.import_rows(s, _rows(), entered_by="clerk-1", today=TODAY)
    assert (res.accepted, res.subjects_created, res.refused) == (4, 1, [])
    with Session() as s:
        subj = s.get(SubjectRow, "S-0001")
        assert subj.accuracy == "exact" and subj.source == "file" and len(subj.chart_id) == 64
        ev = {e.event_type: e for e in s.query(EventRow)}
        assert ev["first_marriage"].age_at_event == 27.5 and ev["first_marriage"].censor_age == 41
        assert ev["first_relocation_abroad"].age_at_event is None              # censored: not by 41
        assert ev["occupation"].value == {"isco08": "2211", "isei": 78.0}
        assert all(not e.after and e.before_reading is not None for e in ev.values())


@pytest.mark.parametrize("change,reason", [
    ({"age_at_event": "45"}, "exceeds the censor age"),
    ({"age_at_event": "-1"}, "precedes birth"),
    ({"consent_id": "C-9999"}, "no consent"),
    ({"subject_id": "S-0002"}, "belongs to another subject"),
    ({"rectified": "yes"}, "rectified"),
    ({"censor_age": "60"}, "beyond the subject's age today"),
    ({"event_type": "promotion"}, "not in the vocabulary"),
    ({"event_type": "occupation", "isco08": "", "isei": ""}, "ISCO-08"),
    ({"accuracy": "roughly"}, "accuracy class"),
    ({"censor_age": ""}, "no censor age"),
])
def test_a_bad_row_is_refused_with_its_reason(Session, change, reason):
    with Session.begin() as s:
        oc.add_consent(s, "C-0001", "S-0001", "v1", "backlog", "clerk-1")
        row = dict(_rows()[0], **change)
        res = oc.import_rows(s, [row], entered_by="clerk-1", today=TODAY)
    assert res.accepted == 0 and any(reason in r for r in res.refused[0]["reasons"]), res.refused
    with Session() as s:
        assert s.query(EventRow).count() == 0


def test_a_withdrawn_consent_refuses_and_an_event_after_a_reading_is_flagged(Session):
    with Session.begin() as s:
        oc.add_consent(s, "C-0001", "S-0001", "v1", "backlog", "clerk-1")
        row = dict(_rows()[0], reading_shown_at="2026-10-01T09:00:00+05:30")
        res = oc.import_rows(s, [row], entered_by="clerk-1", today=TODAY)
        assert res.accepted == 1
        oc.withdraw_consent(s, "C-0001")
        res = oc.import_rows(s, [_rows()[1]], entered_by="clerk-1", today=TODAY)
    assert res.accepted == 0 and "withdrawn" in res.refused[0]["reasons"][0]
    with Session() as s:
        e = s.query(EventRow).one()
        assert e.after is True and e.before_reading is None                   # excluded from every test


def test_post_outcomes_and_erasure(tmp_path):
    url = f"sqlite:///{tmp_path / 'api.db'}"
    app = create_app(url, model_fixture=str(ROOT / "tests" / "fixtures" / "narration_curious.json"),
                     reviewers={"tok-1": "judge-1"}, clerks={"clerk-tok": "clerk-1"},
                     review_checker=lambda s, d: None)
    Session = app.state.Session
    rows = _rows()
    with TestClient(app) as c:
        assert c.post("/outcomes", json={"rows": rows}).status_code == 401
        with Session.begin() as s:
            oc.add_consent(s, "C-0001", "S-0001", "v1", "new", "clerk-1")
        bad = dict(rows[0], age_at_event="50")
        r = c.post("/outcomes", headers={"Authorization": "Bearer clerk-tok"}, json={"rows": rows + [bad]}).json()
        assert r["accepted"] == 4 and len(r["refused"]) == 1 and r["refused"][0]["row"] == 5
        # A reading for the same birth data shares the subject's chart.
        b = rows[0]
        body = {"date": b["date"], "time": b["time"], "tz": b["tz"], "lat": float(b["lat"]), "lon": float(b["lon"]),
                "node": "mean", "question": "How will my career go?", "depth": "curious", "as_of": "2026-10-21"}
        rid = c.post("/readings", json=body).json()["id"]
        for _ in range(600):
            if c.get(f"/readings/{rid}").json()["status"] in ("done", "failed"):
                break
            time.sleep(0.05)
        c.get(f"/readings/{rid}/review", headers={"Authorization": "Bearer tok-1"})
    with Session() as s:
        subj = s.get(SubjectRow, "S-0001")
        assert s.query(ReadingRow).filter_by(chart_id=subj.chart_id).count() == 1
        assert s.get(ChartRow, subj.chart_id) is not None
    with Session.begin() as s:
        counts = oc.erase(s, "S-0001", "dpo-1")
    assert counts == {"reviews": 1, "readings": 1, "exclusions": 1, "charts": 1, "events": 4, "consents": 1,
                      "subjects": 1}
    with Session() as s:
        assert s.get(SubjectRow, "S-0001") is None and s.query(EventRow).count() == 0
        assert s.query(ReadingRow).count() == 0 and s.query(ReviewRow).count() == 0 and s.query(ConsentRow).count() == 0
        log = s.query(ErasureRow).one()
        assert (log.subject_id, log.erased_by, log.counts["events"]) == ("S-0001", "dpo-1", 4)
        assert "1984" not in str(log.counts)                                  # the log holds no birth data


def test_the_commands(tmp_path):
    db = f"sqlite:///{tmp_path / 'cli.db'}"
    jy = str(ROOT / ".venv" / "bin" / "jyotish")
    run = lambda *a: subprocess.run([jy, *a], capture_output=True, text=True)
    assert run("outcomes", "consent", "C-0001", "--subject", "S-0001", "--form", "v1", "--track", "backlog",
               "--by", "clerk-1", "--database", db).returncode == 0
    out = run("outcomes", "import", str(TEMPLATE), "--entered-by", "clerk-1", "--database", db)
    assert out.returncode == 0 and "4 event rows stored (1 new subjects); 0 refused" in out.stdout
    st = run("outcomes", "status")
    assert st.returncode == 0 and "not_testable_yet" in st.stdout
    er = run("subject", "erase", "S-0001", "--by", "dpo-1", "--database", db)
    assert er.returncode == 0 and "4 events" in er.stdout and "(logged)" in er.stdout
