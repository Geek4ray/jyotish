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
from typing import Any

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
    rows = dasha_rows(chart, start_jd, end_jd) + list(tl.rows) + list(tl.tara_rows)
    rows.sort(key=lambda r: (r.start_jd, {"dasha": 0, "transit": 1}.get(r.kind, 2)))
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
    """The timing join under `chart.meta.timing_formula` ("v2" default, "v1" kept)."""
    formula = chart.meta.timing_formula
    if formula in ("v2", "v2.1"):
        return answer_v2(chart, query, formula=formula)
    if formula != "v1":
        raise ValueError(f"timing_formula must be v1, v2 or v2.1, not {formula!r}")
    return answer_v1(chart, query)


def answer_v1(chart: Chart, query: TimingQuery) -> TimingAnswer:
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
    transit = transit_timeline(chart, start, end, taras=False)     # tara rows are not scored yet
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
    return TimingAnswer(query=query, formula="v1", area_tier=area.tier, area_score=area.score_classical,
                        area_stability=area.stability, windows=windows[:query.top], readings=READINGS)


# --- v2 (SPEC Layer 5, timing join v2) ---------------------------------------------------

READINGS_V2 = [
    "q: mean of dignity (-2..2 -> 0..1), Shadbala ratio clipped 0..1, Ishta share, tara class "
    "(adverse 0, Janma 0.5, else 1), relevance (0/1), maha-antar relation (6/8, 2/12 -> 0); "
    "of the period's own lord; nodes average the components they have",
    "relevance: the lord rules, occupies or aspects an area house (query basis), is an area "
    "karaka, or its Nadi activation set does one of these; a Chara sign also when it is an area house",
    "a window exists only where the Vimshottari maha or antar lord is relevant",
    "t: share of Saturn, Jupiter and the nodal axis touching an area house or an area-house "
    "lord's sign; Saturn and Jupiter together = 1; time-weighted",
    "joint = 0.6 q + 0.4 t; the area tier is reported beside, not multiplied in",
    "pieces: Vimshottari antars split at slow-mover ingresses; adjacent pieces with the same "
    "maha/antar and joint within 0.1 merge; windows under 30 days are absorbed by the preceding "
    "window (the following one at the start)",
    "confidence: share of requested systems whose period lords are relevant (>0.7 strong, "
    ">=0.4 moderate, else weak); a window overlapping the month either side of a maha "
    "boundary of a requested system (dasha_sandhi) is capped at moderate",
    "avoid: the window with the lowest joint",
]
SLOW_MOVERS = ("Saturn", "Jupiter", "Rahu", "Ketu")
READINGS_V21 = READINGS_V2[:3] + [
    "t (v2.1): mean over Saturn, Jupiter and the nodal axis of a touch credit against K.N. Rao's "
    "double-transit targets: 1 for the primary house, its lord's sign or the main karaka's sign "
    "(occupation or whole-sign aspect; nodes by occupation), 1/2 for the other area houses and "
    "their lords' signs only; Saturn and Jupiter both on a full target = 1; time-weighted",
] + READINGS_V2[4:] + [
    "an absorbed sub-month piece keeps the host's label and is listed under derivation.absorbed",
    "truncated: the window's Vimshottari antar runs past the edge of the queried range",
    "strongest piece: the highest-joint piece of at least 30 days (else of any length)",
]


def _relevant(chart: Chart, planet: str, basis_sign: int, area_signs: set[int], karakas: set[str]) -> bool:
    if planet in karakas:
        return True
    b = chart.bodies[planet]
    if b.sign in area_signs or any(SIGN_LORD[s] == planet for s in area_signs):
        return True
    if planet in SEVEN:
        h = house_of(b.sign, basis_sign)
        if any(house_of(s, basis_sign) in aspected_houses(planet, h) for s in area_signs):
            return True
    return False


def period_quality_v2(chart: Chart, lords: list[str], relevance: float) -> dict[str, float]:
    p = lords[-1]
    t = chart.bodies[p].tara
    terms = {"tara": 0.0 if t.name in TARA_ADVERSE else 0.5 if t.name == "Janma" else 1.0,
             "relevance": relevance}
    if p in SEVEN:
        terms["dignity"] = (DIGNITY_SCORE[chart.bodies[p].dignity or "node"] + 2.0) / 4.0
        if chart.features.shadbala:
            terms["shadbala"] = max(0.0, min(1.0, chart.features.shadbala.planets[p].ratio))
        if chart.features.ishta_kashta:
            ik = chart.features.ishta_kashta[p]
            terms["ishta"] = ik.ishta / (ik.ishta + ik.kashta) if ik.ishta + ik.kashta else 0.5
    if len(lords) == 2:
        d = (chart.bodies[lords[1]].sign - chart.bodies[lords[0]].sign) % 12 + 1
        terms["relation"] = 0.0 if d in (6, 8, 2, 12) else 1.0
    else:
        terms["relation"] = 1.0
    return terms


