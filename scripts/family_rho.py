"""Over a population of random charts, measure (1) each signal family's mean correlation
with the other families (SPEC Layer 5, "weighted by 1 - rho"), written to
src/jyotish/data/family_rho.json, and (2) each life area's distribution of S, written as
percentiles to src/jyotish/data/area_percentiles.json (an area is "not emphasised" below
its 40th percentile).

Charts are real moments and places: UTC uniform over 1900-2050, latitude uniform in
[-60, 60] (sunrise exists), longitude uniform in [-180, 180], Lahiri, true node, whole
sign, default settings. Each (chart, life area) row gives every family's vote in
{-1, 0, +1} or "not applicable". rho(f, g) is the Pearson correlation of the two
families' votes over the rows where both apply; rho_f is the mean over g != f. A pair
with no variance or no shared rows is left out of the mean.

Run:  .venv/bin/python scripts/family_rho.py [n_charts] [seed]"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

from jyotish.chart import compute
import jyotish.scoring
from jyotish.models import Meta
from jyotish.scoring import AREAS, FAMILIES, table_path

jyotish.scoring.POPULATION_RUN = True   # votes and S only; the tables being made are not read

DATA = Path(__file__).resolve().parents[1] / "src" / "jyotish" / "data"
# The tables are per (varga_term, kp_vote): written for the Meta defaults.
META = Meta()
OUT = table_path(DATA / "family_rho.json", META.varga_term, META.kp_vote)
PCT = table_path(DATA / "area_percentiles.json", META.varga_term, META.kp_vote)


def main(n: int = 10_000, seed: int = 20261021) -> None:
    rng = np.random.default_rng(seed)
    start = datetime(1900, 1, 1, tzinfo=timezone.utc)
    span = (datetime(2050, 1, 1, tzinfo=timezone.utc) - start).total_seconds()
    rows = []
    scores = {a: [] for a in AREAS}
    t0 = time.perf_counter()
    for i in range(n):
        utc = start + timedelta(seconds=float(rng.uniform(0, span)))
        chart = compute(utc, float(rng.uniform(-60, 60)), float(rng.uniform(-180, 180)))
        for area in AREAS:
            scores[area].append(chart.scored.areas[area].score_classical)
            v = chart.scored.areas[area].votes
            rows.append([np.nan if v[f] is None else v[f] for f in FAMILIES])
        if (i + 1) % 1000 == 0:
            print(f"{i + 1} charts, {time.perf_counter() - t0:.0f} s", flush=True)
    X = np.array(rows, dtype=float)
    pair = {}
    for a, f in enumerate(FAMILIES):
        for b, g in enumerate(FAMILIES):
            if b <= a:
                continue
            m = ~np.isnan(X[:, a]) & ~np.isnan(X[:, b])
            x, y = X[m, a], X[m, b]
            if m.sum() < 30 or x.std() == 0 or y.std() == 0:
                continue
            pair[f"{f}|{g}"] = float(np.corrcoef(x, y)[0, 1])
    rho = {}
    for f in FAMILIES:
        vals = [r for k, r in pair.items() if f in k.split("|")]
        rho[f] = float(np.mean(vals)) if vals else 0.0
    applicable = {f: float((~np.isnan(X[:, i])).mean()) for i, f in enumerate(FAMILIES)}
    OUT.write_text(json.dumps({
        "description": "Mean correlation of each Layer 5 signal family with the others "
                       "(scripts/family_rho.py). Confluence weights are 1 - rho.",
        "n_charts": n, "seed": seed, "rows": int(X.shape[0]),
        "settings": f"Lahiri, true node, whole sign, default Meta (varga_term {META.varga_term}, kp_vote {META.kp_vote}); "
                    "UTC 1900-2050, lat -60..60",
        "rho": rho, "pairwise": pair, "applicable_share": applicable,
    }, indent=2) + "\n")
    PCT.write_text(json.dumps({
        "description": "Percentiles of each life area's S_area over the population run "
                       "(scripts/family_rho.py). Not emphasised: S below p40.",
        "n_charts": n, "seed": seed,
        "settings": f"Lahiri, true node, whole sign, default Meta (varga_term {META.varga_term}, kp_vote {META.kp_vote}); "
                    "UTC 1900-2050, lat -60..60",
        "percentiles": {a: {f"p{q}": float(np.percentile(v, q)) for q in (10, 25, 40, 50, 75, 90)}
                        for a, v in scores.items()},
    }, indent=2) + "\n")
    print(json.dumps(rho, indent=2))


if __name__ == "__main__":
    main(*(int(a) for a in sys.argv[1:3]))
