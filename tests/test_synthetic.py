"""Synthetic cohorts prove the validation pipeline (scripts/synthetic_cohort.py, scripts/validate.py):
a planted effect on the engine's own area score is recovered, and events independent of the chart
leave no area surviving Benjamini-Hochberg. Small N here; the harness runs 2,000 and 20,000."""

import importlib.util
import sys
from pathlib import Path

import pytest

pytest.importorskip("sklearn", reason="the validate extra is not installed: pip install -e '.[validate]'")
pytest.importorskip("statsmodels")
ROOT = Path(__file__).resolve().parents[1]


def _load(name):
    sys.path.insert(0, str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mods():
    return _load("validate"), _load("synthetic_cohort")


def _run(mods, tmp_path, mode, n, **kw):
    V, SC = mods
    url = f"sqlite:///{tmp_path / f'{mode}.db'}"
    feats, truth = SC.make(n, mode, url, seed=5, **kw)
    res = V.run(V.load_cohort(url, features=feats, synthetic=True), tmp_path / f"seq_{mode}.txt",
                score_sequestered=True, permutations=400, bootstrap=200, shifts=60, salt="synthetic-test")
    return V, SC, truth, res


def test_a_planted_effect_is_recovered(mods, tmp_path):
    V, SC, truth, res = _run(mods, tmp_path, "planted", 900, odds_ratio=3.0, timing_weight=3.0)
    c = SC.compare(truth, res)
    assert set(c["planted_areas"]) == {"wealth", "mother_home", "children", "intellect", "health", "marriage",
                                       "career", "foreign"}                      # the areas that own an event
    assert c["predicted_power_mean"] > 0.8
    assert c["recovered_share"] >= 0.75 and c["survived_bh_share"] >= 0.6
    assert abs(c["recovered_share"] - c["predicted_power_mean"]) < 0.3          # roughly the predicted power
    assert c["timing_recovered_share"] >= 0.5                                   # the planted window effect
    assert all(res["areas"][a]["nested"]["p_lr"] < 0.05 for a in c["planted_areas"])   # terms add to covariates
    assert not truth["areas"]["father"]["planted"] and truth["areas"]["father"]["owns_events"] == []
    md = V.report(res, label="planted, N = 900")
    assert all("Synthetic" in line for line in md.splitlines() if line.startswith("#"))


def test_a_null_cohort_has_no_area_surviving_bh(mods, tmp_path):
    V, SC, truth, res = _run(mods, tmp_path, "null", 900)
    c = SC.compare(truth, res)
    assert c["planted_areas"] == [] and c["areas_tested"] >= 10
    assert c["areas_surviving_bh"] == 0
    assert c["rules_with_effect"] <= 2                                          # BH across rules at q 0.01
    assert all(abs(t["planted_points"]) < 1e-9 for t in truth["areas"].values())


def test_features_are_shared_between_the_planted_and_the_null_cohort_of_one_size(mods, tmp_path):
    V, SC = mods
    feats, truth = SC.make(60, "planted", f"sqlite:///{tmp_path / 'p.db'}", seed=3)
    again, truth2 = SC.make(60, "null", f"sqlite:///{tmp_path / 'n.db'}", seed=3, features=feats)
    assert again is feats and set(truth2["areas"]) == set(truth["areas"])
    assert all(abs(t["planted_points"]) < 1e-9 for t in truth2["areas"].values())      # a null: identical means
    with pytest.raises(ValueError, match="other births"):
        SC.make(50, "null", f"sqlite:///{tmp_path / 'o.db'}", seed=3, features=feats)


def test_a_fixed_salt_makes_a_synthetic_run_reproducible_and_is_refused_for_a_real_cohort(mods, tmp_path):
    V, SC = mods
    url = f"sqlite:///{tmp_path / 'r.db'}"
    feats, _ = SC.make(120, "null", url, seed=9)
    runs = [V.run(V.load_cohort(url, features=feats, synthetic=True), tmp_path / f"s{i}.txt", permutations=50,
                  bootstrap=20, shifts=5, salt="fixed") for i in range(2)]
    assert runs[0]["n_sequestered"] == runs[1]["n_sequestered"]
    assert runs[0]["areas"]["marriage"]["lift"] == runs[1]["areas"]["marriage"]["lift"]
    with pytest.raises(ValueError):
        V.run(V.load_cohort(url, features=feats), tmp_path / "s9.txt", salt="fixed")


def test_synthetic_runs_never_touch_the_real_split(mods, tmp_path):
    V, SC = mods
    real, registry = ROOT / "data" / "sequestered.txt", ROOT / "docs" / "pre_registration.json"
    before = real.read_text() if real.exists() else None
    reg_before = registry.read_text() if registry.exists() else None
    _run(mods, tmp_path, "null", 60)
    assert (real.read_text() if real.exists() else None) == before
    assert (registry.read_text() if registry.exists() else None) == reg_before
    # Even when a registry is given, a synthetic cohort never writes one.
    url = f"sqlite:///{tmp_path / 'r2.db'}"
    feats, _ = SC.make(60, "null", url, seed=11)
    V.run(V.load_cohort(url, features=feats, synthetic=True), tmp_path / "s_r2.txt", permutations=20, bootstrap=10,
          shifts=5, salt="fixed", registry=tmp_path / "never.json")
    assert not (tmp_path / "never.json").exists()
    with pytest.raises(SystemExit):
        SC.main(["--n", "5", "--mode", "null", "--database", "sqlite:///jyotish.db"])