# --- the pieces of the v2 join (shared with cohort runs, jyotish.cohort) ---------------------

def rao_targets(chart: Chart, area: str, basis: str = "lagna") -> dict[str, Any]:
    """What the join reads of an area from a basis: the basis sign, the area's house signs and
    their lords' signs, its karakas, and K.N. Rao's double-transit targets (v2.1): the full
    targets are the primary house, its lord's sign and the main karaka's sign; the secondary
    ones the other area houses and their lords' signs."""
    spec = AREAS[area]
    base = {"lagna": chart.lagnas.asc_sign, "moon": chart.bodies["Moon"].sign,
            "sun": chart.bodies["Sun"].sign}[basis]
    area_signs = {(base + h - 1) % 12 for h in spec["houses"]}
    karaka_list = _karakas(_View(chart), spec["karakas"])
    primary = (base + spec["houses"][0] - 1) % 12
    full = {primary, chart.bodies[SIGN_LORD[primary]].sign}
    if karaka_list:
        full.add(chart.bodies[karaka_list[0]].sign)
    secondary = ({s for s in area_signs if s != primary}
                 | {chart.bodies[SIGN_LORD[s]].sign for s in area_signs if s != primary}) - full
    return {"base": base, "area_signs": area_signs, "lord_signs": {chart.bodies[SIGN_LORD[s]].sign for s in area_signs},
            "karakas": set(karaka_list), "full": full, "secondary": secondary}


def _share_slice(signs: dict[str, int], area_signs: set[int], lord_signs: set[int], lagna: int) -> float:
    """v2's t for one slice, from each slow mover's sign: the share of Saturn, Jupiter and the
    nodal axis touching an area house or an area-house lord's sign; 1 when Saturn and Jupiter
    both do."""
    on: dict[str, bool] = {}
    for body, sign in signs.items():
        key = "nodes" if body in ("Rahu", "Ketu") else body
        on[key] = on.get(key, False) or any(_touches(sign, body, s, lagna) for s in area_signs | lord_signs)
    return 1.0 if on.get("Saturn") and on.get("Jupiter") else sum(on.values()) / 3.0


def _rao_slice(signs: dict[str, int], full: set[int], secondary: set[int], lagna: int) -> tuple[float, dict]:
    """v2.1's t for one slice, from each slow mover's sign: per mover (Saturn, Jupiter, the nodal
    axis) credit 1 for touching a full target, 1/2 for touching only a secondary one, else 0; t
    is the mean of the three, and 1 when Saturn and Jupiter both touch a full target. Returns
    (t, the slice detail for the derivation)."""
    credit = {"Saturn": 0.0, "Jupiter": 0.0, "nodes": 0.0}
    bodies: dict[str, list[str]] = {}
    for body, sign in signs.items():
        key = "nodes" if body in ("Rahu", "Ketu") else body
        c = 1.0 if any(_touches(sign, body, t, lagna) for t in full) else \
            0.5 if any(_touches(sign, body, t, lagna) for t in secondary) else 0.0
        credit[key] = max(credit[key], c)
        bodies.setdefault(key, []).append(f"{body} {SIGNS[sign]}")
    t = 1.0 if credit["Saturn"] == 1.0 and credit["Jupiter"] == 1.0 else sum(credit.values()) / 3.0
    return t, {"credits": credit, "bodies": bodies}


def slow_spans_of(rows) -> list[tuple[str, int, float, float]]:
    """The slow movers' sign spans (body, sign, start, end) from a transit timeline's rows."""
    return [(r.body, r.sign, r.start_jd, r.end_jd) for r in rows if r.body in SLOW_MOVERS]


def slices(chart: Chart, start: float, end: float, spans: list[tuple[str, int, float, float]]) -> list[tuple]:
    """Every Vimshottari antar inside [start, end] cut at the slow movers' sign ingresses:
    (x, y, period, signs), `signs` being each slow mover's sign over the slice (no ingress falls
    inside one). `spans` are the slow movers' sign spans covering the range. The same slices
    serve every area of a chart, which is what a cohort run needs (jyotish.cohort)."""
    import bisect
    by_body: dict[str, list[tuple[float, float, int]]] = {}
    for body, sign, t0, t1 in spans:
        if t1 > start and t0 < end:
            by_body.setdefault(body, []).append((t0, t1, sign))
    for v in by_body.values():
        v.sort()
    starts = {b: [t0 for t0, _, _ in v] for b, v in by_body.items()}
    edges = sorted({t0 for v in by_body.values() for t0, _, _ in v if start < t0 < end})

    def signs_at(m: float) -> dict[str, int]:
        out = {}
        for b in SLOW_MOVERS:
            v = by_body.get(b)
            if not v:
                continue
            i = bisect.bisect_right(starts[b], m) - 1
            if i >= 0 and v[i][0] <= m < v[i][1]:
                out[b] = v[i][2]
        return out
    out = []
    for per in chart.dashas.get("vimshottari", []):
        if len(per.lords) != 2 or per.end_jd <= start or per.start_jd >= end:
            continue
        a, b = max(start, per.start_jd), min(end, per.end_jd)
        cuts = [a] + edges[bisect.bisect_right(edges, a):bisect.bisect_left(edges, b)] + [b]
        for x, y in zip(cuts, cuts[1:]):
            out.append((x, y, per, signs_at((x + y) / 2.0)))
    return out


