"""The tagged timeline and the timing join (SPEC Layers 4 and 5).

`tagged_timeline(chart, start, end)` merges the dasha rows of every system (Vimshottari,
Yogini, Chara, two levels) with the transit rows into one list ordered by start, each row
typed by `kind`; the named transit windows travel alongside.

`answer(chart, TimingQuery)` returns the top windows for an area. SPEC: "takes the static
S_area, multiplies by the dasha quality score of each window, adds the transit activation
of the area's houses". Simplest readings, named (READINGS):

  period quality   for a planet lord, the mean of its Navatara class (-1..1), D1 dignity / 2,
                   Shadbala ratio - 1 clipped to +-1, and (Ishta - Kashta) / 60; nodes have
                   only the Navatara term. A Chara period takes the quality of its sign's lord.
                   An antardasha's quality is the mean of its maha and antar lords'.
  relevance        1 when the antar lord, its maha lord, or anyone in the antar lord's Nadi
                   activation set (planets in its nakshatras, and its own nakshatra lord) is a
                   lord, karaka or occupant of the area's houses from the query basis, or (for
                   Chara) the period sign is one of those houses; else 0.
  windows          the overlaps of the requested systems' antardashas inside the date range.
  dasha quality    of a window: the mean over the systems of quality x relevance, so systems
                   agreeing raise it.
  transit          Jupiter and Saturn touching (occupy or whole-sign aspect) the area's first
                   house or its lord's sign: 0.5 each, 1.0 for both (K.N. Rao's double
                   transit), averaged over the window by time.
  joint            (S_area / the area's population p90) x dasha quality + transit activation.
  sandhi           a window within 30 days of a maha boundary of any system is tagged
                   "dasha_sandhi" (SPEC: nothing predicted into it above moderate confidence).
  stability        when the chart carries the Layer 1b block: the largest time and ayanamsa
                   spread, in days, of the dasha boundaries that open and close the window."""

from __future__ import annotations

import json
import math

from .constants import GRAHAS, SEVEN, SIGN_LORD, SIGNS, TARA_ADVERSE
from .dignity import aspected_houses, house_of
from .models import (
    Chart, DashaRow, TaggedTimeline, TimingAnswer, TimingQuery, TimingWindow,
)
from .scoring import AREAS, DIGNITY_SCORE, PCT_FILE, _karakas, _View
from .transits import transit_timeline

SYSTEMS = ("vimshottari", "yogini", "chara")
SANDHI_DAYS = 30.0
READINGS = [
    "period quality: mean of Navatara, dignity/2, Shadbala ratio-1 (clipped), (Ishta-Kashta)/60",
    "relevance 1 if the period's lords or Nadi activation set touch the area's houses, else 0",
    "windows: overlaps of the requested systems' antardashas",
    "dasha quality: mean over systems of quality x relevance",
    "transit: Jupiter and Saturn on the first house or its lord, 0.5 each, time-averaged",
    "joint: (S_area / population p90) x dasha quality + transit",
    "dasha_sandhi: within 30 days of a maha boundary",
]


def _jd(d) -> float:
    import swisseph as swe
    return swe.julday(d.year, d.month, d.day, 0.0)


# --- period quality ----------------------------------------------------------------------

def planet_quality(chart: Chart, p: str) -> dict[str, float]:
    t = chart.bodies[p].tara
    nav = -1.0 if t.name in TARA_ADVERSE else 0.0 if t.name == "Janma" else 1.0
    terms = {"navatara": nav if t.cycle == 1 else nav / 2.0}
    if p in SEVEN:
        terms["dignity"] = DIGNITY_SCORE[chart.bodies[p].dignity or "node"] / 2.0
        if chart.features.shadbala:
            terms["shadbala"] = max(-1.0, min(1.0, chart.features.shadbala.planets[p].ratio - 1.0))
        if chart.features.ishta_kashta:
            ik = chart.features.ishta_kashta[p]
            terms["ishta_kashta"] = (ik.ishta - ik.kashta) / 60.0
    return terms


def _lord_planet(system: str, lord: str) -> str:
    return SIGN_LORD[SIGNS.index(lord)] if system == "chara" else lord


def activation_set(chart: Chart, p: str) -> list[str]:
    """Nadi activation: planets in p's nakshatras, and p's own nakshatra lord."""
    out = [q for q in GRAHAS if q != p and chart.bodies[q].nak_lord == p]
    own = chart.bodies[p].nak_lord
    if own != p and own not in out:
        out.append(own)
    return out


def dasha_rows(chart: Chart, start_jd: float, end_jd: float) -> list[DashaRow]:
    quality = {p: planet_quality(chart, p) for p in GRAHAS}
    rows = []
    for system in SYSTEMS:
        for per in chart.dashas.get(system, []):
            if per.end_jd <= start_jd or per.start_jd >= end_jd:
                continue
            planets = [_lord_planet(system, l) for l in per.lords]
            qs = [sum(quality[p].values()) / len(quality[p]) for p in planets]
            tags = [f"system:{system}", f"level:{len(per.lords)}"]
            if len(planets) == 2:
                d = (chart.bodies[planets[1]].sign - chart.bodies[planets[0]].sign) % 12 + 1
                if d in (6, 8):
                    tags.append("relation:6/8")
                elif d in (2, 12):
                    tags.append("relation:2/12")
            rows.append(DashaRow(
                system=system, level=len(per.lords), lords=list(per.lords), start_jd=per.start_jd,
                end_jd=per.end_jd, quality=sum(qs) / len(qs),
                quality_terms={k: v for k, v in quality[planets[-1]].items()},
                tara=chart.bodies[planets[-1]].tara.name, activation=activation_set(chart, planets[-1]),
                tags=tags))
    return rows


