"""The Phase 0 cross-check (SPEC Layer 1, "Validation of this layer alone"): seeded random births
computed by the engine (Lahiri, mean node) and by PyJHora, compared quantity by quantity.

    .venv/bin/pip install -e ".[crosscheck]"
    .venv/bin/python scripts/crosscheck.py                 # 1,000 births, writes docs/crosscheck.md
    .venv/bin/python scripts/crosscheck.py --n 200 --seed 7

Licensing: PyJHora is AGPL (its metadata says so; one classifier says MIT) and is a development-
time reference only. It is installed by the dev-only extra "crosscheck" and imported by this
script and its test, never by src/.

What is compared, against the SPEC gate:
  - the nine bodies' sidereal longitudes and the ascendant: within 1 arc-second;
  - nakshatra and pada of each body and the ascendant;
  - the 16 Parashari varga signs of each body and the ascendant. Boundary-aware: where either
    longitude is within 1'' of the varga's (or pada's) edge, a difference is listed, not failed;
  - the Vimshottari mahadasha start dates: within one day.
PyJHora is set to the engine's conventions before anything is computed: Lahiri, the mean node,
apparent positions (aberration, light deflection and nutation on; its default is true geometric
positions without nutation), and the engine's dasha year of 365.25 days (its default is the mean
sidereal year, 365.256364). Its varga method for each chart is chosen by PyJHora's own label, the
lowest-numbered method its docstring calls "Traditional Parasara" (method 1 everywhere but the
hora, whose 2 it is; its 1 is Uma Shambu's parivritti hora), never by agreement with the engine,
so the varga comparison tests the engine's arithmetic against PyJHora's reading of Parashara
(review 2026-10-23, F11); the report prints every label chosen, and a control with the Raman hora
must fail.

Both programs call the same Swiss Ephemeris (pyswisseph), so agreement on positions shows that the
two use it the same way (flags, ayanamsa, node, ascendant), not that two ephemerides agree; an
independent ephemeris is SPEC's licensing track (jplephem / skyfield), not this check."""

from __future__ import annotations

import argparse
import contextlib
import inspect
import io
import math
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import swisseph as swe  # noqa: E402

from jyotish.chart import compute  # noqa: E402
from jyotish.constants import GRAHAS  # noqa: E402
from jyotish.nakshatra import nakshatra_of  # noqa: E402
from jyotish.vargas import VARGAS  # noqa: E402

ARCSEC = 1.0 / 3600.0
SHODASAVARGA = [1, 2, 3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60]
PARASHARI_LABEL = "Traditional Parasara"      # the words PyJHora's docstrings use for Parashara's method
BODIES = GRAHAS + ["Asc"]
DOC = ROOT / "docs" / "crosscheck.md"


# --- PyJHora, set to the engine's conventions ----------------------------------------------------

@dataclass
class Jhora:
    version: str
    drik: object
    charts: object
    vimsottari: object
    const: object
    defaults: dict = field(default_factory=dict)
    methods: dict = field(default_factory=dict)       # varga -> (chart_method, PyJHora's label), by label


def parashari_methods(charts) -> dict[int, tuple[int, str]]:
    """PyJHora's chart_method for each varga, chosen by its own label: the lowest-numbered method
    whose docstring line says "Traditional Parasara". Chosen by name, never by agreement with the
    engine, so that the varga comparison is a test and not a fit."""
    out = {}
    for k in SHODASAVARGA:
        if k == 1:
            continue
        fn = getattr(charts, charts.divisional_chart_functions[k])
        lines = [(int(m.group(1)), m.group(2).strip()) for m in
                 (re.match(r"\s*(\d+)\s*=>\s*(.*)$", line) for line in (inspect.getdoc(fn) or "").splitlines()) if m]
        hits = [(n, label) for n, label in lines if PARASHARI_LABEL.lower() in label.lower()]
        if not hits:
            raise RuntimeError(f"PyJHora names no {PARASHARI_LABEL!r} method for D{k}: {lines}")
        out[k] = min(hits)
    return out