def window_pieces(chart: Chart, area: str, start: float, end: float, spans: list[tuple[str, int, float, float]],
                  basis: str = "lagna", formula: str = "v2.1", cut: list[tuple] | None = None) -> list[dict]:
    """The join's pieces for an area over [start, end]: the slices of the gated antars (maha or
    antar lord relevant to the area from `basis`), each with its q terms, q, t (v2.1's Rao credit,
    v2's share) and joint = 0.6 q + 0.4 t. `cut` is `slices(...)` already made, so a cohort run
    cuts a chart once for all its areas. answer_v2 builds its windows from these pieces, and
    jyotish.cohort its activation years, so the two cannot drift apart."""
    tg = rao_targets(chart, area, basis)
    lagna = chart.lagnas.asc_sign

    def relevant(lords: list[str]) -> bool:
        planet = lords[-1]
        return any(_relevant(chart, q, tg["base"], tg["area_signs"], tg["karakas"])
                   for q in [planet] + activation_set(chart, planet))
    gate: dict[tuple, tuple[bool, bool]] = {}
    quality: dict[tuple, tuple[dict, float]] = {}
    pieces = []
    for x, y, per, signs in (cut if cut is not None else slices(chart, start, end, spans)):
        key = tuple(per.lords)
        if key not in gate:
            gate[key] = (relevant(list(per.lords[:1])), relevant(list(per.lords)))
        maha_rel, antar_rel = gate[key]
        if not (maha_rel or antar_rel):
            continue
        if key not in quality:
            terms = period_quality_v2(chart, list(per.lords), 1.0 if antar_rel else 0.0)
            quality[key] = (terms, sum(terms.values()) / len(terms))
        terms, q = quality[key]
        if formula == "v2.1":
            t, tdetail = _rao_slice(signs, tg["full"], tg["secondary"], lagna)
        else:
            t, tdetail = _share_slice(signs, tg["area_signs"], tg["lord_signs"], lagna), None
        pieces.append({"a": x, "b": y, "lords": key, "q": q, "t": t, "terms": terms,
                       "joint": 0.6 * q + 0.4 * t, "transit": tdetail})
    return pieces


