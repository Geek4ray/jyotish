"""Depth full, part 4: the comparison. scripts/compare_readings.py offline (two recordings replayed,
no API call), and /compare/{a}/{b}: two readings shown blind as A and B, one question, the answer
logged to the judgements with the reviewer, the settings revealed only after it, in both roles."""

import json
import sys
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from jyotish.api import ReviewRow, compare_order, create_app
from jyotish.reference import REFERENCE_LAT, REFERENCE_LON

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
EDITED = str(FIXTURES / "narration_career_edited.json")
QUESTION = "How will my career go, and when is the best time for a job change?"
BODY = {"date": "2001-03-12", "time": "10:10:25", "tz": "Asia/Kolkata", "lat": REFERENCE_LAT, "lon": REFERENCE_LON,
        "node": "mean", "place": "Rewari, Haryana", "question": QUESTION, "as_of": "2026-10-21", "depth": "astrologer"}
JUDGES = {"tok-1": "judge-1", "tok-2": "judge-2", "tok-3": "judge-3", "tok-4": "judge-4"}
AUTH = lambda tok: {"Authorization": f"Bearer {tok}"}


def wait(client, rid):
    for _ in range(900):
        r = client.get(f"/readings/{rid}").json()
        if r["status"] in ("done", "failed"):
            return r
        time.sleep(0.1)
    raise AssertionError(f"reading {rid} still {r['status']}")


@pytest.fixture(scope="module")
def env(tmp_path_factory):
    db = tmp_path_factory.mktemp("compare") / "j.db"
    app = create_app(f"sqlite:///{db}", model_fixture=EDITED, reviewers=JUDGES)
    with TestClient(app) as client:
        a = client.post("/readings", json=dict(BODY, writer_effort="medium")).json()["id"]
        b = client.post("/readings", json=dict(BODY, writer_effort="max", writer_model="claude-fable-5-1")).json()["id"]
        other = client.post("/readings", json=dict(BODY, question="Will I marry?")).json()["id"]
        for rid in (a, b, other):
            assert wait(client, rid)["status"] == "done"
        yield client, app, a, b, other, db


def test_the_page_is_served_and_the_view_needs_a_reviewer(env):
    client, _, a, b, _, _ = env
    assert client.get(f"/compare/{a}/{b}").text.startswith("<!doctype html>")
    assert client.get(f"/compare/{a}/{b}/view").status_code == 401
    assert client.post(f"/compare/{a}/{b}/answer", json={"choice": "A", "why": "x"}).status_code == 401


def test_the_two_readings_are_blind_until_answered(env):
    client, _, a, b, _, _ = env
    v = client.get(f"/compare/{a}/{b}/view", headers=AUTH("tok-1")).json()
    assert set(v["readings"]) == {"A", "B"} and v["answer"] is None and "reveal" not in v
    text = json.dumps(v)
    for hidden in ("claude-fable-5-1", '"effort":', '"writer":', '"usage":', '"model":', "--writer", '"attempts":'):
        assert hidden not in text, hidden
    for r in v["readings"].values():
        assert r["question"] == QUESTION and r["areas"] and "command" not in r["chart"]


def test_an_answer_is_logged_and_reveals_the_settings(env):
    client, app, a, b, _, _ = env
    r = client.post(f"/compare/{a}/{b}/answer", headers=AUTH("tok-2"),
                    json={"choice": "B", "why": "B weighs the KP vote against the 10th lord, A does not."})
    assert r.status_code == 200
    v = r.json()
    shown_a, shown_b = compare_order(a, b, "judge-2")
    assert v["answer"]["choice"] == "B" and v["answer"]["reviewer"] == "judge-2"
    assert v["reveal"]["A"]["reading_id"] == shown_a and v["reveal"]["B"]["reading_id"] == shown_b
    effort = {a: "medium", b: "max"}
    assert v["reveal"]["A"]["effort"] == effort[shown_a] and v["reveal"]["B"]["effort"] == effort[shown_b]
    assert {v["reveal"][x]["model"] for x in "AB"} == {"claude-opus-5-5", "claude-fable-5-1"}
    with app.state.Session() as s:
        row = s.query(ReviewRow).filter_by(action="compare", reviewer_id="judge-2").one()
        assert row.answer["chosen"] == shown_b and row.answer["shown_as"] == {"A": shown_a, "B": shown_b}
        assert set(row.answer["settings"]) == {a, b} and row.comment.startswith("B weighs")
    again = client.post(f"/compare/{a}/{b}/answer", headers=AUTH("tok-2"), json={"choice": "A", "why": "changed"})
    assert again.status_code == 409                                  # the settings are seen: no second answer
    assert client.get(f"/compare/{b}/{a}/view", headers=AUTH("tok-2")).json()["answer"]["choice"] == "B"
    # Another reviewer's answer and the settings stay hidden from one who has not answered.
    assert client.get(f"/compare/{a}/{b}/view", headers=AUTH("tok-3")).json()["answer"] is None


