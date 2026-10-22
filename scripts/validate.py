"""SPEC Layer 6 validation over any cohort in the database: the splits, then the tests.

    .venv/bin/pip install -e ".[validate]"
    .venv/bin/python scripts/validate.py --database sqlite:///jyotish.db          # docs/validation.md
    .venv/bin/python scripts/validate.py --database ... --score-sequestered       # once per numbered release

Cohort: every subject whose chart is not rectified, and their events not flagged `after`. Each chart
is computed from its birth data (Lahiri, the subject's node) with the engine's area scores, tiers and
terms, its fired rules and its window activation.

1. Splits. The sequestered 25% is chosen by a salted hash of the subject id. data/sequestered.txt
   holds the salt and every assignment, frozen the first time it runs: an assignment is never redrawn,
   and a subject added later is assigned by the same salted hash and appended. The other 75% is the
   development set, with grouped K-fold (K = 5): groups are the connected components of shared
   household and birthplace-cluster keys, so related charts never straddle a fold, stratified by
   birth decade, sex and region. Every test below runs on the development set, except that the
   sequestered cohort is scored when --score-sequestered is given, once per numbered release.
2. Lift per area of the engine's tier (strong or moderate counts as a positive prediction) against
   the area's mapped events (data/outcome_map.yaml). The permutation null permutes labels within
   birth decade x sex x region strata (>= 1,000 permutations); there is a 95% bootstrap interval,
   and Benjamini-Hochberg across areas.
3. Nested models per area: covariates (age, sex, region, era) against covariates plus the area's own
   engine terms from scoring. SPEC's "~50 terms" counts terms across areas; v1 uses each area's own.
   Likelihood-ratio test in sample, and DeLong on the out-of-fold AUCs.
4. Timing as a discrete-time hazard. Person-years from birth to the first mapped event or censoring,
   with the area's window activation as a time-varying covariate: the year mostly inside a
   Vimshottari antar whose lord, or a planet it activates, is relevant to the area. This is the
   engine's window gate without the transit term. Compared with coverage-matched random windows
   (each subject's own activation pattern shifted round their lifetime).
5. Abstention: an area with no score, or one whose accuracy class cannot pass the stability gate
   (approximate, unknown), is an abstention. Every number carries its coverage.
6. Per-rule effects with intervals, and the powered-null rule: classical_rejected is recommended
   only when power >= 0.8 for a 5-point lift at alpha 0.01 and the effect is not significant;
   otherwise the rule is not_testable_yet.
7. Calibration: an isotonic map from the area score to the event rate, its expected calibration
   error, and the gate of >= 200 positives in every bin that decides whether probability language
   is allowed. On development folds it is provisional; the gate is decided on the sequestered cohort.
8. A power table per area at the current n.
10. Pre-registration hashes: the rule set, the weight set, the split definition and this script."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import secrets
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

SEQUESTERED = ROOT / "data" / "sequestered.txt"
DOC = ROOT / "docs" / "validation.md"
FRACTION = 0.25
K = 5
POSITIVE_TIERS = ("strong", "moderate")
ABSTAIN_ACCURACY = ("approximate", "unknown")
PERMUTATIONS = 1000
BOOTSTRAP = 1000
SHIFTS = 200
ALPHA_RULE = 0.01
LIFT_POINTS = 0.05
BIN_GATE = 200
MAX_AGE = 120


# --- the cohort -----------------------------------------------------------------------------------

def features_for(births: dict[str, dict], workers: int | None = None) -> dict[str, dict]:
    from jyotish.cohort import features_for as f
    return f(births, workers)


@dataclass
class Cohort:
    subjects: list[dict]                       # id, chart_id, sex, region, decade, accuracy, source, groups
    events: dict[str, list[dict]]              # subject id -> events (not `after`)
    features: dict[str, dict]                  # chart id -> chart_features
    synthetic: bool = False


def load_cohort(database_url: str, features: dict | None = None, synthetic: bool = False) -> Cohort:
    from jyotish.api import EventRow, SubjectRow
    from jyotish.outcomes import sessionmaker_for
    Session = sessionmaker_for(database_url)
    with Session() as s:
        subs = [x for x in s.query(SubjectRow).order_by(SubjectRow.id) if not x.rectified]
        evs = {}
        for e in s.query(EventRow).filter_by(after=False):
            evs.setdefault(e.subject_id, []).append({"type": e.event_type, "age": e.age_at_event, "censor": e.censor_age,
                                                     "value": e.value})
        subjects = [{"id": x.id, "chart_id": x.chart_id, "sex": x.sex, "region": x.region, "accuracy": x.accuracy,
                     "source": x.source, "decade": int(str(x.birth["date"])[:3] + "0"), "household": x.household_key,
                     "cluster": x.birthplace_cluster, "birth": x.birth} for x in subs]
    have = dict(features or {})
    need = {x["chart_id"]: x["birth"] for x in subjects if x["chart_id"] not in have}
    have.update(features_for(need))
    return Cohort(subjects, evs, have, synthetic)


# --- splits ---------------------------------------------------------------------------------------

def _hash_unit(salt: str, sid: str) -> float:
    return int(hashlib.sha256(f"{salt}:{sid}".encode()).hexdigest(), 16) / 2 ** 256


def sequester(ids: list[str], path: Path = SEQUESTERED) -> tuple[set[str], dict]:
    """The sequestered ids, frozen in `path` (created on first use, appended for new subjects)."""
    if path.exists():
        lines = path.read_text().splitlines()
        meta = dict(x[2:].split(": ", 1) for x in lines if x.startswith("# ") and ": " in x)
        assign = dict(x.split(" ", 1) for x in lines if x and not x.startswith("#"))
        salt = meta["salt"]
    else:
        salt, assign, meta = secrets.token_hex(16), {}, {}
        meta = {"salt": salt, "fraction": str(FRACTION), "created": datetime.now(timezone.utc).isoformat()}
    new = [i for i in ids if i not in assign]
    for i in new:
        assign[i] = "sequestered" if _hash_unit(salt, i) < float(meta.get("fraction", FRACTION)) else "development"
    if new or not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        head = ["# The sequestered cohort (SPEC Layer 6 test 1): frozen; an assignment is never redrawn.",
                f"# salt: {salt}", f"# fraction: {meta.get('fraction', FRACTION)}", f"# created: {meta['created']}"]
        path.write_text("\n".join(head + [f"{k} {v}" for k, v in assign.items()]) + "\n")
    return {i for i, v in assign.items() if v == "sequestered"}, {"salt": salt, "file_sha256": hashlib.sha256(
        path.read_bytes()).hexdigest()}


def groups_of(subjects: list[dict]) -> list[int]:
    """Connected components of shared household and birthplace-cluster keys."""
    parent = list(range(len(subjects)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    first: dict[tuple, int] = {}
    for i, s in enumerate(subjects):
        for key in (("h", s["household"]), ("c", s["cluster"])):
            if key[1]:
                if key in first:
                    parent[find(i)] = find(first[key])
                else:
                    first[key] = i
    return [find(i) for i in range(len(subjects))]


def stratum(s: dict) -> str:
    return f"{s['decade']}|{s['sex']}|{s['region']}"


def folds(subjects: list[dict], seed: int = 0) -> np.ndarray:
    import warnings
    from sklearn.model_selection import StratifiedGroupKFold
    warnings.filterwarnings("ignore", message="The least populated class", category=UserWarning)
    g = np.array(groups_of(subjects))
    y = np.array([stratum(s) for s in subjects])
    out = np.zeros(len(subjects), dtype=int)
    k = min(K, len(set(g)))
    try:
        splits = list(StratifiedGroupKFold(n_splits=k, shuffle=True, random_state=seed).split(y, y, g))
    except ValueError:                       # a cohort too small to stratify: groups only
        from sklearn.model_selection import GroupKFold
        splits = list(GroupKFold(n_splits=k).split(y, y, g))
    for f, (_, test) in enumerate(splits):
        out[test] = f
    return out


# --- outcomes per area --------------------------------------------------------------------------

def outcome(events: list[dict], mapped: list[str], isei_threshold: float) -> dict | None:
    """(case, age at first mapped event or censoring) from a subject's rows of the mapped types; None
    when the subject has no row of any mapped type (no data, not a non-case)."""
    rows = [e for e in events if e["type"] in mapped]
    if not rows:
        return None
    ages = []
    for e in rows:
        if e["age"] is None:
            continue
        if e["type"] == "occupation" and (e.get("value") or {}).get("isei", 0) < isei_threshold:
            continue
        ages.append(e["age"])
    censor = max(e["censor"] for e in rows)
    return {"case": bool(ages), "age": min(ages) if ages else censor, "censor": censor}


# --- statistics -----------------------------------------------------------------------------------

def bh(pvals: dict[str, float], q: float = 0.05) -> dict[str, dict]:
    """Benjamini-Hochberg: adjusted p and whether each survives at q."""
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    adj, running = {}, 1.0
    for rank in range(m, 0, -1):
        k, p = items[rank - 1]
        running = min(running, p * m / rank)
        adj[k] = running
    return {k: {"p_adj": adj[k], "survives": adj[k] <= q} for k in pvals}


def lift_stats(y: np.ndarray, pred: np.ndarray) -> float:
    base = y.mean()
    return float(y[pred].mean() / base) if pred.any() and base > 0 else float("nan")


def permutation_lift(y: np.ndarray, pred: np.ndarray, strata: np.ndarray, rng, n: int = PERMUTATIONS):
    obs = lift_stats(y, pred)
    idx = [np.flatnonzero(strata == s) for s in np.unique(strata)]
    base = y.mean()
    count = 0
    for _ in range(n):
        yp = y.copy()
        for ix in idx:
            if len(ix) > 1:
                yp[ix] = y[rng.permutation(ix)]
        if pred.any() and base > 0 and yp[pred].mean() / base >= obs - 1e-12:
            count += 1
    return obs, (1 + count) / (1 + n)


def bootstrap_ci(y, pred, rng, n: int = BOOTSTRAP):
    vals = []
    for _ in range(n):
        ix = rng.integers(0, len(y), len(y))
        v = lift_stats(y[ix], pred[ix])
        if not math.isnan(v):
            vals.append(v)
    return (float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))) if vals else (float("nan"),) * 2


def power_two_props(p0: float, n1: int, n0: int, delta: float = LIFT_POINTS, alpha: float = ALPHA_RULE) -> float:
    """Power of a two-sided two-proportion z test to detect p1 = p0 + delta."""
    from scipy.stats import norm
    if n1 == 0 or n0 == 0:
        return 0.0
    p1 = min(max(p0 + delta, 1e-9), 1 - 1e-9)
    p0 = min(max(p0, 1e-9), 1 - 1e-9)
    pbar = (n1 * p1 + n0 * p0) / (n1 + n0)
    se0 = math.sqrt(pbar * (1 - pbar) * (1 / n1 + 1 / n0))
    se1 = math.sqrt(p1 * (1 - p1) / n1 + p0 * (1 - p0) / n0)
    z = norm.ppf(1 - alpha / 2)
    return float(norm.sf((z * se0 - abs(p1 - p0)) / se1))


def delong(y: np.ndarray, a: np.ndarray, b: np.ndarray) -> dict:
    """DeLong's test for two correlated AUCs on the same cases."""
    from scipy.stats import norm
    pos, neg = y == 1, y == 0
    m, n = pos.sum(), neg.sum()
    if m < 2 or n < 2:
        return {"auc_a": float("nan"), "auc_b": float("nan"), "z": float("nan"), "p": float("nan")}

    def comps(s):
        X, Y = s[pos], s[neg]
        v10 = np.array([((x > Y).sum() + 0.5 * (x == Y).sum()) / n for x in X])
        v01 = np.array([((X > yv).sum() + 0.5 * (X == yv).sum()) / m for yv in Y])
        return v10.mean(), v10, v01
    aa, a10, a01 = comps(a)
    ab, b10, b01 = comps(b)
    s10 = np.cov(np.vstack([a10, b10]))
    s01 = np.cov(np.vstack([a01, b01]))
    var = (s10[0, 0] + s10[1, 1] - 2 * s10[0, 1]) / m + (s01[0, 0] + s01[1, 1] - 2 * s01[0, 1]) / n
    z = (ab - aa) / math.sqrt(var) if var > 0 else float("nan")
    return {"auc_a": float(aa), "auc_b": float(ab), "z": float(z), "p": float(2 * norm.sf(abs(z))) if var > 0 else float("nan")}


