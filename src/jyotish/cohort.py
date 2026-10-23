"""Chart features for cohort analysis (scripts/validate.py, scripts/synthetic_cohort.py): per area
the engine's score, tier, confidence, votes, terms and window activation, and the rules that fired.
In the package so a process pool can import it; it uses the engine only, none of the validation
dependencies.

Window activation (SPEC Layer 6 test 4) is the engine's own. The timing join's pieces (timing
.window_pieces, v2.1: the gated Vimshottari antars cut at the slow movers' sign ingresses, each with
joint = 0.6 q + 0.4 t) are computed over the life from birth to `until`, and the active years are
the best third of that life by joint: what the engine answers a "when" question with is its top
windows, so the covariate is a ranking, and a third of the person-years are active for everyone,
which is what the coverage-matched null needs. (The dasha gate alone, which the first version used,
covered nine years in ten: review 2026-10-23, F1.) The slow movers' sign spans do not depend on the
chart, so one sweep per process, 1850 to 2150, serves every chart of a cohort."""

from __future__ import annotations

import os
from concurrent.futures import ProcessPoolExecutor
from datetime import date
from functools import partial

ACTIVE_SHARE = 1.0 / 3.0                      # of the life, by joint, from the top
SWEEP = (date(1850, 1, 1), date(2150, 1, 1))  # the standard sweep of the slow movers
_SLOW: dict[tuple, list[tuple[str, int, float, float]]] = {}


def _jd(d: date) -> float:
    import swisseph as swe
    return swe.julday(d.year, d.month, d.day, 0.0)


def slow_spans(ayanamsa: str, true_node: bool, start_jd: float, end_jd: float) -> list[tuple[str, int, float, float]]:
    """(body, sign, t0, t1) for Saturn, Jupiter, Rahu and Ketu over at least [start, end]: the
    standard sweep when it covers the range, else a sweep of the range; once per process."""
    from .timing import SLOW_MOVERS
    from .transits import Sky, segments
    a, b = _jd(SWEEP[0]), _jd(SWEEP[1])
    if not (a <= start_jd and end_jd <= b):
        a, b = start_jd, end_jd
    key = (ayanamsa, true_node, a, b)
    if key not in _SLOW:
        sky = Sky(ayanamsa, true_node)
        _SLOW[key] = [(body, s, t0, t1) for body in SLOW_MOVERS for s, t0, t1, _ in segments(sky, body, a, b)]
    return _SLOW[key]


def active_windows(pieces: list[dict], start_jd: float, end_jd: float, jd0: float,
                   share: float = ACTIVE_SHARE) -> tuple[list[tuple[float, float]], float]:
    """The active spans in years from birth (`jd0`), and the share of [start, end] they cover: the
    pieces by joint from the top, taken until the next would carry the total past `share` of the
    range (the first is taken whatever its length); adjacent spans merged. Years in no piece (the
    gate shut) are never active."""
    total = end_jd - start_jd
    if not pieces or total <= 0:
        return [], 0.0
    taken, covered = [], 0.0
    for p in sorted(pieces, key=lambda p: (-p["joint"], p["a"])):
        length = p["b"] - p["a"]
        if taken and covered + length > share * total + 1e-9:
            break
        taken.append((p["a"], p["b"]))
        covered += length
    merged: list[list[float]] = []
    for a, b in sorted(taken):
        if merged and abs(merged[-1][1] - a) < 1e-9:
            merged[-1][1] = b
        else:
            merged.append([a, b])
    return [((a - jd0) / 365.25, (b - jd0) / 365.25) for a, b in merged], covered / total


def chart_features(birth: dict, until: str | None = None, stability_samples: int = 0) -> dict:
    """Everything the tests read from one chart: per area its score, tier, confidence, votes and
    terms, and the ages at which the engine's windows are active, from birth to `until` (today
    by default: no event is later); and the rules that fired. With `stability_samples` the Layer
    1b sampler runs with that many birth times from the accuracy class's posterior
    (`birth["accuracy"]`, exact by default), and each area carries the time-stability of its tier
    and whether the engine would narrate it (`narrate`, the stability gate of SPEC test 5); without,
    those are None and the tests fall back to the accuracy class. Top level, so a process pool
    can run it."""
    from jyotish.chart import compute
    from jyotish.scoring import AREAS
    from jyotish.service import birth_utc
    from jyotish.timing import slices, window_pieces
    utc, _ = birth_utc(birth["date"], birth["time"], birth["tz"])
    true_node = (birth.get("node") or "mean") == "true"
    if stability_samples > 0:
        from jyotish.uncertainty import assess
        c = assess(utc, float(birth["lat"]), float(birth["lon"]), true_node=true_node, n=stability_samples,
                   time_accuracy=birth.get("accuracy") or "exact")
    else:
        c = compute(utc, float(birth["lat"]), float(birth["lon"]), true_node=true_node, dasha_levels=2)
    jd0 = c.meta.jd
    day = date.fromisoformat(until) if until else date.today()
    end_jd = _jd(day)
    out = {"areas": {}, "rules": sorted({f.id for f in c.fired_rules}), "until": day.isoformat()}
    cut = spans = None
    if end_jd > jd0:
        spans = slow_spans(c.meta.ayanamsa, c.meta.node == "true", jd0, end_jd)
        cut = slices(c, jd0, end_jd, spans)
    for name, a in c.scored.areas.items():
        spec = AREAS.get(name)
        active, share = [], 0.0
        if cut is not None and spec and spec.get("houses"):
            pieces = window_pieces(c, name, jd0, end_jd, spans, cut=cut)
            active, share = active_windows(pieces, jd0, end_jd, jd0)
        out["areas"][name] = {"score": a.score_classical, "tier": a.tier, "confidence": a.confidence,
                              "votes": dict(a.votes), "terms": dict(sorted(a.terms.items())),
                              "active": active, "active_share": share,
                              "stability_time": a.stability.time if a.stability is not None else None,
                              "narrate": a.narrate if a.stability is not None else None}
    out["stability_samples"] = stability_samples
    return out


def features_for(births: dict[str, dict], workers: int | None = None, until: str | None = None,
                 stability_samples: int = 0) -> dict[str, dict]:
    """birth key -> features, computed in a process pool; `until` closes every life on one day;
    `stability_samples` runs the sampler per chart (see chart_features)."""
    keys = list(births)
    workers = workers or min(8, os.cpu_count() or 1)
    f = partial(chart_features, until=until, stability_samples=stability_samples)
    if workers <= 1 or len(keys) < 50:
        return {k: f(births[k]) for k in keys}
    with ProcessPoolExecutor(max_workers=workers) as ex:
        return dict(zip(keys, ex.map(f, [births[k] for k in keys], chunksize=32)))