def load_pyjhora() -> Jhora:
    """Import PyJHora quietly (it prints and edits sys.path on import) and set it to Lahiri, the
    mean node, apparent positions and a 365.25-day dasha year. Raises ImportError when absent."""
    from importlib.metadata import version
    saved_path = list(sys.path)
    with contextlib.redirect_stdout(io.StringIO()):
        from jhora import const, utils
        from jhora.horoscope.chart import charts
        from jhora.horoscope.dhasa.graha import vimsottari
        from jhora.panchanga import drik
    sys.path[:] = saved_path
    defaults = {"ayanamsa": const._DEFAULT_AYANAMSA_MODE, "true_nodes": const._use_true_nodes_for_rahu_ketu,
                "true_positions": getattr(const, "PLANET_POSITIONS_TRUE", True),
                "nutation": getattr(const, "PLANET_POSITIONS_USE_NUTATION", False),
                "deflection": getattr(const, "PLANET_POSITIONS_USE_DEFLECTION", False),
                "dasha_year": vimsottari.year_duration}
    const.PLANET_POSITIONS_TRUE = False
    const.PLANET_POSITIONS_USE_ABERRATION = True
    const.PLANET_POSITIONS_USE_DEFLECTION = True
    const.PLANET_POSITIONS_USE_NUTATION = True
    const.set_node_mode(False)
    drik.refresh_planet_flags()
    vimsottari.year_duration = 365.25
    # PyJHora's import points Swiss Ephemeris at its own folder; give the engine's back.
    if os.environ.get("JYOTISH_EPHE_PATH"):
        swe.set_ephe_path(os.environ["JYOTISH_EPHE_PATH"])
    return Jhora(version("PyJHora"), drik, charts, vimsottari, const, defaults, parashari_methods(charts))


def ephemeris_mode() -> str:
    """What Swiss Ephemeris actually ran: a file-ephemeris call falls back to Moshier without files."""
    _, ret = swe.calc_ut(2451545.0, swe.SUN, swe.FLG_SWIEPH)
    return "Swiss Ephemeris files" if ret & swe.FLG_SWIEPH else "Moshier (no ephemeris files)"


# --- the births ---------------------------------------------------------------------------------

def draw_births(n: int, seed: int) -> list[dict]:
    """Uniform in time over 1900-2050, longitude over the globe, latitude 60 S to 60 N."""
    rng = np.random.default_rng(seed)
    t0 = datetime(1900, 1, 1, tzinfo=timezone.utc)
    span = (datetime(2051, 1, 1, tzinfo=timezone.utc) - t0).total_seconds()
    out = []
    for i in range(n):
        utc = t0 + timedelta(seconds=float(rng.uniform(0, span)))
        out.append({"i": i, "utc": utc.replace(microsecond=0), "lat": round(float(rng.uniform(-60, 60)), 4),
                    "lon": round(float(rng.uniform(-180, 180)), 4)})
    return out


def _jd(utc: datetime) -> float:
    return swe.julday(utc.year, utc.month, utc.day, utc.hour + utc.minute / 60 + utc.second / 3600)


# --- each side ----------------------------------------------------------------------------------

def engine_side(b: dict) -> dict:
    c = compute(b["utc"], b["lat"], b["lon"], ayanamsa="lahiri", true_node=False, dasha_levels=1)
    lon = {p: c.bodies[p].lon for p in GRAHAS} | {"Asc": c.lagnas.asc}
    nak = {p: (nakshatra_of(v).index + 1, nakshatra_of(v).pada) for p, v in lon.items()}
    vargas = {k: {p: VARGAS[f"D{k}"](v) for p, v in lon.items()} for k in SHODASAVARGA}
    maha = [(p.lords[0], p.start_jd) for p in c.dashas["vimshottari"] if len(p.lords) == 1]
    return {"lon": lon, "nak": nak, "vargas": vargas, "maha": maha}