def _design(rows: list[dict], with_terms: list[str] | None) -> np.ndarray:
    cols = []
    ages = np.array([r["censor"] for r in rows], dtype=float)
    cols.append((ages - ages.mean()) / (ages.std() or 1))
    for key in ("sex", "region"):
        levels = sorted({r[key] for r in rows})[1:]
        cols += [np.array([r[key] == lv for r in rows], dtype=float) for lv in levels]
    era = np.array([r["decade"] for r in rows], dtype=float)
    cols.append((era - era.mean()) / (era.std() or 1))
    for t in with_terms or []:
        v = np.array([r["terms"].get(t, 0.0) for r in rows], dtype=float)
        cols.append((v - v.mean()) / (v.std() or 1))
    return np.column_stack([np.ones(len(rows))] + cols)


def nested(rows: list[dict], fold: np.ndarray) -> dict:
    import statsmodels.api as sm
    from scipy.stats import chi2
    y = np.array([r["case"] for r in rows], dtype=float)
    terms = sorted({t for r in rows for t in r["terms"]})
    terms = [t for t in terms if np.std([r["terms"].get(t, 0.0) for r in rows]) > 0]
    X0, X1 = _design(rows, None), _design(rows, terms)
    try:
        m0 = sm.Logit(y, X0).fit(disp=0, maxiter=200)
        m1 = sm.Logit(y, X1).fit(disp=0, maxiter=200)
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}
    lr = 2 * (m1.llf - m0.llf)
    df = X1.shape[1] - X0.shape[1]
    oof0, oof1 = np.zeros(len(y)), np.zeros(len(y))
    for f in np.unique(fold):
        tr, te = fold != f, fold == f
        try:
            oof0[te] = sm.Logit(y[tr], X0[tr]).fit(disp=0, maxiter=200).predict(X0[te])
            oof1[te] = sm.Logit(y[tr], X1[tr]).fit(disp=0, maxiter=200).predict(X1[te])
        except Exception:
            oof0[te], oof1[te] = np.nan, np.nan
    ok = ~np.isnan(oof0) & ~np.isnan(oof1)
    d = delong(y[ok].astype(int), oof0[ok], oof1[ok])
    return {"terms": terms, "lr": float(lr), "df": int(df), "p_lr": float(chi2.sf(lr, df)) if df else float("nan"),
            "auc_covariates": d["auc_a"], "auc_with_engine": d["auc_b"], "delong_z": d["z"], "delong_p": d["p"],
            "oof_n": int(ok.sum())}


