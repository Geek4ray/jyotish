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
        assert r["label"] in ("accept", "reject") and r["where"] in ("claim", "summary", "paragraph", "analysis")
        assert r["tags"] == [f"{k}:{v}" for k, v in TAG.findall(r["sentence"])]
        assert isinstance(json.loads(r["facts"]), dict)                   # what the checker is given
        assert set(r["validator"]) - {"full"} == {"allowed", "offered_votes", "chains", "family_rule"}
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
    rows = [r for r in rows if not r["id"].startswith(("b-", "r2-", "kind-", "live-"))]   # comparisons', kinds', live: own tests
    accepted = [r for r in rows if r["label"] == "accept"]
    # 2026-10-31: three paragraph sentences the reading accepted break the client's words, now held at
    # curious depth; they are wording rejects (client_words), the rest of the reading as it was.
    relabelled = [r for r in rows if r["category"] == "client_words"]
    assert {r["id"] for r in relabelled} == {"accept-18", "accept-19", "accept-44"}
    expected = [x for x in expected if x not in {r["sentence"] for r in relabelled}]
    assert sorted(r["sentence"] for r in accepted) == sorted(expected) and len(accepted) == 42
    assert all(r["audit"] and "CONTRADICTED" not in r["audit"] for r in accepted)
    assert sum("ratio" in r["audit"] for r in accepted) >= 8                  # strength words computed
    accepted_ids = {r["id"] for r in accepted + relabelled}         # a constructed row's source, relabelled or not
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


def test_an_offline_run_keeps_the_live_section_on_record(cb, tmp_path, monkeypatch):
    old = ("# Checker benchmark\n\nRun 2026-10-22 at commit `b0eb697` by `scripts/checker_bench.py`.\n\n"
           "## The code validator alone\n\nold table\n\n" + cb.LIVE_HEADING + "\n\nModel claude-opus-5-5, checker effort high; "
           "103 checker calls.\n\n| category | n | caught / false rejects | precision | recall | F1 |\n"
           "| overall | 119 | 72 of 74 | 1.000 | 0.973 | 0.986 |\n")
    out = tmp_path / "checker_scorecard.md"
    out.write_text(old)
    monkeypatch.setattr(cb, "SCORECARD", out)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert cb.main(["--offline"]) == 0
    new = out.read_text()
    assert "old table" not in new and "| overall | 119 | 72 of 74 | 1.000 | 0.973 | 0.986 |" in new
    assert "Carried over from the run of 2026-10-22 at commit `b0eb697`" in new and new.count(cb.LIVE_HEADING) == 1
    assert cb.main(["--offline"]) == 0 and out.read_text().count("Carried over") == 1       # once, not twice


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



def test_the_comparisons_refusals_carry_the_lesson(cb, rows):
    """Every refusal of reading B (docs/comparison_2026-10-23) that was the engine's fault is a row, with
    the label the engine now makes it earn: verbatim from B's recording unless built from one of them
    by the change its origin names, accepted rows audited, rejected ones refused by the validator when
    they are wording errors and left to the checker when they are not."""
    b = {r["id"]: r for r in rows if r["id"].startswith("b-")}
    assert len(b) == 21 and all(r["origin"].startswith("comparison 2026-10-23, reading B: ") for r in b.values())
    kinds = {"varga label": ["b-varga-career", "b-varga-marriage", "b-varga-longevity"],
             "stability label": ["b-stability-career", "b-stability-marriage", "b-stability-longevity"],
             "ranking": ["b-ranking-career", "b-ranking-longevity"], "houses": ["b-nth-sign"], "arudha": ["b-arudha"],
             "not computed": ["b-synastry"], "judgement": ["b-judgement-marriage"],
             "validator": ["b-chain-navamsa", "b-tradition-family", "b-hyphen", "b-votes-fact"]}
    assert set(sum(kinds.values(), [])) | {k for k in b if k.endswith(("-fixed", "-percentile"))} == set(b)
    rec = json.loads(cb.COMPARISON.read_text())
    said = json.dumps(rec)
    for rid, r in b.items():
        if not rid.endswith(("-fixed", "-percentile")):
            assert json.dumps(r["sentence"])[1:-1] in said, rid                # B's own words
        assert r["validator"]["full"] == cb.FULL and isinstance(json.loads(r["facts"]), dict)
        if r["label"] == "accept":
            assert r["audit"] and r["category"] == "accepted"
    pred = cb.run_validator(list(b.values()))
    for rid, r in b.items():
        if r["label"] == "accept":
            assert not pred[rid][0], (rid, pred[rid][1])
        elif r["category"] in cb.WORDING:
            assert pred[rid][0], rid
    assert all(not pred[k][0] for k in ("b-arudha", "b-synastry", "b-votes-fact"))   # the checker's to catch
    facts = json.loads(b["b-varga-career"]["facts"])                 # a claim citing no fact: its finding's data
    assert {x["varga_dignity_label"] for x in facts["derivation"]} >= {"exalted", "own"}
    assert json.loads(b["b-judgement-marriage"]["facts"])["judgement"] is True



