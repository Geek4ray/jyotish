"""Chart features for cohort analysis (scripts/validate.py, scripts/synthetic_cohort.py): per area
the engine's score, tier, terms and window activation, and the rules that fired. In the package so
a process pool can import it; it uses the engine only, none of the validation dependencies."""

from __future__ import annotations

import os
from concurrent.futures import ProcessPoolExecutor


def chart_features(birth: dict) -> dict:
    """Everything the tests read from one chart: per area its score, tier and terms, and per area
    the ages at which the engine's windows are active; and the rules that fired. Top level, so a
    process pool can run it."""
    from jyotish.chart import compute
    from jyotish.constants import SIGN_LORD
    from jyotish.scoring import AREAS, _karakas, _View
    from jyotish.service import birth_utc
    from jyotish.timing import _relevant, activation_set
    utc, _ = birth_utc(birth["date"], birth["time"], birth["tz"])
    c = compute(utc, float(birth["lat"]), float(birth["lon"]), true_node=(birth.get("node") or "mean") == "true",
                dasha_levels=2)
    jd0 = c.meta.jd
    out = {"areas": {}, "rules": sorted({f.id for f in c.fired_rules})}
    antars = [p for p in c.dashas.get("vimshottari", []) if len(p.lords) == 2]
    view = _View(c)
    for name, a in c.scored.areas.items():
        spec = AREAS.get(name)
        active = []
        if spec and spec.get("houses"):
            base = c.lagnas.asc_sign
            signs = {(base + h - 1) % 12 for h in spec["houses"]}
            karakas = set(_karakas(view, spec["karakas"]))
            for p in antars:
                lord = p.lords[-1]
                if any(_relevant(c, q, base, signs, karakas) for q in [lord] + activation_set(c, lord)):
                    active.append(((p.start_jd - jd0) / 365.25, (p.end_jd - jd0) / 365.25))
        out["areas"][name] = {"score": a.score_classical, "tier": a.tier, "confidence": a.confidence,
                              "terms": dict(sorted(a.terms.items())), "active": active}
    return out


def features_for(births: dict[str, dict], workers: int | None = None) -> dict[str, dict]:
    """chart key -> features, computed in a process pool."""
    keys = list(births)
    workers = workers or min(8, os.cpu_count() or 1)
    if workers <= 1 or len(keys) < 50:
        return {k: chart_features(births[k]) for k in keys}
    with ProcessPoolExecutor(max_workers=workers) as ex:
        return dict(zip(keys, ex.map(chart_features, [births[k] for k in keys], chunksize=32)))