def hazard(rows: list[dict], rng, shifts: int = SHIFTS) -> dict:
    """Discrete-time hazard by person-year: Mantel-Haenszel rate ratio of active against inactive
    years (strata: 5-year age bins), its logistic estimate, and coverage-matched random windows."""
    import statsmodels.api as sm
    n = len(rows)
    L = np.array([int(min(MAX_AGE, math.floor(r["age"])) + 1) for r in rows])
    ev_year = np.array([int(math.floor(r["age"])) if r["case"] else -1 for r in rows])
    act = np.zeros((n, MAX_AGE + 1), dtype=np.int8)
    for i, r in enumerate(rows):
        for a, b in r["active"]:
            for yv in range(max(0, int(math.floor(a))), min(MAX_AGE, int(math.ceil(b)))):
                cover = min(b, yv + 1) - max(a, yv)
                if cover >= 0.5:
                    act[i, yv] = 1
    years = np.arange(MAX_AGE + 1)
    at_risk = years[None, :] < L[:, None]
    event = years[None, :] == ev_year[:, None]
    agebin = np.minimum(years // 5, 20)

    def mh(a_mat):
        num = den = 0.0
        for b in range(21):
            cols = agebin == b
            r = at_risk[:, cols]
            e = event[:, cols]
            x = a_mat[:, cols].astype(bool)
            t1, t0 = (r & x).sum(), (r & ~x).sum()
            d1, d0 = (e & x & r).sum(), (e & ~x & r).sum()
            t = t1 + t0
            if t == 0:
                continue
            num += d1 * t0 / t
            den += d0 * t1 / t
        return num / den if den > 0 else float("nan")
    obs = mh(act)
    coverage = float((act.astype(bool) & at_risk).sum() / at_risk.sum()) if at_risk.sum() else 0.0
    null = []
    idx = np.arange(MAX_AGE + 1)[None, :]
    for _ in range(shifts):
        off = rng.integers(0, np.maximum(L, 1))
        shifted = act[np.arange(n)[:, None], (idx + off[:, None]) % np.maximum(L, 1)[:, None]]
        null.append(mh(shifted))
    null = np.array([x for x in null if not math.isnan(x)])
    p = float((1 + (null >= obs - 1e-12).sum()) / (1 + len(null))) if len(null) and not math.isnan(obs) else float("nan")
    # The logistic discrete-time hazard on the aggregated person-years (age bin x activation).
    cells = []
    for b in range(21):
        cols = agebin == b
        r, e, x = at_risk[:, cols], event[:, cols], act[:, cols].astype(bool)
        for flag in (0, 1):
            m = x if flag else ~x
            t, d = (r & m).sum(), (e & m & r).sum()
            if t:
                cells.append((b, flag, d, t))
    est = {}
    if cells and sum(c[2] for c in cells):
        bins = sorted({c[0] for c in cells})
        X = np.array([[1.0, c[1]] + [float(c[0] == bb) for bb in bins[1:]] for c in cells])
        yv = np.array([[c[2], c[3] - c[2]] for c in cells], dtype=float)
        try:
            fit = sm.GLM(yv, X, family=sm.families.Binomial()).fit()
            lo, hi = fit.conf_int()[1]
            est = {"log_odds": float(fit.params[1]), "ci": [float(lo), float(hi)], "p": float(fit.pvalues[1])}
        except Exception as e:
            est = {"error": str(e)}
    return {"rate_ratio": float(obs), "p_random_windows": p, "shifts": int(len(null)), "coverage": coverage,
            "person_years": int(at_risk.sum()), "events": int((event & at_risk).sum()), "logistic": est}


def calibration(score: np.ndarray, y: np.ndarray, fold: np.ndarray, test_score=None, test_y=None) -> dict:
    from sklearn.isotonic import IsotonicRegression
    oof = np.zeros(len(y))
    for f in np.unique(fold):
        tr, te = fold != f, fold == f
        if len(np.unique(y[tr])) < 2:
            oof[te] = y[tr].mean() if tr.any() else 0.0
            continue
        iso = IsotonicRegression(out_of_bounds="clip").fit(score[tr], y[tr])
        oof[te] = iso.predict(score[te])

    def ece(pred, yy):
        bins = np.minimum((pred * 10).astype(int), 9)
        tot, rows = 0.0, []
        for b in range(10):
            m = bins == b
            if m.any():
                tot += m.sum() * abs(pred[m].mean() - yy[m].mean())
                rows.append({"bin": b, "n": int(m.sum()), "positives": int(yy[m].sum())})
        return tot / len(yy), rows
    e_dev, bins_dev = ece(oof, y)
    out = {"ece_dev": float(e_dev), "bins_dev": bins_dev,
           "gate_dev": all(b["positives"] >= BIN_GATE for b in bins_dev), "evaluated_on": "development folds"}
    if test_score is not None and len(test_y):
        iso = IsotonicRegression(out_of_bounds="clip").fit(score, y)
        e_t, bins_t = ece(iso.predict(test_score), test_y)
        out |= {"ece_sequestered": float(e_t), "bins_sequestered": bins_t,
                "gate": all(b["positives"] >= BIN_GATE for b in bins_t), "evaluated_on": "the sequestered cohort"}
    else:
        out["gate"] = None
    return out


# --- the run --------------------------------------------------------------------------------------

def area_rows(cohort: Cohort, area: str, ids: set[str]) -> list[dict]:
    from jyotish.outcomes import area_events, outcome_map
    mapped = area_events(area)
    thr = outcome_map()["occupation_isei_threshold"]
    out = []
    for s in cohort.subjects:
        if s["id"] not in ids:
            continue
        o = outcome(cohort.events.get(s["id"], []), mapped, thr)
        if o is None:
            continue
        f = cohort.features[s["chart_id"]]["areas"][area]
        abstain = f["score"] is None or f["tier"] == "needs two charts" or s["accuracy"] in ABSTAIN_ACCURACY
        out.append(dict(o, id=s["id"], sex=s["sex"], region=s["region"], decade=s["decade"], tier=f["tier"],
                        score=f["score"], terms=f["terms"], active=f["active"], abstain=abstain, stratum=stratum(s)))
    return out


def hashes(seq_meta: dict) -> dict:
    from jyotish.scoring import WEIGHTS
    rules = hashlib.sha256()
    for p in sorted((ROOT / "rules").glob("*.yaml")):
        rules.update(p.name.encode() + p.read_bytes())
    weights = hashlib.sha256(json.dumps(WEIGHTS, sort_keys=True, default=str).encode())
    for p in sorted((ROOT / "src" / "jyotish" / "data").glob("family_*.json")):
        weights.update(p.read_bytes())
    split = {"salt_sha256": hashlib.sha256(seq_meta["salt"].encode()).hexdigest(), "fraction": FRACTION, "k": K,
             "groups": "household and birthplace cluster, connected components",
             "strata": "birth decade x sex x region", "sequestered_file_sha256": seq_meta["file_sha256"]}
    return {"rule_set": rules.hexdigest(), "weight_set": weights.hexdigest(),
            "split_definition": hashlib.sha256(json.dumps(split, sort_keys=True).encode()).hexdigest(),
            "analysis_code": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "split": split}


def run(cohort: Cohort, sequestered_file: Path = SEQUESTERED, score_sequestered: bool = False, seed: int = 0,
        permutations: int = PERMUTATIONS, bootstrap: int = BOOTSTRAP, shifts: int = SHIFTS) -> dict:
    from jyotish.outcomes import area_events, outcome_map, rule_testability
    rng = np.random.default_rng(seed)
    ids = [s["id"] for s in cohort.subjects]
    seq, seq_meta = sequester(ids, sequestered_file)
    dev_subjects = [s for s in cohort.subjects if s["id"] not in seq]
    dev = {s["id"] for s in dev_subjects}
    fold_of = dict(zip([s["id"] for s in dev_subjects], folds(dev_subjects, seed))) if len(dev_subjects) >= K else {}
    res = {"date": date.today().isoformat(), "synthetic": cohort.synthetic, "n_subjects": len(ids),
           "n_sequestered": len(seq), "n_development": len(dev), "folds": int(len(set(fold_of.values()))),
           "areas": {}, "rules": {}, "hashes": hashes(seq_meta), "score_sequestered": score_sequestered}
    gid = dict(zip([s["id"] for s in dev_subjects], groups_of(dev_subjects)))
    straddle = sum(1 for g in set(gid.values()) if len({fold_of[i] for i in gid if gid[i] == g}) > 1)
    res["groups_straddling_folds"] = straddle
    pvals = {}
    for area in outcome_map()["areas"]:
        if not area_events(area):
            res["areas"][area] = {"status": "not_testable_yet", "why": "no measured outcome is mapped to this area"}
            continue
        rows = area_rows(cohort, area, dev)
        n_data = len(rows)
        rows_c = [r for r in rows if not r["abstain"]]
        cov = len(rows_c) / n_data if n_data else 0.0
        a = {"n_with_outcome": n_data, "coverage": cov, "n": len(rows_c), "events": area_events(area)}
        if len(rows_c) < 20 or len({r["case"] for r in rows_c}) < 2:
            a |= {"status": "insufficient", "why": "fewer than 20 predicted charts, or no variation in the outcome"}
            res["areas"][area] = a
            continue
        y = np.array([r["case"] for r in rows_c], dtype=float)
        pred = np.array([r["tier"] in POSITIVE_TIERS for r in rows_c])
        strata = np.array([r["stratum"] for r in rows_c])
        lift, p = permutation_lift(y, pred, strata, rng, permutations)
        lo, hi = bootstrap_ci(y, pred, rng, bootstrap)
        a |= {"status": "tested", "base_rate": float(y.mean()), "n_predicted": int(pred.sum()),
              "rate_predicted": float(y[pred].mean()) if pred.any() else None,
              "rate_other": float(y[~pred].mean()) if (~pred).any() else None,
              "lift": lift, "lift_ci": [lo, hi], "p_permutation": p, "permutations": permutations,
              "power_5pt": power_two_props(float(y[~pred].mean()) if (~pred).any() else float(y.mean()),
                                           int(pred.sum()), int((~pred).sum()))}
        a["power_5pt_alpha05"] = power_two_props(a["rate_other"] or a["base_rate"], a["n_predicted"],
                                                 a["n"] - a["n_predicted"], alpha=0.05)
        fold = np.array([fold_of[r["id"]] for r in rows_c])
        a["nested"] = nested(rows_c, fold)
        a["timing"] = hazard(rows_c, rng, shifts)
        score = np.array([r["score"] for r in rows_c], dtype=float)
        test = None
        if score_sequestered:
            trows = [r for r in area_rows(cohort, area, seq) if not r["abstain"]]
            test = (np.array([r["score"] for r in trows], dtype=float), np.array([r["case"] for r in trows], dtype=float))
        a["calibration"] = calibration(score, y, fold, *(test or (None, None)))
        a["probability_language"] = bool(a["calibration"]["gate"]) if a["calibration"]["gate"] is not None else False
        pvals[area] = p
        res["areas"][area] = a
    for area, x in bh(pvals).items():
        res["areas"][area] |= x
    res["rules"] = rule_effects(cohort, dev, rule_testability())
    return res


def rule_effects(cohort: Cohort, dev: set[str], testability: dict) -> dict:
    from scipy.stats import norm
    from jyotish.outcomes import outcome_map
    thr = outcome_map()["occupation_isei_threshold"]
    subs = [s for s in cohort.subjects if s["id"] in dev]
    out = {}
    for rid, t in testability.items():
        if t["status"] != "testable":
            out[rid] = {"status": "not_testable_yet", "why": "its outcomes map to nothing measured"}
            continue
        ys, fired = [], []
        for s in subs:
            o = outcome(cohort.events.get(s["id"], []), t["events"], thr)
            if o is None:
                continue
            ys.append(o["case"])
            fired.append(rid in cohort.features[s["chart_id"]]["rules"])
        y, f = np.array(ys, dtype=float), np.array(fired, dtype=bool)
        n1, n0 = int(f.sum()), int((~f).sum())
        if n1 < 5 or n0 < 5:
            out[rid] = {"status": "not_testable_yet", "why": f"fires on {n1} of {len(y)} charts with data", "n_fired": n1}
            continue
        p1, p0 = y[f].mean(), y[~f].mean()
        se = math.sqrt(p1 * (1 - p1) / n1 + p0 * (1 - p0) / n0) or 1e-9
        d = p1 - p0
        pv = float(2 * norm.sf(abs(d) / se))
        out[rid] = {"n_fired": n1, "n": len(y), "effect": float(d), "ci": [float(d - 1.96 * se), float(d + 1.96 * se)],
                    "p": pv, "power_5pt": power_two_props(p0, n1, n0)}
    # Hundreds of rules are tested at once: an effect counts after Benjamini-Hochberg across them.
    tested = {rid: r["p"] for rid, r in out.items() if "p" in r}
    for rid, x in bh(tested, q=ALPHA_RULE).items():
        r = out[rid]
        r["p_adj"] = x["p_adj"]
        r["status"] = ("effect on development data" if x["survives"] else
                       "classical_rejected (recommended: powered null)" if r["power_5pt"] >= 0.8 else
                       "not_testable_yet (under-powered)")
    return out


# --- the report -----------------------------------------------------------------------------------

def _f(x, nd=3):
    return "–" if x is None or (isinstance(x, float) and math.isnan(x)) else (f"{x:.{nd}f}" if isinstance(x, float) else str(x))


def report(res: dict, label: str = "") -> str:
    syn = "Synthetic — " if res["synthetic"] else ""
    h = res["hashes"]
    L = [f"# {syn}Validation{(' — ' + label) if label else ''}", "",
         f"Run {res['date']} by `scripts/validate.py`{' on a synthetic cohort: these numbers prove the pipeline, not the engine' if res['synthetic'] else ''}. "
         f"{res['n_subjects']} subjects: {res['n_development']} development, {res['n_sequestered']} sequestered "
         f"({'scored in this run' if res['score_sequestered'] else 'not scored in this run'}); {res['folds']} grouped folds, "
         f"{res['groups_straddling_folds']} groups straddling a fold.", "",
         f"## {syn}Pre-registration hashes (test 10)", "",
         f"- rule set `{h['rule_set']}`", f"- weight set `{h['weight_set']}`",
         f"- split definition `{h['split_definition']}` ({json.dumps(h['split'])})", f"- analysis code `{h['analysis_code']}`", "",
         f"## {syn}Lift of the tier, per area (tests 2 and 5)", "",
         "Positive prediction: tier strong or moderate. n is the predicted charts with the outcome recorded; coverage "
         "is their share of all charts with it (the rest abstain).", "",
         "| area | n | coverage | base rate | lift | 95% CI | p (permutation) | BH p | survives | power (5 pt, α 0.01) |",
         "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for area, a in res["areas"].items():
        if a.get("status") != "tested":
            L.append(f"| {area} | {a.get('n', 0)} | {_f(a.get('coverage'))} | – | – | – | – | – | {a['status']} | – |")
            continue
        L.append(f"| {area} | {a['n']} | {_f(a['coverage'])} | {_f(a['base_rate'])} | {_f(a['lift'])} | "
                 f"{_f(a['lift_ci'][0])}–{_f(a['lift_ci'][1])} | {_f(a['p_permutation'], 4)} | {_f(a['p_adj'], 4)} | "
                 f"{'yes' if a['survives'] else 'no'} | {_f(a['power_5pt'])} |")
    L += ["", f"## {syn}Incremental validity: nested models (test 3)", "",
          "| area | n | coverage | engine terms | LR | df | p (LR) | AUC covariates | AUC + engine | DeLong p |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for area, a in res["areas"].items():
        if a.get("status") == "tested" and "lr" in a["nested"]:
            nm = a["nested"]
            L.append(f"| {area} | {a['n']} | {_f(a['coverage'])} | {len(nm['terms'])} | {_f(nm['lr'], 2)} | {nm['df']} | "
                     f"{_f(nm['p_lr'], 4)} | {_f(nm['auc_covariates'])} | {_f(nm['auc_with_engine'])} | {_f(nm['delong_p'], 4)} |")
    L += ["", f"## {syn}Timing as a discrete-time hazard (test 4)", "",
          "Activation: the year mostly inside an antardasha the engine's window gate counts as relevant to the area. "
          "Rate ratio: Mantel-Haenszel over 5-year age bins; p against coverage-matched random windows.", "",
          "| area | n | coverage | person-years | events | active share | rate ratio | p (random windows) | log-odds (95% CI) |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for area, a in res["areas"].items():
        if a.get("status") == "tested":
            t = a["timing"]
            lg = t["logistic"]
            L.append(f"| {area} | {a['n']} | {_f(a['coverage'])} | {t['person_years']} | {t['events']} | {_f(t['coverage'])} | "
                     f"{_f(t['rate_ratio'])} | {_f(t['p_random_windows'], 4)} | "
                     f"{_f(lg.get('log_odds'))} ({_f((lg.get('ci') or [None])[0])}, {_f((lg.get('ci') or [None, None])[1])}) |")
    L += ["", f"## {syn}Calibration (test 7)", "",
          f"Isotonic map from the area score to the event rate. Probability language needs ≥ {BIN_GATE} positives in every "
          "bin, on the sequestered cohort.", "",
          "| area | n | coverage | ECE (development folds) | ECE (sequestered) | bins | smallest bin positives | probability language |",
          "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for area, a in res["areas"].items():
        if a.get("status") == "tested":
            c = a["calibration"]
            bins = c.get("bins_sequestered") or c["bins_dev"]
            L.append(f"| {area} | {a['n']} | {_f(a['coverage'])} | {_f(c['ece_dev'])} | {_f(c.get('ece_sequestered'))} | "
                     f"{len(bins)} | {min(b['positives'] for b in bins) if bins else '–'} | "
                     f"{'allowed' if a['probability_language'] else 'not allowed'} |")
    L += ["", f"## {syn}Power at the current n (pre-registration table)", "",
          "| area | n | coverage | predicted | power, 5-point lift, α 0.01 | power, 5-point lift, α 0.05 |",
          "| --- | --- | --- | --- | --- | --- |"]
    for area, a in res["areas"].items():
        if a.get("status") == "tested":
            L.append(f"| {area} | {a['n']} | {_f(a['coverage'])} | {a['n_predicted']} | {_f(a['power_5pt'])} | {_f(a['power_5pt_alpha05'])} |")
    counts: dict[str, int] = {}
    for r in res["rules"].values():
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    L += ["", f"## {syn}Per-rule effects (test 6)", "",
          "Effect: event rate where the rule fires minus where it does not, on the development set; an effect "
          "counts after Benjamini-Hochberg across the rules tested (q 0.01). classical_rejected is a recommendation "
          "for a powered null (power ≥ 0.8 for a 5-point lift), never applied by this script.", "",
          *[f"- {k}: {v} rules" for k, v in sorted(counts.items())], "",
          "| rule | n | fired | effect | 95% CI | p | power (5 pt, α 0.01) | status |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for rid, r in sorted(res["rules"].items()):
        if "effect" in r:
            L.append(f"| `{rid}` | {r['n']} | {r['n_fired']} | {_f(r['effect'])} | {_f(r['ci'][0])}–{_f(r['ci'][1])} | "
                     f"{_f(r['p'], 4)} | {_f(r['power_5pt'])} | {r['status']} |")
    L += ["", f"## {syn}Not tested", "", "Areas with no mapped outcome, or too little data:", ""]
    L += [f"- {area}: {a['status']} ({a.get('why', '')})" for area, a in res["areas"].items() if a.get("status") != "tested"]
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--database", default=os.environ.get("JYOTISH_DATABASE_URL", "sqlite:///jyotish.db"))
    ap.add_argument("--out", default=str(DOC))
    ap.add_argument("--sequestered", default=str(SEQUESTERED))
    ap.add_argument("--score-sequestered", action="store_true", help="score the sequestered cohort (once per release)")
    ap.add_argument("--synthetic", action="store_true", help="the cohort is synthetic: every heading says so")
    ap.add_argument("--json", help="also write the results as JSON")
    a = ap.parse_args(argv)
    cohort = load_cohort(a.database, synthetic=a.synthetic)
    res = run(cohort, Path(a.sequestered), a.score_sequestered)
    Path(a.out).write_text(report(res))
    if a.json:
        Path(a.json).write_text(json.dumps(res, indent=1, default=str))
    tested = [x for x in res["areas"].values() if x.get("status") == "tested"]
    print(f"{res['n_subjects']} subjects; {len(tested)} areas tested, {sum(x['survives'] for x in tested)} survive BH -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