def test_the_re_runs_two_gaps_are_accepted_with_the_facts_the_engine_now_gives(cb, rows):
    """docs/comparison_2026-10-23_r2: reading B's two narration gaps, both refused for want of a fact,
    verbatim from B's recording, now passing the validator with every cited field stating what the
    sentence says: Saturn's D10 dignity, and the Kantaka Shani spans' areas."""
    r2 = {r["id"]: r for r in rows if r["id"].startswith("r2-")}
    assert set(r2) == {"r2-varga-dignity", "r2-areas-touched"}
    said = json.dumps(json.loads(cb.COMPARISON_R2.read_text()))
    for rid, r in r2.items():
        assert json.dumps(r["sentence"])[1:-1] in said, rid                       # B's own words
        assert r["origin"].startswith("comparison 2026-10-23 r2, reading B: ") and r["audit"]
        assert (r["label"], r["category"], r["where"]) == ("accept", "accepted", "analysis")
        assert json.loads(r["facts"])["judgement"] is True                       # premises checked, weighing not
    pred = cb.run_validator(list(r2.values()))
    assert not any(rejected for rejected, _ in pred.values()), pred
    assert json.loads(r2["r2-varga-dignity"]["facts"])["facts"]["vargas.D10.Saturn"] == {"sign": "Capricorn",
                                                                                          "dignity": "own"}
    spans = json.loads(r2["r2-areas-touched"]["facts"])["facts"]
    for w in ("transits.windows.1", "transits.windows.3"):
        assert spans[w]["kind"] == "kantaka_shani" and "grade:adverse" in spans[w]["tags"]
        assert spans[w]["areas_touched"][0]["from_moon"] == {"house": 7, "areas": ["marriage", "foreign"]}


def test_each_new_sentence_kind_reaches_the_live_checker(cb, rows):
    """The review of 2026-10-23, F5: rows of each new kind that the validator passes, so the live run
    measures the checker on them: an accepted judgement, a judgement with a false premise, a synthesis
    whose conclusion does not follow, and an untagged sentence of each label."""
    k = {r["id"]: r for r in rows if r["id"].startswith("kind-")}
    assert set(k) == {"kind-judgement-accept", "kind-judgement-premise", "kind-synthesis-does-not-follow",
                      "kind-untagged-summary", "kind-untagged-framing"}
    pred = cb.run_validator(list(k.values()))
    assert not any(rejected for rejected, _ in pred.values()), pred          # every one reaches the checker
    marks = {rid: json.loads(r["facts"]) for rid, r in k.items()}
    assert marks["kind-judgement-accept"]["judgement"] and marks["kind-judgement-premise"]["judgement"]
    assert marks["kind-synthesis-does-not-follow"]["synthesis"]
    assert marks["kind-untagged-summary"]["findings"] == [] and not k["kind-untagged-summary"]["tags"]
    assert [k[x]["label"] for x in sorted(k)] == ["accept", "reject", "reject", "accept", "reject"]
    # the gate's own kind in the analysis: an untagged analysis sentence is the validator's to refuse
    analysis = dict(k["kind-untagged-summary"], where="analysis", area="career", section="assessment",
                    validator=dict(k["kind-judgement-accept"]["validator"]))
    assert cb.run_validator([analysis])[analysis["id"]][0]


def test_the_three_label_disagreements_are_settled(rows):
    """F8: b-hyphen and b-votes-fact (a last clause no field states) carry one label; b-judgement-marriage
    is rejected on its arudha premise, which is false on the facts."""
    b = {r["id"]: r for r in rows}
    assert (b["b-hyphen"]["label"], b["b-hyphen"]["category"]) == ("reject", "unstated_claim") == \
        (b["b-votes-fact"]["label"], b["b-votes-fact"]["category"])
    assert "rests on UL, UL2 and A7" in b["b-judgement-marriage"]["origin"]
    facts = json.loads(b["b-stability-career"]["facts"])["facts"]
    assert facts["stability.lagna_sign_by_varga.D10"]["samples"] == "holds in 159 of 200 birth-time samples"


def test_the_live_readings_false_reject_is_a_row_the_validator_passes(cb, rows):
    # 2026-10-27: a placement claim stating its lordship as "rules the 2nd" was refused on every attempt.
    row = next(r for r in rows if r["id"] == "live-rules-the-2nd")
    assert row["label"] == "accept" and "rules the 2nd" in row["sentence"]
    assert cb.run_validator([row])[row["id"]][0] is False


def test_a_lordship_in_a_list_is_a_row_the_validator_passes(cb, rows):
    # 2026-10-31: the first reading on Fly lost its career paragraph to "the lord of the 2nd and 5th houses".
    row = next(r for r in rows if r["id"] == "live-lord-of-the-2nd-and-5th")
    assert (row["where"], row["label"]) == ("paragraph", "accept") and "2nd and 5th houses" in row["sentence"]
    assert cb.run_validator([row])[row["id"]][0] is False


def test_a_yoga_named_with_a_non_breaking_hyphen_is_a_row_the_validator_passes(cb, rows):
    # 2026-10-31: the curious comparison's career paragraph was refused for "Kendra\u2011Trikona" (U+2011).
    row = next(r for r in rows if r["id"] == "live-kendra-nonbreaking-hyphen")
    assert row["label"] == "accept" and "\u2011" in row["sentence"]
    assert cb.run_validator([row])[row["id"]][0] is False
