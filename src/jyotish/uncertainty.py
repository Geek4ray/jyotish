"""Layer 1b-A: the uncertainty sampler. Draws birth times from the posterior implied by
the accuracy class, recomputes the chart for each, and reports per-varga stability of the
lagna and the planets. Ayanamsa and house-system robustness are separate axes."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .chart import ACCURACY_HALF_WIDTH_MIN
from .ephemeris import compute_sky
from .vargas import PRODUCTION_VARGAS, VARGAS


@dataclass(frozen=True)
class Stability:
    samples: int
    half_width_min: float
    shape: str
    varga_lagna: dict[str, float]           # share of samples with the same lagna varga sign
    varga_bodies: dict[str, dict[str, float]]  # varga -> body -> share with same sign
    ayanamsa_lagna: dict[str, int]           # lagna sign under each ayanamsa (D1)


def sample_times(jd: float, time_accuracy: str, n: int = 200, seed: int = 0) -> np.ndarray:
    half = ACCURACY_HALF_WIDTH_MIN[time_accuracy] / 1440.0
    rng = np.random.default_rng(seed)
    if time_accuracy == "approximate":
        return jd + rng.normal(0.0, half / 2.0, size=n)  # sigma = 30 min for a 60-min half-width
    return jd + rng.uniform(-half, half, size=n)


def stability(jd: float, lat: float, lon: float, time_accuracy: str = "exact", n: int = 200,
              ayanamsa: str = "lahiri", seed: int = 0) -> Stability:
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
    ayan = {}
    for a in ("lahiri", "raman", "kp"):
        ayan[a] = int(compute_sky(jd, lat, lon, ayanamsa=a).asc // 30)
    return Stability(
        samples=n, half_width_min=ACCURACY_HALF_WIDTH_MIN[time_accuracy], shape=shape,
        varga_lagna={v: asc_hits[v] / n for v in PRODUCTION_VARGAS},
        varga_bodies={v: {b: body_hits[v][b] / n for b in base.bodies} for v in PRODUCTION_VARGAS},
        ayanamsa_lagna=ayan,
    )
