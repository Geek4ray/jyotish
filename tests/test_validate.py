"""scripts/validate.py: the splits and the statistics (SPEC Layer 6 tests 1-8, 10), unit by unit,
and one run end to end over a small cohort imported through the capture path."""

import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("sklearn", reason="the validate extra is not installed: pip install -e '.[validate]'")
pytest.importorskip("statsmodels")
ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def V():
    sys.path.insert(0, str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location("validate", ROOT / "scripts" / "validate.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["validate"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_the_sequestered_cohort_is_frozen_and_never_redrawn(V, tmp_path):
    f = tmp_path / "sequestered.txt"
    ids = [f"S-{i:04d}" for i in range(400)]
    seq, meta = V.sequester(ids, f)
    assert 0.18 < len(seq) / len(ids) < 0.32 and f.read_text().startswith("# The sequestered cohort")
    before = f.read_text()
    again, _ = V.sequester(ids, f)
    assert again == seq and f.read_text() == before                          # frozen
    more, _ = V.sequester(ids + ["S-9999", "S-9998"], f)
    assert seq <= more and f.read_text().startswith(before.rstrip("\n"))       # appended, nothing redrawn
    other, _ = V.sequester(ids, tmp_path / "other.txt")
    assert other != seq                                                       # a new salt is a new draw
    assert "# unit: household" in f.read_text() and "# columns: subject assignment unit" in f.read_text()


def test_households_land_on_one_side_and_newcomers_follow(V, tmp_path):
    f = tmp_path / "s.txt"
    subs = [{"id": f"S-{i:04d}", "household": f"H-{i // 3:04d}" if i % 7 else None} for i in range(600)]
    seq, meta = V.sequester(subs, f, salt="households")       # fixed: ~200 units draw a share of 0.25 +- 0.03
    assert meta["unit"] == "household" and 0.18 < len(seq) / len(subs) < 0.32
    assert V.households_straddling(subs, seq) == 0
    by_h = {}
    for x in subs:
        if x["household"]:
            by_h.setdefault(x["household"], set()).add(x["id"] in seq)
    assert len(by_h) > 150 and all(len(v) == 1 for v in by_h.values())
    # A newcomer to an assigned household takes its side, whatever its own hash would say.
    more, _ = V.sequester(subs + [{"id": "S-9999", "household": "H-0001"}], f)
    assert ("S-9999" in more) == ("S-0003" in more) and seq <= more
    assert "S-9999 " in f.read_text() and " h:H-0001" in f.read_text()
    # A subject with no household is a unit of its own, and bare ids still work.
    assert V.split_unit({"id": "x", "household": None}) == "s:x" == V.split_unit("x")
    # A file written before units were recorded: its assignments stand; its subjects are their own units.
    old = tmp_path / "old.txt"
    old.write_text("# salt: abc\n# fraction: 0.25\n# created: 2026-01-01T00:00:00+00:00\n"
                   "S-0001 sequestered\nS-0002 development\n")
    seq2, _ = V.sequester([{"id": "S-0001", "household": "H-0000"}, {"id": "S-0002", "household": "H-0000"},
                           {"id": "S-0003", "household": "H-0000"}], old)
    assert "S-0001" in seq2 and "S-0002" not in seq2 and "S-0001 sequestered s:S-0001" in old.read_text()


def test_the_registry_refuses_a_lost_or_changed_split(V, tmp_path):
    f, reg = tmp_path / "s.txt", tmp_path / "reg.json"
    ids = [f"S-{i:03d}" for i in range(100)]
    seq, meta = V.sequester(ids, f, registry=reg)
    r = json.loads(reg.read_text())
    assert r["split"]["salt_sha256"] == hashlib.sha256(meta["salt"].encode()).hexdigest()
    assert r["split"]["unit"] == "household" and r["sequestered_scorings"] == [] and meta["registered"]
    again, _ = V.sequester(ids, f, registry=reg)
    assert again == seq
    f.unlink()
    with pytest.raises(RuntimeError, match="missing"):
        V.sequester(ids, f, registry=reg)                                    # no silent redraw
    V.sequester(ids, f, salt="another")                                       # a fresh file, another salt
    with pytest.raises(RuntimeError, match="not the one registered"):
        V.sequester(ids, f, registry=reg)


def test_groups_and_folds(V):
    subs = [{"id": str(i), "household": f"H{i // 3}", "cluster": "BPx" if i in (2, 3) else None,
             "decade": 1950 + 10 * (i % 4), "sex": "female" if i % 2 else "male", "region": "r"} for i in range(60)]
    g = V.groups_of(subs)
    assert g[0] == g[1] == g[2] == g[3] == g[4] == g[5] and g[6] != g[0]      # households joined by the cluster
    fold = V.folds(subs)
    for grp in set(g):
        assert len({fold[i] for i in range(60) if g[i] == grp}) == 1         # no group straddles a fold
    assert len(set(fold)) == 5


def test_benjamini_hochberg(V):
    r = V.bh({"a": 0.001, "b": 0.02, "c": 0.04, "d": 0.6})
    assert [r[k]["survives"] for k in "abcd"] == [True, True, False, False]
    assert r["c"]["p_adj"] == pytest.approx(0.04 * 4 / 3) and r["a"]["p_adj"] == pytest.approx(0.004)


def test_delong_matches_the_auc_and_detects_a_difference(V):
    from sklearn.metrics import roc_auc_score
    rng = np.random.default_rng(0)
    y = rng.integers(0, 2, 400)
    good = y + rng.normal(0, 0.8, 400)
    noise = rng.normal(0, 1, 400)
    d = V.delong(y, noise, good)
    assert d["auc_a"] == pytest.approx(roc_auc_score(y, noise)) and d["auc_b"] == pytest.approx(roc_auc_score(y, good))
    assert d["p"] < 1e-6
    twin = y + rng.normal(0, 0.8, 400)                                       # the same signal, other noise
    assert V.delong(y, good, twin)["p"] > 0.01


def test_power_follows_n(V):
    # SPEC Layer 6: a rule firing on 5% of 2,000 charts (n ~ 100) has ~0.2 power for a 5-point lift at
    # alpha 0.01, ~0.9 at 20,000; that holds for a base rate near 10%.
    small, big = V.power_two_props(0.1, 100, 1900), V.power_two_props(0.1, 1000, 19000)
    assert 0.15 < small < 0.25 and big > 0.9
    assert V.power_two_props(0.3, 100, 1900) < small                           # a commoner outcome needs more n
    assert V.power_two_props(0.3, 0, 10) == 0.0


def test_the_permutation_null_is_calibrated_and_finds_a_real_lift(V):
    rng = np.random.default_rng(1)
    strata = np.array(["a", "b"] * 150)
    pred = rng.random(300) < 0.3
    ps = []
    for _ in range(40):
        y = (rng.random(300) < 0.3).astype(float)
        ps.append(V.permutation_lift(y, pred, strata, rng, 200)[1])
    assert 0.3 < np.mean(ps) < 0.7                                            # uniform-ish under the null
    y = np.where(pred, rng.random(300) < 0.6, rng.random(300) < 0.25).astype(float)
    lift, p = V.permutation_lift(y, pred, strata, rng, 500)
    assert lift > 1.5 and p < 0.01


def test_the_bootstrap_resamples_households(V):
    # Thirty households of ten with one outcome each: the row bootstrap treats 300 draws as independent
    # and gives a narrow interval; the household bootstrap, which is the data's real sample size, a wide one.
    rng = np.random.default_rng(7)
    house = np.repeat(np.arange(30), 10)
    y = np.repeat((rng.random(30) < 0.4).astype(float), 10)
    pred = np.repeat(rng.random(30) < 0.5, 10)
    lo_r, hi_r = V.bootstrap_ci(y, pred, np.random.default_rng(1), 400)
    lo_h, hi_h = V.bootstrap_ci(y, pred, np.random.default_rng(1), 400, groups=house)
    assert hi_h - lo_h > 1.5 * (hi_r - lo_r)
    assert lo_h <= V.lift_stats(y, pred) <= hi_h


def test_the_analysis_code_hash_covers_the_feature_code(V, tmp_path, monkeypatch):
    _, meta = V.sequester(["a", "b"], tmp_path / "s.txt")
    before = V.hashes(meta)["analysis_code"]
    src = V.ROOT / "src" / "jyotish" / "cohort.py"
    original = src.read_bytes()
    try:
        src.write_bytes(original + b"\n# touched\n")
        assert V.hashes(meta)["analysis_code"] != before
    finally:
        src.write_bytes(original)
    assert V.hashes(meta)["analysis_code"] == before


def test_the_delong_cell_marks_a_fall(V):
    assert V._delong_cell({"delong_p": 0.012, "auc_covariates": 0.494, "auc_with_engine": 0.487}) == "0.0120 (AUC fell)"
    assert V._delong_cell({"delong_p": 0.012, "auc_covariates": 0.494, "auc_with_engine": 0.540}) == "0.0120"
    assert V._delong_cell({"delong_p": float("nan"), "auc_covariates": float("nan"), "auc_with_engine": 0.5}) == "–"


def test_outcome_rows(V):
    ev = [{"type": "occupation", "age": 35, "censor": 50, "value": {"isei": 72}},
          {"type": "tenure_change", "age": None, "censor": 50, "value": None}]
    assert V.outcome(ev, ["occupation", "tenure_change"], 60) == {"case": True, "age": 35, "censor": 50}
    low = [dict(ev[0], value={"isei": 30}), ev[1]]
    assert V.outcome(low, ["occupation", "tenure_change"], 60) == {"case": False, "age": 50, "censor": 50}
    assert V.outcome(ev, ["first_child"], 60) is None                         # no data is not a non-case


def test_hazard_finds_a_planted_window_and_not_a_random_one(V):
    rng = np.random.default_rng(2)
    rows = []
    for i in range(400):
        active = [(20.0, 30.0)] if i % 2 else [(40.0, 50.0)]
        if rng.random() < 0.6:
            a, b = active[0]
            age = float(rng.uniform(a, b)) if rng.random() < 0.7 else float(rng.uniform(15, 60))
            rows.append({"case": True, "age": age, "active": active})
        else:
            rows.append({"case": False, "age": 60.0, "active": active})
    h = V.hazard(rows, rng, shifts=100)
    assert h["rate_ratio"] > 2 and h["p_random_windows"] < 0.05 and h["logistic"]["log_odds"] > 0.5
    assert 0 < h["coverage"] < 1 and h["person_years"] > 10000


def test_hashes_name_the_rule_weight_split_and_code(V, tmp_path):
    _, meta = V.sequester(["a", "b"], tmp_path / "s.txt")
    h = V.hashes(meta)
    assert all(len(h[k]) == 64 for k in ("rule_set", "weight_set", "split_definition", "analysis_code"))
    _, meta2 = V.sequester(["a", "b"], tmp_path / "s2.txt")
    assert V.hashes(meta2)["split_definition"] != h["split_definition"] and V.hashes(meta2)["rule_set"] == h["rule_set"]


def test_school_split_chooses_the_school_whose_votes_predict(V):
    from sklearn.metrics import roc_auc_score
    rng = np.random.default_rng(4)
    rows = []
    for i in range(600):
        par = {f: int(rng.integers(-1, 2)) for f in ("house", "lord", "karaka", "varga", "panchanga")}
        votes = dict(par, arudha=int(rng.integers(-1, 2)), kp=None if i % 3 else int(rng.integers(-1, 2)))
        p = 1 / (1 + math.exp(-(0.8 * sum(par.values()) - 0.2)))
        rows.append({"case": bool(rng.random() < p), "votes": votes})
    sp = V.school_split(rows[:450], rows[450:])
    assert sp["chosen"] == "parashari" and sp["schools"]["nadi"]["status"] == "no vote in this area"
    par = sp["schools"]["parashari"]
    y = np.array([r["case"] for r in rows[:450]], dtype=float)
    s = np.array([V.school_score(r["votes"], "parashari") for r in rows[:450]])
    assert par["auc"] == pytest.approx(roc_auc_score(y, s)) and par["ci"][0] < par["auc"] < par["ci"][1] < 1
    assert par["auc"] > 0.6 and par["status"] == "compared" and par["coverage"] == 1.0
    assert sp["schools"]["kp"]["n"] == sum(1 for r in rows[:450] if r["votes"]["kp"] is not None)
    assert sp["sequestered"] is not None and 0 < sp["sequestered"]["auc"] <= 1 and sp["sequestered"]["n"] == 150
    assert V.school_split(rows[:450])["sequestered"] is None                 # not scored: not estimated
    assert V.school_score({"house": 1, "lord": None}, "parashari") == 1.0 and V.school_score({}, "jaimini") is None
    assert V.school_split(rows[:10])["chosen"] is None                       # too few to compare


def test_end_to_end_on_a_small_imported_cohort(V, tmp_path):
    from datetime import date
    from jyotish import outcomes as oc
    rng = np.random.default_rng(3)
    url = f"sqlite:///{tmp_path / 'c.db'}"
    Session = oc.sessionmaker_for(url)
    rows = []
    with Session.begin() as s:
        for i in range(160):
            sid = f"T-{i:04d}"
            oc.add_consent(s, f"C-{sid}", sid, "test", "new", "test")
            y, m, d = 1950 + int(rng.integers(0, 50)), 1 + int(rng.integers(0, 12)), 1 + int(rng.integers(0, 28))
            age = (date(2026, 10, 22) - date(y, m, d)).days / 365.25
            base = {"consent_id": f"C-{sid}", "subject_id": sid, "date": f"{y}-{m:02d}-{d:02d}", "time": "06:30",
                    "tz": "UTC", "lat": f"{rng.uniform(-50, 50):.3f}", "lon": f"{rng.uniform(-170, 170):.3f}",
                    "node": "mean", "accuracy": "exact" if i % 10 else "unknown", "sex": "female" if i % 2 else "male",
                    "region": "north" if i % 3 else "south", "source": "file", "rectified": "no",
                    "household_key": f"H{i // 2}", "censor_age": f"{age:.1f}", "self_report": "no"}
            for e in ("first_marriage", "first_child", "first_relocation_abroad"):
                happened = rng.random() < 0.4
                rows.append(dict(base, event_type=e, age_at_event=f"{rng.uniform(18, age - 1):.1f}" if happened else ""))
        res = oc.import_rows(s, rows, entered_by="test")
    assert res.accepted == len(rows)
    reg = tmp_path / "reg.json"
    res = V.run(V.load_cohort(url), tmp_path / "seq.txt", permutations=100, bootstrap=100, shifts=20, registry=reg)
    assert res["groups_straddling_folds"] == 0 and res["n_sequestered"] + res["n_development"] == 160
    assert res["households_straddling_the_split"] == 0 and res["split"] == {"unit": "household", "registered": True}
    r = json.loads(reg.read_text())
    assert "split" in r and r["sequestered_scorings"] == [] and "sequestered_scorings" not in res
    m = res["areas"]["marriage"]
    assert m["status"] == "tested" and 0 < m["coverage"] < 1 and m["n_with_outcome"] == res["n_development"]
    assert {"lift", "lift_ci", "p_permutation", "p_adj", "survives", "nested", "timing", "calibration", "power_5pt"} <= set(m)
    assert m["calibration"]["gate"] is None and m["probability_language"] is False   # the sequestered cohort was not scored
    assert m["school_split"]["sequestered"] is None and set(m["school_split"]["schools"]) == {"parashari", "jaimini", "kp", "nadi"}
    assert res["areas"]["personality"]["status"] == "not_testable_yet"
    assert res["areas"]["career"]["status"] == "insufficient"                 # no occupation rows in this cohort
    md = V.report(res)
    for heading in ("Pre-registration hashes", "Lift of the tier", "nested models", "discrete-time hazard",
                    "Calibration", "School-split (test 8)", "Power at the current n", "Per-rule effects"):
        assert heading in md
    assert "Synthetic" not in md and "0 households straddle it" in md and "was not scored" in md
    # Scoring the sequestered cohort is logged in the registry, and the report says how many times.
    res2 = V.run(V.load_cohort(url), tmp_path / "seq.txt", permutations=50, bootstrap=50, shifts=10, registry=reg,
                 score_sequestered=True)
    assert res2["sequestered_scorings"] == 1 and res2["n_sequestered"] == res["n_sequestered"]
    logged = json.loads(reg.read_text())["sequestered_scorings"]
    assert len(logged) == 1 and logged[0]["n_sequestered"] == res["n_sequestered"] and "marriage" in logged[0]["areas"]
    assert "logs 1 scoring(s)" in V.report(res2)
