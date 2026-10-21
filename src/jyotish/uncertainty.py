"""Layer 1b-A: the uncertainty sampler. It runs before scoring and needs only the birth
data and its accuracy class (SPEC Layer 1b; the rectifier, which uses outcomes, runs after
scoring and is not here).

`assess` computes the chart at the recorded time, then:
  - the time axis: `n` birth times drawn from the accuracy-class posterior, each a full
    chart with rules (exact: uniform +-2 min; within_15: uniform +-15; approximate:
    Gaussian, sigma 30 min; unknown: uniform over the day);
  - the ayanamsa axis: the recorded time under Lahiri, Raman and KP;
  - the house axis: the recorded time under whole sign and Sripati.
Every fired rule, varga placement and dasha boundary of the recorded-time chart gets one
number per axis, never pooled: a doctrinal choice is not clock error.

The per-sample charts are computed one by one (the ephemeris and the rule evaluator are
scalar); the aggregation over samples is vectorised."""

from __future__ import annotations

import time as _time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import numpy as np

from .chart import ACCURACY_HALF_WIDTH_MIN, compute
from .ephemeris import compute_sky
from .models import (
    BoundaryStability, Chart, RuleShare, Stability, TimePosterior, Uncertainty,
)
from .vargas import PRODUCTION_VARGAS, VARGAS

AYANAMSA_AXIS = ("lahiri", "raman", "kp")
HOUSE_AXIS = ("whole_sign", "sripati")
DASHA_SYSTEMS = ("vimshottari", "yogini", "chara")


def sample_times(jd: float, time_accuracy: str, n: int = 200, seed: int = 0) -> np.ndarray:
    half = ACCURACY_HALF_WIDTH_MIN[time_accuracy] / 1440.0
    rng = np.random.default_rng(seed)
    if time_accuracy == "approximate":
        return jd + rng.normal(0.0, half / 2.0, size=n)  # sigma = 30 min for a 60-min half-width
    return jd + rng.uniform(-half, half, size=n)


def label(time_share: float) -> str:
    return "unstable" if time_share < 0.5 else "sensitive" if time_share <= 0.8 else "stable"


# --- what a chart asserts, as hashable keys ---------------------------------------------

def rule_keys(chart: Chart) -> set[tuple]:
    """(id, basis, planets): a fire "still holds" when the same rule fires from the same
    basis on the same planets (its house nodes may move)."""
    return {(f.id, f.basis, tuple(n for n in f.nodes if not n.startswith("H")))
            for f in chart.fired_rules}


def placements(chart: Chart) -> dict[tuple[str, str], int]:
    return {(v, b): s for v, signs in chart.vargas.items() for b, s in signs.items()}


def boundaries(chart: Chart) -> dict[tuple[str, tuple[str, ...]], float]:
    """Start of every dasha period, keyed by system and the lord sequence. Chara and
    Yogini lords repeat across cycles, so repeats are numbered."""
    out: dict[tuple, float] = {}
    for system in DASHA_SYSTEMS:
        seen: dict[tuple, int] = {}
        for p in chart.dashas.get(system, []):
            lords = tuple(p.lords)
            k = seen.get(lords, 0)
            seen[lords] = k + 1
            out[(system, lords if k == 0 else lords + (f"#{k + 1}",))] = p.start_jd
    return out


def _share(center, others) -> float:
    return sum(1 for o in others if o == center) / len(others)


@dataclass
class _Run:
    chart: Chart
    rules: set
    places: dict
    starts: dict


def _run(chart: Chart) -> _Run:
    return _Run(chart, rule_keys(chart), placements(chart), boundaries(chart))