def answer_v2(chart: Chart, query: TimingQuery, formula: str = "v2") -> TimingAnswer:
    if chart.scored is None:
        raise ValueError("the chart has no Layer 5 score (it needs the birth moment)")
    start, end = _jd(query.start), _jd(query.end)
    area = chart.scored.areas[query.area]
    tg = rao_targets(chart, query.area, query.basis)
    base, area_signs, karakas = tg["base"], tg["area_signs"], tg["karakas"]

    def relevant(system: str, lords: list[str]) -> bool:
        planet = _lord_planet(system, lords[-1])
        if system == "chara" and SIGNS.index(lords[-1]) in area_signs:
            return True
        return any(_relevant(chart, q, base, area_signs, karakas) for q in [planet] + activation_set(chart, planet))

    periods = {s: [p for p in chart.dashas.get(s, []) if len(p.lords) == 2 and p.end_jd > start and p.start_jd < end]
               for s in ("vimshottari",) + tuple(x for x in query.systems if x != "vimshottari")}
    transit = transit_timeline(chart, start, end, taras=False)     # tara rows are not scored yet
    mahas = [p for s in query.systems for p in chart.dashas.get(s, []) if len(p.lords) == 1]
    bounds = {}
    if chart.uncertainty is not None:
        for bd in chart.uncertainty.boundaries:
            bounds.setdefault(round(bd.start_jd, 6), []).append(bd)

    # Pieces: gated Vimshottari antars, split at slow-mover ingresses (window_pieces, shared with
    # the cohort runs).
    pieces = window_pieces(chart, query.area, start, end, slow_spans_of(transit.rows), query.basis, formula)

    def weighted(ws):
        span = sum(w["b"] - w["a"] for w in ws)
        return {k: sum(w[k] * (w["b"] - w["a"]) for w in ws) / span for k in ("q", "t", "joint")}

    # Merge adjacent pieces with the same maha/antar and joint within 0.1.
    merged = []
    for pc in pieces:
        last = merged[-1] if merged else None
        if (last and last["lords"] == pc["lords"] and abs(last["b"] - pc["a"]) < 1e-9
                and abs(last["joint"] - pc["joint"]) <= 0.1):
            group = last["parts"] + [pc]
            last.update(weighted(group), b=pc["b"], parts=group)
        else:
            merged.append(dict(pc, parts=[pc]))
    # Absorb windows shorter than a month into the preceding (else the following) window.
    changed = True
    while changed and len(merged) > 1:
        changed = False
        for i, w in enumerate(merged):
            if w["b"] - w["a"] < 30.0:
                j = i - 1 if i > 0 else i + 1
                host = merged[j]
                group = (host["parts"] + w["parts"]) if j < i else (w["parts"] + host["parts"])
                absorbed = host.get("absorbed", []) + [{"start_jd": w["a"], "end_jd": w["b"], "lords": list(w["lords"])}] \
                    + w.get("absorbed", [])
                host.update(weighted(group), a=min(host["a"], w["a"]), b=max(host["b"], w["b"]), parts=group,
                            absorbed=absorbed)   # the host keeps its own label (lords, q terms)
                del merged[i]
                changed = True
                break

    windows = []
    for w in merged:
        mid = (w["a"] + w["b"]) / 2.0
        per_sys, rel = {}, {}
        for system, rows in periods.items():
            r = next((x for x in rows if x.start_jd <= mid < x.end_jd), None)
            if r is not None:
                per_sys[system] = list(r.lords)
                rel[system] = relevant(system, list(r.lords)) or (system == "vimshottari" and relevant(system, list(r.lords[:1])))
        share = sum(rel[s] for s in query.systems if s in rel) / len(query.systems)
        conf = "strong" if share > 0.7 else "moderate" if share >= 0.4 else "weak"
        tags = []
        # Sandhi: the window overlaps the last or first month of adjoining maha periods.
        junctions = {m.start_jd for m in mahas} | {m.end_jd for m in mahas}
        if any(w["a"] < t0 + SANDHI_DAYS and w["b"] > t0 - SANDHI_DAYS for t0 in junctions
               if start < t0 < end):
            tags.append("dasha_sandhi")
            if conf == "strong":
                conf = "moderate"
        stab = None
        if chart.uncertainty is not None:
            edge = [x for t0 in (w["a"], w["b"]) for x in bounds.get(round(t0, 6), [])]
            if edge:
                stab = {"time_range_days": max(x.time_range_days for x in edge),
                        "ayanamsa_range_days": max((x.ayanamsa_range_days or 0.0) for x in edge),
                        "boundaries": len(edge)}
        vim = next((x for x in periods["vimshottari"] if x.start_jd <= mid < x.end_jd), None)
        if vim is not None and ((w["a"] <= start + 1e-9 and vim.start_jd < start - 1e-9)
                                or (w["b"] >= end - 1e-9 and vim.end_jd > end + 1e-9)):
            tags.append("truncated")
        long_parts = [p for p in w["parts"] if p["b"] - p["a"] >= 30.0] or w["parts"]
        best = max(long_parts, key=lambda p: p["joint"])
        windows.append(TimingWindow(
            start_jd=w["a"], end_jd=w["b"], joint=w["joint"], dasha_quality=w["q"],
            transit_activation=w["t"], periods={k: v for k, v in per_sys.items() if k in query.systems},
            stability=stab, tags=tags, confidence=conf,
            derivation={"formula": "0.6 q + 0.4 t", "transit_formula": formula, "q_terms": w["terms"],
                        "t": w["t"], "pieces": len(w["parts"]),
                        "relevant_systems": [s for s in query.systems if rel.get(s)],
                        "strongest_piece": {"start_jd": best["a"], "end_jd": best["b"], "joint": best["joint"],
                                            "q": best["q"], "t": best["t"], "transit": best.get("transit")},
                        "absorbed": w.get("absorbed", []),
                        "targets": ({"full": sorted(SIGNS[x] for x in tg["full"]),
                                     "secondary": sorted(SIGNS[x] for x in tg["secondary"])}
                                    if formula == "v2.1" else None),
                        "area_tier": area.tier}))
    ranked = sorted(windows, key=lambda x: -x.joint)
    avoid = min(windows, key=lambda x: x.joint) if windows else None
    readings = READINGS_V2 if formula == "v2" else READINGS_V21
    return TimingAnswer(query=query, formula=formula, area_tier=area.tier, area_score=area.score_classical,
                        area_stability=area.stability, windows=ranked[:query.top], avoid=avoid, readings=readings)