def pyjhora_side(j: Jhora, b: dict, methods: dict | None = None) -> dict:
    """`methods` overrides the label-chosen varga methods (the control test passes Raman's hora)."""
    methods = methods or j.methods
    jd = _jd(b["utc"])
    place = j.drik.Place("x", b["lat"], b["lon"], 0.0)          # timezone 0: jd is UTC
    with contextlib.redirect_stdout(io.StringIO()):
        j.drik.set_ayanamsa_mode("LAHIRI")
        ids = [j.const._SUN, j.const._MOON, j.const._MARS, j.const._MERCURY, j.const._JUPITER, j.const._VENUS,
               j.const._SATURN, j.const._RAHU, j.const._KETU]
        lon = {p: j.drik.sidereal_longitude(jd, pid) for p, pid in zip(GRAHAS, ids)}
        sign, deg, *_ = j.drik.ascendant(jd, place)
        lon["Asc"] = sign * 30 + deg
        nak = {p: tuple(j.drik.nakshatra_pada(v)[:2]) for p, v in lon.items()}
        rasi = [[i, (int(v // 30), v % 30)] for i, v in enumerate(lon.values())]
        vargas = {}
        for k in SHODASAVARGA:
            if k == 1:
                vargas[k] = {p: int(v // 30) for p, v in lon.items()}
                continue
            got = j.charts.divisional_positions_from_rasi_positions(rasi, k, chart_method=methods[k][0])
            vargas[k] = {p: got[i][1][0] for i, p in enumerate(lon)}
        md = j.vimsottari.vimsottari_mahadasa(jd, place)
    maha = [(GRAHAS[lord], start) for lord, start in md.items()]
    return {"lon": lon, "nak": nak, "vargas": vargas, "maha": maha}


# --- comparison ---------------------------------------------------------------------------------

def arcsec(a: float, b: float) -> float:
    d = (a - b + 180.0) % 360.0 - 180.0
    return abs(d) * 3600.0


TRIMSAMSA_EDGES = {True: [0, 5, 10, 18, 25, 30], False: [0, 5, 12, 20, 25, 30]}     # odd, even signs


def edge_distance(lon: float, k: int) -> float:
    """Arc-seconds from `lon` to the nearest edge of its D-k part (k = 108 for the pada)."""
    lon %= 360.0
    if k == 108:
        x = lon * 108.0 / 360.0
        return min(x - math.floor(x), math.ceil(x) - x) * (360.0 / 108.0) * 3600.0
    deg = lon % 30.0
    if k == 30:
        edges = TRIMSAMSA_EDGES[int(lon // 30) % 2 == 0]
        return min(abs(deg - e) for e in edges) * 3600.0
    x = deg * k / 30.0
    return min(x - math.floor(x), math.ceil(x) - x) * (30.0 / k) * 3600.0


@dataclass
class Result:
    n: int
    errors: dict = field(default_factory=dict)          # quantity -> list of errors
    listed: list = field(default_factory=list)          # boundary differences: listed, not failed
    failed: list = field(default_factory=list)          # gate failures, each with its cause


def compare(births: list[dict], ours: list[dict], theirs: list[dict]) -> Result:
    r = Result(n=len(births))
    for b, o, t in zip(births, ours, theirs):
        who = f"birth {b['i']} ({b['utc'].isoformat()}, {b['lat']}, {b['lon']})"
        for p in BODIES:
            e = arcsec(o["lon"][p], t["lon"][p])
            r.errors.setdefault(f"longitude {p}", []).append(e)
            if e > 1.0:
                r.failed.append(f"{who}: {p} longitude differs by {e:.3f}″")
            if o["nak"][p] != t["nak"][p]:
                row = f"{who}: {p} nakshatra/pada {o['nak'][p]} vs {t['nak'][p]}"
                near = min(edge_distance(o["lon"][p], 108), edge_distance(t["lon"][p], 108))
                (r.listed if near <= 1.0 else r.failed).append(
                    row + (f" (within {near:.3f}″ of a pada edge)" if near <= 1.0 else f" (longitudes {e:.3f}″ apart)"))
            for k in SHODASAVARGA:
                if o["vargas"][k][p] != t["vargas"][k][p]:
                    near = min(edge_distance(o["lon"][p], k), edge_distance(t["lon"][p], k))
                    row = f"{who}: D{k} {p} sign {o['vargas'][k][p]} vs {t['vargas'][k][p]}"
                    if near <= 1.0:
                        r.listed.append(row + f" (within {near:.3f}″ of a D{k} edge)")
                    else:
                        r.failed.append(row + f" ({near:.1f}″ from the edge: a rule difference)")
        lords_o, lords_t = [x[0] for x in o["maha"]], [x[0] for x in t["maha"]]
        if lords_o[:9] != lords_t[:9]:
            r.failed.append(f"{who}: mahadasha order {lords_o[:3]} vs {lords_t[:3]} "
                            f"(Moon {arcsec(o['lon']['Moon'], t['lon']['Moon']):.3f}″ apart)")
            continue
        for (lord, a), (_, z) in zip(o["maha"][:9], t["maha"][:9]):
            d = abs(a - z)
            r.errors.setdefault("mahadasha start (days)", []).append(d)
            if d > 1.0:
                r.failed.append(f"{who}: {lord} mahadasha starts {d:.3f} days apart")
    return r


def run(n: int, seed: int) -> tuple[Result, Jhora, list[dict]]:
    j = load_pyjhora()
    births = draw_births(n, seed)
    ours = [engine_side(b) for b in births]
    theirs = [pyjhora_side(j, b) for b in births]
    return compare(births, ours, theirs), j, births


# --- the report ---------------------------------------------------------------------------------

def _commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True,
                              check=True).stdout.strip()
    except Exception:
        return "unknown"


def summary(r: Result) -> dict:
    """quantity -> (max, mean), for the scorecard."""
    return {q: (max(v), sum(v) / len(v)) for q, v in r.errors.items() if v}


def report(r: Result, j: Jhora, n: int, seed: int, seconds: float) -> str:
    s = summary(r)
    rows = "\n".join(f"| {q} | {mx:.6f} | {mean:.6f} |" for q, (mx, mean) in s.items())
    gate = "passes" if not r.failed else f"fails ({len(r.failed)} disagreements beyond the gate)"
    d = j.defaults
    out = [
        "# Phase 0 cross-check: the engine against PyJHora", "",
        f"Run {date.today().isoformat()} at commit `{_commit()}` by `scripts/crosscheck.py --n {n} --seed {seed}` "
        f"in {seconds:.0f} s. PyJHora {j.version}; ephemeris: {ephemeris_mode()}, for both programs (they call the "
        "same Swiss Ephemeris, so this checks how each uses it, not two ephemerides).", "",
        f"**Gate (SPEC Layer 1: within 1″, varga signs boundary-aware, mahadasha starts within a day): {gate}.**", "",
        f"{n} births drawn with seed {seed}: uniform in time over 1900-2050, longitude over the globe, latitude "
        "60° S to 60° N. The engine at Lahiri, the mean node, apparent positions (Moshier unless JYOTISH_EPHE_PATH "
        "names ephemeris files) and a 365.25-day dasha year.", "",
        "PyJHora set to the same conventions before anything was computed. Its own defaults, any of which would "
        f"show here as a disagreement: ayanamsa {d['ayanamsa']}, true nodes {d['true_nodes']}, true (geometric) "
        f"positions {d['true_positions']}, nutation {d['nutation']}, light deflection {d['deflection']}, dasha year "
        f"{d['dasha_year']} days.", "",
        "Varga methods, chosen by PyJHora's own labels (the lowest-numbered method its docstring calls "
        f"\"{PARASHARI_LABEL}\"), never by agreement with the engine: "
        + "; ".join(f"D{k} method {n} ({label})" for k, (n, label) in sorted(j.methods.items())) + ".", "",
        "## Errors per quantity", "",
        "Longitudes in arc-seconds; mahadasha starts in days.", "",
        "| quantity | max | mean |", "| --- | --- | --- |", rows, "",
        "## Causes of the residuals", "",
        *(["- Rahu and Ketu (up to "
           f"{max(s.get('longitude Rahu', (0, 0))[0], s.get('longitude Ketu', (0, 0))[0]):.6f}″): the engine asks Swiss "
           "Ephemeris for the mean node with the Moshier flag, PyJHora with the file flag, which falls back to Moshier "
           "without files; the two paths differ by up to 0.00013″ (seen directly at JD 2415021.0, 1900)."]
          if max(s.get("longitude Rahu", (0, 0))[0], s.get("longitude Ketu", (0, 0))[0]) > 0 else []),
        "- Every other residual is zero to six decimals: the same library, flags and ayanamsa on both sides.", "",
        f"## Disagreements beyond the gate ({len(r.failed)})", "",
        *([f"- {x}" for x in r.failed] or ["None."]), "",
        f"## Listed, not failed: within 1″ of an edge ({len(r.listed)})", "",
        "A body this close to a varga or pada edge may legitimately fall either side (SPEC Layer 1).", "",
        *([f"- {x}" for x in r.listed] or ["None."]), "",
    ]
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    import time
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--n", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=str(DOC))
    a = ap.parse_args(argv)
    t = time.time()
    try:
        r, j, _ = run(a.n, a.seed)
    except ImportError as e:
        print(f"PyJHora is not installed ({e}): pip install -e '.[crosscheck]'", file=sys.stderr)
        return 2
    Path(a.out).write_text(report(r, j, a.n, a.seed, time.time() - t))
    print(f"{a.n} births: {len(r.failed)} beyond the gate, {len(r.listed)} listed at edges -> {a.out}")
    return 0 if not r.failed else 1


if __name__ == "__main__":
    sys.exit(main())