def test_both_readings_take_both_roles(env):
    """Which reading is A is fixed per reviewer and pair, whatever the URL's order, and across
    reviewers each reading is shown as A and as B."""
    client, _, a, b, _, _ = env
    for tok, who in JUDGES.items():
        one = client.get(f"/compare/{a}/{b}/view", headers=AUTH(tok)).json()["readings"]
        two = client.get(f"/compare/{b}/{a}/view", headers=AUTH(tok)).json()["readings"]
        assert one == two
        assert compare_order(a, b, who) == compare_order(b, a, who)
    firsts = {compare_order(a, b, who)[0] for who in [f"judge-{i}" for i in range(1, 40)]}
    assert firsts == {a, b}


def test_only_two_readings_of_one_chart_and_question(env):
    client, _, a, _, other, _ = env
    assert client.get(f"/compare/{a}/{a}/view", headers=AUTH("tok-1")).status_code == 422
    assert client.get(f"/compare/{a}/{other}/view", headers=AUTH("tok-1")).status_code == 422
    assert client.post(f"/compare/{a}/{other}/answer", headers=AUTH("tok-1"),
                       json={"choice": "C", "why": "x"}).status_code == 422


def test_the_export_carries_the_comparison(env, tmp_path):
    from jyotish.export import export_reviews
    _, _, a, b, _, db = env
    export_reviews(f"sqlite:///{db}", tmp_path)
    rows = [json.loads(x) for x in (tmp_path / "judgements.jsonl").read_text().splitlines()[1:]]
    cmp = [r for r in rows if r.get("kind") == "compare"]
    assert len(cmp) == 1 and cmp[0]["reviewer"] == "judge-2" and cmp[0]["readings"] == sorted((a, b))
    assert cmp[0]["choice"] == "B" and cmp[0]["why"].startswith("B weighs") and set(cmp[0]["settings"]) == {a, b}


# --- the script --------------------------------------------------------------------------------

def test_compare_script_offline_writes_the_document(tmp_path):
    """Two recordings replayed (no API call): the table for each setting and the pages side by side."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import compare_readings as cr
    rec = json.loads(Path(EDITED).read_text())
    recs = []
    for key, s in (("a", {"model": "claude-opus-5-5", "effort": "medium", "depth": "astrologer"}),
                   ("b", {"model": "claude-opus-5-5", "effort": "high", "depth": "astrologer"})):
        p = tmp_path / f"{key}.json"
        p.write_text(json.dumps(dict(rec, settings=s, wall_seconds=12.5)))
        recs.append(str(p))
    out = tmp_path / "comparison.md"
    db = tmp_path / "c.db"
    assert cr.main(["--replay-a", recs[0], "--replay-b", recs[1], "--as-of", "2026-10-21", "--question", QUESTION,
                    "--out", str(out), "--database", f"sqlite:///{db}"]) == 0
    doc = out.read_text()
    assert doc.startswith("# Comparison of two readings") and "replayed from recordings (no API call)" in doc
    for row in ("Checked sentences shown", "Rejected claims", "Narration gaps", "Synthesis sentences",
                "Tradition sentences", "Writer tokens", "Cost, USD", "Narration wall time, s"):
        assert f"| {row}" in doc, row
    assert "| Writer | claude-opus-5-5, effort medium, thinking not sent | claude-opus-5-5, effort high" in doc
    assert "| Narration wall time, s | 12.5 | 12.5 |" in doc
    assert "<table>" in doc and "## The two pages side by side" in doc
    assert doc.count("<th colspan=\"2\">Career</th>") == 1           # one row per section, A beside B
    assert "/compare/" in doc                                          # both stored, the blind page named
    assert json.loads((tmp_path / "comparison" / "a.reading.json").read_text())["writer"]["effort"] == "medium"


def test_compare_script_refuses_an_unknown_setting():
    sys.path.insert(0, str(ROOT / "scripts"))
    import argparse
    import compare_readings as cr
    assert cr.setting("claude-opus-5-5, max, full") == {"model": "claude-opus-5-5", "effort": "max", "depth": "full"}
    for bad in ("claude-opus-5-5,max", "gpt-5,max,full", "claude-opus-5-5,maximum,full", "claude-opus-5-5,max,deep"):
        with pytest.raises(argparse.ArgumentTypeError):
            cr.setting(bad)


def test_cost_from_the_price_table():
    sys.path.insert(0, str(ROOT / "scripts"))
    import compare_readings as cr
    t = {"input_tokens": 1_000_000, "output_tokens": 100_000, "cache_read_input_tokens": 2_000_000,
         "cache_creation_input_tokens": 0}
    assert cr.cost("claude-opus-5-5", t) == pytest.approx(4.00 + 2.00 + 0.40)
    assert cr.cost("claude-unknown", t) is None
