"""The checker benchmark (tests/fixtures/checker_bench.jsonl, scripts/checker_bench.py): the file's
schema, its construction, and that the code validator alone rejects every row whose category is a
tag or wording error and no accepted row. The validator + live checker run is marked live."""

import importlib.util
import json
import os
import sys
from pathlib import Path

import pytest

from jyotish.narrate import TAG, sentences

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def cb():
    spec = importlib.util.spec_from_file_location("checker_bench", ROOT / "scripts" / "checker_bench.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["checker_bench"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def rows(cb):
    return cb.load()


def test_the_file_has_its_schema(cb, rows):
    assert len(rows) >= 100
    keys = {"id", "sentence", "tags", "facts", "label", "category", "origin", "where", "area", "finding_id", "validator"}
    ids = [r["id"] for r in rows]
    assert len(ids) == len(set(ids))
    for r in rows:
        assert keys <= set(r), r["id"]
        assert r["label"] in ("accept", "reject") and r["where"] in ("claim", "summary", "paragraph")
        assert r["tags"] == [f"{k}:{v}" for k, v in TAG.findall(r["sentence"])]
        assert isinstance(json.loads(r["facts"]), dict)                   # what the checker is given
        assert set(r["validator"]) == {"allowed", "offered_votes", "chains", "family_rule"}
        assert (r["category"] == "accepted") == (r["label"] == "accept")
    cats = {r["category"] for r in rows}
    assert set(cb.CONSTRUCTED) <= cats
    assert {"refers_to_another_claim", "tag_not_offered", "family_not_cited", "forbidden_word", "untagged"} <= cats
    assert cats - {"accepted"} <= cb.WORDING | cb.SEMANTIC


def test_accepted_rows_are_the_reading_audited(cb, rows):
    reading = json.loads(cb.READING.read_text())
    expected = sentences(reading["summary"]["text"])
    for a in reading["areas"]:
        expected += [c["text"] for c in a["claims"]] + sentences(a["paragraph"] or "")
    accepted = [r for r in rows if r["label"] == "accept"]
    assert sorted(r["sentence"] for r in accepted) == sorted(expected) and len(accepted) == 45
    assert all(r["audit"] and "CONTRADICTED" not in r["audit"] for r in accepted)
    assert sum("ratio" in r["audit"] for r in accepted) >= 8                  # strength words computed
    accepted_ids = {r["id"] for r in accepted}
    for r in rows:
        if r["category"] in cb.CONSTRUCTED:
            assert any(f"constructed from {i}" in r["origin"] for i in accepted_ids), r["id"]
    for r in rows:                                                           # one change each, never the original
        if r["label"] == "reject":
            assert r["sentence"] not in expected


def test_dasha_rows_cite_the_chain_that_names_the_true_lord(rows):
    dasha = [r for r in rows if r["category"] == "dasha_lord_changed"]
    assert len(dasha) == 6
    for r in dasha:
        facts = r["facts"]
        assert any(t.startswith("chain:") for t in r["tags"]) and "activated by the current" in facts
        wrong = r["sentence"].split("current major period of ")[1].split(" ")[0]
        assert f"current major period (mahadasha) of {wrong}" not in facts and f"sub-period (antardasha) of {wrong}" not in facts


def test_the_validator_alone_catches_every_tag_and_wording_error_and_no_accepted_row(cb, rows):
    pred = cb.run_validator(rows)
    for r in rows:
        if r["category"] in cb.WORDING:
            assert pred[r["id"]][0], (r["id"], r["sentence"])
        if r["label"] == "accept":
            assert not pred[r["id"]][0], (r["id"], pred[r["id"]][1])
    s = cb.scores(rows, pred)
    assert s["overall"]["precision"] == 1.0 and s["tier_word"]["recall"] == 1.0


def test_the_file_is_what_the_builder_makes(cb, rows):
    assert cb.build() == rows                                                # regenerate with --build


@pytest.mark.live
@pytest.mark.skipif(os.environ.get("JYOTISH_LIVE_NARRATION") != "1", reason="set JYOTISH_LIVE_NARRATION=1 to call the API")
def test_live_validator_and_checker(cb, rows):
    import time
    t = time.time()
    pred, usage = cb.run_live(rows)
    cb.SCORECARD.write_text(cb.report(rows, cb.run_validator(rows), (pred, usage, time.time() - t)))
    assert set(pred) == {r["id"] for r in rows} and usage["calls"] > 0
