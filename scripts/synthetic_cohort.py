"""Synthetic cohorts for scripts/validate.py, so the validation pipeline is proven before real data.

    .venv/bin/python scripts/synthetic_cohort.py --n 2000 --mode planted --database sqlite:////tmp/syn.db
    .venv/bin/python scripts/synthetic_cohort.py --n 2000 --mode null    --database sqlite:////tmp/syn0.db

N random births (1940-2000, latitude 60 S to 60 N, any longitude and time; synthetic, no one's data)
go through the real capture path: a consent per subject, and one sheet row per mapped event type,
imported by outcomes.import_rows. Events are drawn one of two ways:
  planted  each tested area's event has probability logistic(logit(base) + beta * z), where z is
           the engine's own area score standardised over the cohort and beta = ln(odds ratio per
           SD). A case's event age falls in the engine's active window years with twice the weight of
           other years (a planted timing effect, hazard ratio about 2). validate.py should recover
           both with roughly the power its table predicts.
  null     events independent of the chart, at the base rate, with uniform ages: validate.py should
           find no area surviving Benjamini-Hochberg.
Sex, region, household and birthplace cluster are random (households of one to three).
`expected()` gives, per area, the planted rates for predicted and other charts and the implied
power of the lift test, which the harness compares with what validate.py recovers."""

from __future__ import annotations

import argparse
import math
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

TODAY = date(2026, 10, 22)
BASE_RATE = 0.3
ODDS_RATIO = 1.2              # per SD of the area score, in planted mode: mid power at 2,000, near 1 at 20,000
TIMING_WEIGHT = 2.0           # an event year inside an active window is this much likelier, in planted mode
REGIONS = ["north", "south", "east", "west"]


def births(n: int, seed: int) -> list[dict]:
    rng = np.random.default_rng(seed)
    t0 = datetime(1940, 1, 1, tzinfo=timezone.utc)
    span = (datetime(2001, 1, 1, tzinfo=timezone.utc) - t0).total_seconds()
    out, household = [], 0
    for i in range(n):
        utc = t0 + timedelta(seconds=float(rng.uniform(0, span)))
        if i == 0 or rng.random() > 0.3:              # about a third share a household with the one before
            household += 1
        out.append({"subject_id": f"SYN-{i + 1:06d}", "date": utc.strftime("%Y-%m-%d"), "time": utc.strftime("%H:%M:%S"),
                    "tz": "UTC", "lat": round(float(rng.uniform(-60, 60)), 4), "lon": round(float(rng.uniform(-180, 180)), 4),
                    "node": "mean", "sex": "female" if rng.random() < 0.5 else "male",
                    "region": REGIONS[int(rng.integers(0, 4))], "household_key": f"H-{household:06d}",
                    "birthplace_cluster": f"BP-{int(rng.integers(0, max(2, n // 4))):05d}"})
    return out


def _age(b: dict) -> float:
    return (TODAY - date.fromisoformat(b["date"])).days / 365.25


def tested_areas() -> list[str]:
    from jyotish.outcomes import area_events, outcome_map
    return [a for a in outcome_map()["areas"] if area_events(a)]