def tagged_timeline(chart: Chart, start_jd: float, end_jd: float) -> TaggedTimeline:
    tl = transit_timeline(chart, start_jd, end_jd)
    rows = dasha_rows(chart, start_jd, end_jd) + list(tl.rows)
    rows.sort(key=lambda r: (r.start_jd, 0 if r.kind == "dasha" else 1))
    return TaggedTimeline(start_jd=start_jd, end_jd=end_jd, rows=rows, windows=tl.windows)


# --- the join ----------------------------------------------------------------------------

def _area_targets(chart: Chart, area: str, basis: str) -> tuple[set[str], set[int], int, str]:
    """(planets that touch the area, the area's house signs, first-house sign, its lord)."""
    spec = AREAS[area]
    base = {"lagna": chart.lagnas.asc_sign, "moon": chart.bodies["Moon"].sign,
            "sun": chart.bodies["Sun"].sign}[basis]
    signs = {(base + h - 1) % 12 for h in spec["houses"]}
    lords = {SIGN_LORD[s] for s in signs}
    occupants = {p for p in GRAHAS if chart.bodies[p].sign in signs}
    karakas = set(_karakas(_View(chart), spec["karakas"]))
    first = (base + spec["houses"][0] - 1) % 12
    return lords | occupants | karakas, signs, first, SIGN_LORD[first]


def _touches(sign_of: int, planet: str, target: int, lagna: int) -> bool:
    h, t = house_of(sign_of, lagna), house_of(target, lagna)
    return h == t or (planet in SEVEN and t in aspected_houses(planet, h))


def _p90(area: str) -> float:
    return json.loads(PCT_FILE.read_text())["percentiles"][area]["p90"]


def answer(chart: Chart, query: TimingQuery) -> TimingAnswer:
    if chart.scored is None:
        raise ValueError("the chart has no Layer 5 score (it needs the birth moment)")
    start, end = _jd(query.start), _jd(query.end)
    area = chart.scored.areas[query.area]
    s_norm = (area.score_classical or 0.0) / _p90(query.area)
    touching, area_signs, first_sign, first_lord = _area_targets(chart, query.area, query.basis)
    rows = [r for r in dasha_rows(chart, start, end) if r.system in query.systems]
    antars = {s: [r for r in rows if r.system == s and r.level == 2] for s in query.systems}
    mahas = [r for r in rows if r.level == 1]

    # Window edges: every antar boundary of the requested systems inside the range.
    edges = sorted({start, end} | {t for rs in antars.values() for r in rs for t in (r.start_jd, r.end_jd)
                                   if start < t < end})
    transit = transit_timeline(chart, start, end)
    lagna = chart.lagnas.asc_sign
    bounds = {}
    if chart.uncertainty is not None:
        for b in chart.uncertainty.boundaries:
            bounds.setdefault(round(b.start_jd, 6), []).append(b)

    windows = []
    for a, b in zip(edges, edges[1:]):
        mid = (a + b) / 2.0
        periods, parts, why = {}, [], {}
        for system, rs in antars.items():
            r = next((x for x in rs if x.start_jd <= mid < x.end_jd), None)
            if r is None:
                continue
            planets = [_lord_planet(system, l) for l in r.lords]
            involved = set(planets) | set(r.activation)
            relevant = bool(involved & touching) or (system == "chara" and SIGNS.index(r.lords[-1]) in area_signs)
            periods[system] = r.lords
            parts.append(r.quality * (1.0 if relevant else 0.0))
            why[system] = {"lords": r.lords, "quality": round(r.quality, 4), "relevant": relevant,
                           "via": sorted(involved & touching), "tags": r.tags}
        if not parts:
            continue
        dq = sum(parts) / len(parts)
        # Transit activation, time-weighted over [a, b].
        act = 0.0
        for body in ("Jupiter", "Saturn"):
            for r in transit.rows:
                if r.body != body or r.end_jd <= a or r.start_jd >= b:
                    continue
                overlap = (min(b, r.end_jd) - max(a, r.start_jd)) / (b - a)
                hit = (_touches(r.sign, body, first_sign, lagna)
                       or _touches(r.sign, body, chart.bodies[first_lord].sign, lagna))
                act += 0.5 * overlap * hit
        joint = s_norm * dq + act
        tags = []
        if any(abs(a - m.start_jd) < SANDHI_DAYS or abs(b - m.start_jd) < SANDHI_DAYS
               or abs(a - m.end_jd) < SANDHI_DAYS or abs(b - m.end_jd) < SANDHI_DAYS for m in mahas):
            tags.append("dasha_sandhi")
        stab = None
        if chart.uncertainty is not None:
            edge_b = [x for t in (a, b) for x in bounds.get(round(t, 6), [])]
            if edge_b:
                stab = {"time_range_days": max(x.time_range_days for x in edge_b),
                        "ayanamsa_range_days": max((x.ayanamsa_range_days or 0.0) for x in edge_b),
                        "boundaries": len(edge_b)}
        windows.append(TimingWindow(
            start_jd=a, end_jd=b, joint=joint, dasha_quality=dq, transit_activation=act,
            periods=periods, stability=stab, tags=tags,
            derivation={"S_area": area.score_classical, "S_norm": s_norm, "systems": why,
                        "transit": act, "formula": "S_norm x dasha_quality + transit"}))
    windows.sort(key=lambda w: -w.joint)
    return TimingAnswer(query=query, area_tier=area.tier, area_score=area.score_classical,
                        area_stability=area.stability, windows=windows[:query.top], readings=READINGS)
