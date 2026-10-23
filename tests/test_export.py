"""`jyotish export-reviews` (export.py): the review step's judgements as preference files, from a
review made through the API on a fresh database. Judgements, not outcomes; no birth data by default."""

import json
import subprocess
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from jyotish.api import create_app
from jyotish.narrate import CheckResult, Proposition

ROOT = Path(__file__).resolve().parents[1]
CURIOUS = str(ROOT / "tests" / "fixtures" / "narration_curious.json")
BODY = {"date": "2001-03-12", "time": "10:10:25", "tz": "Asia/Kolkata", "lat": 28.1989, "lon": 76.617, "node": "mean",
        "place": "Rewari, Haryana", "question": "How will my career go, and when is the best time for a job change?",
        "as_of": "2026-10-21", "depth": "curious"}
J1, J2 = {"Authorization": "Bearer tok-1"}, {"Authorization": "Bearer tok-2"}


def checker(sentence, data):
    ok = "REJECTED" not in sentence
    return CheckResult(propositions=[Proposition(text=sentence if ok else "REJECTED", supported=ok, evidence="stub")])


@pytest.fixture(scope="module")
def db(tmp_path_factory):
    path = tmp_path_factory.mktemp("export") / "e.db"
    app = create_app(f"sqlite:///{path}", model_fixture=CURIOUS, reviewers={"tok-1": "judge-1", "tok-2": "judge-2"},
                     review_checker=checker)
    with TestClient(app) as c:
        rid = c.post("/readings", json=BODY).json()["id"]
        for _ in range(600):
            if c.get(f"/readings/{rid}").json()["status"] in ("done", "failed"):
                break
            time.sleep(0.05)
        post = lambda body, tok=J1: c.post(f"/readings/{rid}/review/answer", headers=tok, json=body)
        post({"step": "intro", "answer": "done"})
        post({"step": "match", "area": "career", "answer": "agree"})
        post({"step": "match", "area": "career", "answer": "partly", "comment": "The 10th lord carries it."})
        post({"step": "off", "area": "career", "answer": {"reasons": ["timing"], "line": "too early"}})
        edit = lambda text: c.post(f"/readings/{rid}/review/edit", headers=J1,
                                   json={"target": "paragraph:career:0", "text": text, "keep_tags": True}).json()
        assert not edit("REJECTED: Budhaditya yoga and a raja yoga form in the 10th.")["accepted"]   # not exported
        assert edit("The Sun and Mercury join in the 10th, forming Budhaditya yoga and a raja yoga.")["accepted"]
        post({"step": "sentences", "area": "career", "answer": {"decisions": {"paragraph:career:0": "rewritten"}}})
        post({"step": "note", "area": "career", "answer": {"text": "Recognition comes late."}})
        post({"step": "period", "area": "career", "answer": {"choice": "later", "from": "2030-01", "to": "2031-06"},
              "comment": "Saturn's return."})
        post({"step": "whole", "answer": {"text": "Sound overall."}, "comment": "seen in practice"})
        blind = lambda body: post(dict(body, mode="blind"), J2)
        blind({"step": "blind_reading", "area": "marriage", "answer": "difficult", "comment": "the Upapada"})
        blind({"step": "match", "area": "marriage", "answer": "disagree"})
    return f"sqlite:///{path}", rid


def _read(path):
    lines = [json.loads(x) for x in Path(path).read_text().splitlines()]
    return lines[0], lines[1:]


def test_rewrites_one_row_per_accepted_rewrite(db, tmp_path):
    from jyotish.export import export_reviews
    url, rid = db
    n = export_reviews(url, tmp_path)
    head, rows = _read(tmp_path / "rewrites.jsonl")
    assert head["kind"] == "header" and "judgements, not outcomes" in head["note"] and head["with_birth_data"] is False
    assert n["rewrites"] == len(rows) == 1                                  # the refused edit is not a pair
    r = rows[0]
    assert (r["reading_id"], r["area"], r["step"], r["reviewer"]) == (rid, "career", "sentences", "judge-1")
    assert r["chart_hash"] and len(r["chart_hash"]) == 64 and r["at"]
    assert r["original_plain"].startswith("In your chart the Sun and Mercury")
    assert r["rewritten"].startswith("The Sun and Mercury join in the 10th, forming Budhaditya yoga and a raja yoga [rule:")
    assert r["rewritten_plain"] == "The Sun and Mercury join in the 10th, forming Budhaditya yoga and a raja yoga."
    assert any("Budhaditya yoga, formed by Sun and Mercury" in f for f in r["facts_shown"])
    assert r["facts_shown_source"] == "stored at review" and "birth" not in r
    # A row from before the facts were stored with the edit: recomputed with the engine of today, and said so.
    from sqlalchemy import create_engine, text
    with create_engine(url).begin() as conn:
        conn.execute(text("UPDATE reviews SET facts = NULL WHERE action = 'edit'"))
    export_reviews(url, tmp_path / "again")
    _, again = _read(tmp_path / "again" / "rewrites.jsonl")
    assert again[0]["facts_shown_source"] == "recomputed with the current engine" and again[0]["facts_shown"] == r["facts_shown"]


def test_judgements_one_row_per_area_answer(db, tmp_path):
    from jyotish.export import export_reviews
    url, rid = db
    export_reviews(url, tmp_path)
    head, rows = _read(tmp_path / "judgements.jsonl")
    assert "judgements, not outcomes" in head["note"]
    by = {(r["reviewer"], r["mode"], r["area"]): r for r in rows}
    career = by[("judge-1", "review", "career")]
    assert career["verdict"] == "partly"                                     # the latest answer, not the first
    assert career["what_is_off"] == ["timing"] and career["what_is_off_line"] == "too early"
    assert career["comments"] == {"match": "The 10th lord carries it.", "period": "Saturn's return."}
    assert career["best_period"] == {"choice": "later", "from": "2030-01", "to": "2031-06"}
    assert career["note"] == "Recognition comes late." and career["sentences"] == {"paragraph:career:0": "rewritten"}
    assert career["own_reading"] is None
    whole = by[("judge-1", "review", None)]
    assert whole["whole_reading"] == "Sound overall." and whole["comments"] == {"whole": "seen in practice"}
    blind = by[("judge-2", "blind", "marriage")]
    assert blind["own_reading"] == "difficult" and blind["verdict"] == "disagree" and blind["comments"]["blind_reading"] == "the Upapada"
    assert all("birth" not in r for r in rows)
    assert not any(r["area"] == "intro" for r in rows) and ("judge-1", "review", "intro") not in by


def test_birth_data_only_when_asked(db, tmp_path):
    from jyotish.export import export_reviews
    url, _ = db
    export_reviews(url, tmp_path, with_birth_data=True)
    head, rows = _read(tmp_path / "judgements.jsonl")
    assert head["with_birth_data"] is True
    assert all(r["birth"] and "lat" in json.dumps(r["birth"]) for r in rows)


def test_the_command_and_the_gitignore(db, tmp_path):
    url, _ = db
    out = subprocess.run([str(ROOT / ".venv" / "bin" / "jyotish"), "export-reviews", "--database", url, "--out", str(tmp_path)],
                         capture_output=True, text=True)
    assert out.returncode == 0 and "judgements, not outcomes; no birth data" in out.stdout
    assert (tmp_path / "rewrites.jsonl").exists() and (tmp_path / "judgements.jsonl").exists()
    ignore = (ROOT / ".gitignore").read_text()
    assert "data/preferences/" in ignore and "data/outcomes/" in ignore     # client data, kept apart