def make(n: int, mode: str, database_url: str, seed: int = 0, odds_ratio: float = ODDS_RATIO,
         timing_weight: float = TIMING_WEIGHT) -> tuple[dict, dict]:
    """Build the cohort in `database_url`; returns (features by chart id, the planted truth)."""
    import validate as V
    from jyotish.outcomes import add_consent, area_events, import_rows, sessionmaker_for
    from jyotish.service import BirthInput, assess_kwargs
    from jyotish.cache import birth_key
    rng = np.random.default_rng(seed + 1)
    bs = births(n, seed)
    keys = {}
    for b in bs:
        bi = BirthInput(date=b["date"], time=b["time"], tz=b["tz"], lat=b["lat"], lon=b["lon"], node="mean")
        utc, _ = assess_kwargs(bi)
        keys[b["subject_id"]] = birth_key(utc, bi.lat, bi.lon)
    feats = V.features_for({keys[b["subject_id"]]: b for b in bs}, until=TODAY.isoformat())
    beta = math.log(odds_ratio) if mode == "planted" else 0.0
    truth = {"mode": mode, "n": n, "odds_ratio_per_sd": odds_ratio if mode == "planted" else 1.0, "base_rate": BASE_RATE,
             "timing_weight": timing_weight if mode == "planted" else 1.0, "areas": {}}
    probs = {}
    for area in tested_areas():
        s = np.array([feats[keys[b["subject_id"]]]["areas"][area]["score"] or 0.0 for b in bs], dtype=float)
        z = (s - s.mean()) / (s.std() or 1.0)
        logit = math.log(BASE_RATE / (1 - BASE_RATE)) + beta * z
        probs[area] = 1 / (1 + np.exp(-logit))
    # One event row per (subject, event type). Areas share event types (occupation is intellect's,
    # career's and reputation's), so each type is drawn once, from the score of the first tested area
    # that maps it, its owner; an area that owns none of its events has no planted effect of its own.
    event_area = {}
    for area in tested_areas():
        for e in area_events(area):
            event_area.setdefault(e, area)
    for area in tested_areas():
        # The planted rate of this area's outcome: any of its events, each from its owner's score.
        p_any = 1 - np.prod([1 - probs[event_area[e]] for e in area_events(area)], axis=0)
        pred = np.array([feats[keys[b["subject_id"]]]["areas"][area]["tier"] in V.POSITIVE_TIERS for b in bs])
        p1 = float(p_any[pred].mean()) if pred.any() else float(p_any.mean())
        p0 = float(p_any[~pred].mean()) if (~pred).any() else float(p_any.mean())
        owns = [e for e in area_events(area) if event_area[e] == area]
        truth["areas"][area] = {"rate_predicted": p1, "rate_other": p0, "n_predicted": int(pred.sum()),
                                "planted_points": p1 - p0, "owns_events": owns,
                                "planted": mode == "planted" and bool(owns)}
    Session = sessionmaker_for(database_url)
    with Session.begin() as s:
        for i, b in enumerate(bs):
            add_consent(s, f"CON-{b['subject_id']}", b["subject_id"], "synthetic-v1", "new", "synthetic")
    rows = []
    for i, b in enumerate(bs):
        age_now = _age(b)
        f = feats[keys[b["subject_id"]]]
        for etype, area in event_area.items():
            case = rng.random() < probs[area][i]
            row = {"consent_id": f"CON-{b['subject_id']}", "subject_id": b["subject_id"], "date": b["date"],
                   "time": b["time"], "tz": b["tz"], "lat": str(b["lat"]), "lon": str(b["lon"]), "place": "",
                   "node": "mean", "accuracy": "exact", "sex": b["sex"], "region": b["region"], "source": "file",
                   "rectified": "no", "seen_by_astrologer": "no", "household_key": b["household_key"],
                   "birthplace_cluster": b["birthplace_cluster"], "event_type": etype, "age_at_event": "",
                   "censor_age": f"{age_now:.2f}", "isco08": "", "isei": "", "self_report": "no",
                   "entered_at": "2026-10-22T00:00:00+00:00", "reading_shown_at": ""}
            if case:
                lo, hi = 1, int(math.floor(age_now))
                years = np.arange(lo, max(lo + 1, hi))
                w = np.ones(len(years))
                if mode == "planted":
                    act = f["areas"][area]["active"]
                    inside = np.array([any(a <= y + 0.5 < bb for a, bb in act) for y in years])
                    w[inside] = timing_weight
                y = int(rng.choice(years, p=w / w.sum()))
                row["age_at_event"] = f"{min(y + rng.random(), age_now - 0.01):.2f}"
                if etype == "occupation":
                    row |= {"isco08": "2211", "isei": "75"}
            elif etype == "occupation":
                row |= {"age_at_event": f"{min(35.0, age_now - 0.01):.2f}", "isco08": "9112", "isei": "20"}
            rows.append(row)
    with Session.begin() as s:
        res = import_rows(s, rows, entered_by="synthetic", today=TODAY)
    if res.refused:
        raise RuntimeError(f"synthetic rows refused: {res.refused[:3]}")
    return feats, truth


def compare(truth: dict, res: dict) -> dict:
    """What validate.py recovered against what was planted. Predicted power per planted area: the
    lift test's two-proportion power at the planted rate difference, the development n and alpha 0.05."""
    import validate as V
    planted = [a for a, t in truth["areas"].items() if t["planted"] and res["areas"].get(a, {}).get("status") == "tested"]
    tested = [a for a, x in res["areas"].items() if x.get("status") == "tested"]
    per = {}
    for a in planted:
        t, x = truth["areas"][a], res["areas"][a]
        per[a] = {"planted_points": t["planted_points"],
                  "predicted_power": V.power_two_props(x["rate_other"] or x["base_rate"], x["n_predicted"],
                                                       x["n"] - x["n_predicted"], delta=t["planted_points"], alpha=0.05),
                  "recovered": x["p_permutation"] < 0.05, "survives_bh": x["survives"],
                  "timing_recovered": (x["timing"]["p_random_windows"] or 1) < 0.05}
    mean = lambda xs: float(sum(xs) / len(xs)) if xs else float("nan")
    rules = res["rules"].values()
    return {"mode": truth["mode"], "n": truth["n"], "planted_areas": planted, "per_area": per,
            "predicted_power_mean": mean([v["predicted_power"] for v in per.values()]),
            "recovered_share": mean([v["recovered"] for v in per.values()]),
            "survived_bh_share": mean([v["survives_bh"] for v in per.values()]),
            "timing_recovered_share": mean([v["timing_recovered"] for v in per.values()]),
            "areas_surviving_bh": sum(1 for a in tested if res["areas"][a]["survives"]),
            "areas_tested": len(tested),
            "rules_with_effect": sum(1 for r in rules if r.get("status") == "effect on development data"),
            "rules_tested": sum(1 for r in rules if "p" in r)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=2000)
    ap.add_argument("--mode", choices=["planted", "null"], required=True)
    ap.add_argument("--database", required=True)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args(argv)
    if "jyotish.db" in a.database:
        raise SystemExit("refusing to write a synthetic cohort into the real database")
    _, truth = make(a.n, a.mode, a.database, a.seed)
    print(f"{a.n} synthetic subjects ({a.mode}) -> {a.database}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