def assess(utc: datetime, lat: float, lon: float, *, time_accuracy: str = "exact",
           n: int = 200, seed: int = 0, true_node: bool = True, tz: str | None = None) -> Chart:
    """The recorded-time chart (Lahiri, whole sign) with `stability` on every fired rule
    and the `uncertainty` block filled."""
    t0 = _time.perf_counter()
    utc = utc.astimezone(timezone.utc) if utc.tzinfo else utc.replace(tzinfo=timezone.utc)
    kw = dict(true_node=true_node, time_accuracy=time_accuracy, tz=tz)
    center = compute(utc, lat, lon, **kw)
    c = _run(center)
    jd0 = center.meta.jd

    times = sample_times(jd0, time_accuracy, n, seed)
    samples = [_run(compute(utc + timedelta(days=float(t - jd0)), lat, lon, **kw)) for t in times]
    ayan = [c if a == "lahiri" else _run(compute(utc, lat, lon, ayanamsa=a, **kw)) for a in AYANAMSA_AXIS]
    house = [c if h == "whole_sign" else _run(compute(utc, lat, lon, house_system=h, **kw))
             for h in HOUSE_AXIS]

    # Fired rules: membership matrices over each axis.
    keys = sorted(c.rules)
    t_hits = np.array([[k in s.rules for s in samples] for k in keys], dtype=bool).reshape(len(keys), n)
    a_hits = np.array([[k in r.rules for r in ayan] for k in keys], dtype=bool).reshape(len(keys), len(ayan))
    h_hits = np.array([[k in r.rules for r in house] for k in keys], dtype=bool).reshape(len(keys), len(house))
    by_key = {k: (t_hits[i].mean(), a_hits[i].mean(), h_hits[i].mean()) for i, k in enumerate(keys)}
    for f in center.fired_rules:
        k = (f.id, f.basis, tuple(x for x in f.nodes if not x.startswith("H")))
        t, a, h = by_key[k]
        f.stability = Stability(time=float(t), ayanamsa=float(a), house=float(h), label=label(float(t)))
    elsewhere: dict[tuple, int] = {}
    for s in samples:
        for k in s.rules - c.rules:
            elsewhere[k] = elsewhere.get(k, 0) + 1
    rules_elsewhere = [RuleShare(id=k[0], basis=k[1], planets=list(k[2]), time=v / n)
                       for k, v in sorted(elsewhere.items(), key=lambda kv: -kv[1])]

    # Varga placements: sign arrays over samples, compared with the recorded sign.
    pkeys = sorted(c.places)
    centre_signs = np.array([c.places[k] for k in pkeys])
    t_signs = np.array([[s.places[k] for k in pkeys] for s in samples])          # (n, keys)
    a_signs = np.array([[r.places[k] for k in pkeys] for r in ayan])
    h_signs = np.array([[r.places[k] for k in pkeys] for r in house])
    t_share = (t_signs == centre_signs).mean(axis=0)
    a_share = (a_signs == centre_signs).mean(axis=0)
    h_share = (h_signs == centre_signs).mean(axis=0)
    placement_block: dict[str, dict[str, Stability]] = {}
    for i, (v, b) in enumerate(pkeys):
        placement_block.setdefault(v, {})[b] = Stability(
            time=float(t_share[i]), ayanamsa=float(a_share[i]), house=float(h_share[i]),
            label=label(float(t_share[i])))
    varga_stability = {v: placement_block[v]["Asc"].time for v in PRODUCTION_VARGAS}

    # Dasha boundaries: start dates across samples, in days.
    bkeys = list(c.starts)
    t_starts = np.array([[s.starts.get(k, np.nan) for k in bkeys] for s in samples], dtype=float)
    present = ~np.isnan(t_starts)
    with np.errstate(invalid="ignore"):
        t_range = np.nanmax(t_starts, axis=0) - np.nanmin(t_starts, axis=0)
        t_sd = np.nanstd(t_starts, axis=0)

    def axis_range(runs, k):
        vals = [r.starts.get(k) for r in runs]
        return None if any(v is None for v in vals) else float(max(vals) - min(vals))

    boundary_block = [
        BoundaryStability(system=k[0], lords=list(k[1]), start_jd=c.starts[k],
                          time_share=float(present[:, i].mean()),
                          time_range_days=float(t_range[i]), time_sd_days=float(t_sd[i]),
                          ayanamsa_range_days=axis_range(ayan, k),
                          house_range_days=axis_range(house, k))
        for i, k in enumerate(bkeys)]

    shape = "gaussian" if time_accuracy == "approximate" else "uniform"
    center.birth.time_posterior = TimePosterior(
        shape=shape, half_width_min=ACCURACY_HALF_WIDTH_MIN[time_accuracy], samples=n)
    center.uncertainty = Uncertainty(
        samples=n, half_width_min=ACCURACY_HALF_WIDTH_MIN[time_accuracy], shape=shape,
        center_jd=jd0, ayanamsas=list(AYANAMSA_AXIS), house_systems=list(HOUSE_AXIS),
        varga_stability=varga_stability, placements=placement_block,
        boundaries=boundary_block, rules_elsewhere=rules_elsewhere,
        seconds=_time.perf_counter() - t0)
    return center


# --- the lagna-only summary kept from Phase 0 -------------------------------------------

@dataclass(frozen=True)
class LagnaStability:
    samples: int
    half_width_min: float
    shape: str
    varga_lagna: dict[str, float]               # share of samples with the same lagna varga sign
    varga_bodies: dict[str, dict[str, float]]   # varga -> body -> share with the same sign
    ayanamsa_lagna: dict[str, int]              # D1 lagna sign under each ayanamsa


def stability(jd: float, lat: float, lon: float, time_accuracy: str = "exact", n: int = 200,
              ayanamsa: str = "lahiri", seed: int = 0) -> LagnaStability:
    """Positions-only stability of the lagna and planets per varga (no rules, no dashas)."""
    base = compute_sky(jd, lat, lon, ayanamsa=ayanamsa)
    base_asc = {v: VARGAS[v](base.asc) for v in PRODUCTION_VARGAS}
    base_bodies = {v: {b: VARGAS[v](p.lon) for b, p in base.bodies.items()} for v in PRODUCTION_VARGAS}
    times = sample_times(jd, time_accuracy, n, seed)
    asc_hits = {v: 0 for v in PRODUCTION_VARGAS}
    body_hits = {v: {b: 0 for b in base.bodies} for v in PRODUCTION_VARGAS}
    for t in times:
        sky = compute_sky(float(t), lat, lon, ayanamsa=ayanamsa)
        for v in PRODUCTION_VARGAS:
            if VARGAS[v](sky.asc) == base_asc[v]:
                asc_hits[v] += 1
            for b, p in sky.bodies.items():
                if VARGAS[v](p.lon) == base_bodies[v][b]:
                    body_hits[v][b] += 1
    shape = "gaussian" if time_accuracy == "approximate" else "uniform"
    ayan = {a: int(compute_sky(jd, lat, lon, ayanamsa=a).asc // 30) for a in AYANAMSA_AXIS}
    return LagnaStability(
        samples=n, half_width_min=ACCURACY_HALF_WIDTH_MIN[time_accuracy], shape=shape,
        varga_lagna={v: asc_hits[v] / n for v in PRODUCTION_VARGAS},
        varga_bodies={v: {b: body_hits[v][b] / n for b in base.bodies} for v in PRODUCTION_VARGAS},
        ayanamsa_lagna=ayan,
    )
