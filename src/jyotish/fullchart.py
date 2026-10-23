"""The whole chart for the writer at depth full (SPEC Layer 7, depth full; docs/spec_notes_2026-10-23.md).

`payload(chart, as_of, start, end, areas)` serialises everything the engine computes, compactly,
under stable paths: a path is the keys from the root joined by dots, a list item by its index
(`planets.Mars.dignity`, `shadbala.Mars.ratio`, `vimshottari.periods.Rahu-Saturn-Venus`,
`yogini.periods.12`). A sentence cites any field as `[fact:<path>]`; the validator accepts the
tag when `resolve` finds the path, and the checker receives the field's value beside the
sentence. Nothing here is new computation: every value is the chart's own or one the engine's
own functions return for it (the display tables, the timing join, the transit timeline).

What is left out, and why (each would cite nothing the rest does not):
  - absolute longitudes: a position is its sign and degree within the sign (d°m′s″), the way the
    chart table shows it;
  - the Moon's transit rows, its daily tara rows and the vedha spans it casts over the range: one
    row every two days and every day, thousands over ten years; the slow planets' and the Sun's
    and Mars's rows stay;
  - Kakshya spans of the fast transits (Sun, Mars): a span lasts under four days;
  - Julian days: every date is YYYY-MM-DD (UTC).

What the engine knows is stated, not left to be inferred (docs/spec_notes_2026-10-23.md, the second
heading): a stability is {time, ayanamsa, house} with its word and "holds under n of 3 ayanamsas"
(SPEC Layer 1b's three numbers, never pooled); a varga dignity carries its label beside its number;
a field whose reference point is not obvious says it in its name (tara_from_moon, bav_grade,
good_from_moon); `constants` holds the tables a sentence leans on (sign order, sign lords,
exaltation, debilitation, moolatrikona), `houses` each house's sign, lord and occupants from the
lagna, the Moon and the Sun ("Aquarius, the 10th house from the lagna" cites houses.lagna.10), and
`not_computed` what the engine does not do, so a sentence about it has a fact to cite."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from typing import Any

from .constants import GRAHAS, SEVEN, SIGNS
from .models import Chart, Stability

FAST_TRANSITS = ("Sun", "Mars")       # rows kept, Kakshya spans left out
LEFT_OUT_TRANSITS = ("Moon",)         # rows and tara rows left out (see the module docstring)


def _date(jd: float) -> str:
    import swisseph as swe
    y, m, d, _ = swe.revjul(jd, swe.GREG_CAL)
    return f"{y:04d}-{m:02d}-{d:02d}"


def _r(x: Any, n: int = 3) -> Any:
    """Floats rounded (n places), recursively; everything else as it is."""
    if isinstance(x, float):
        return round(x, n)
    if isinstance(x, dict):
        return {str(k): _r(v, n) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_r(v, n) for v in x]
    return x


def _st(s: Stability | None, chart: Chart) -> dict | None:
    """A stability as a labelled object: the three shares, the time share's word, and how many of the
    sampled ayanamsas and house systems it holds under ("holds under 2 of 3 ayanamsas")."""
    if s is None:
        return None
    u = chart.uncertainty
    n_ay, n_h = (len(u.ayanamsas), len(u.house_systems)) if u else (3, 2)
    return {"time": round(s.time, 3), "ayanamsa": round(s.ayanamsa, 3), "house": round(s.house, 3), "label": s.label,
            "ayanamsas": f"holds under {round(s.ayanamsa * n_ay)} of {n_ay} ayanamsas",
            "house_systems": f"holds under {round(s.house * n_h)} of {n_h} house systems"}


def _time_st(share: float | None, chart: Chart) -> dict | None:
    """A time-only stability (the share of the birth-time samples in which a thing holds) as a
    labelled object, like every stability in the payload (review F8: the varga lagnas and the
    votes' stability were bare numbers)."""
    if share is None:
        return None
    from .uncertainty import label
    n = chart.uncertainty.samples if chart.uncertainty else 200
    return {"time": round(share, 3), "label": label(share),
            "samples": f"holds in {round(share * n)} of {n} birth-time samples"}


def _pos(lon: float) -> str:
    """A sidereal longitude as its sign and degree within the sign: 'Taurus 6°17′31″'."""
    from .display import dms
    return f"{SIGNS[int(lon * 12 / 360) % 12]} {dms(lon % 30)}"


def _planets(chart: Chart) -> dict:
    from .display import dms
    out = {}
    for p in GRAHAS:
        b = chart.bodies[p]
        out[p] = {"sign": b.sign_name, "deg": dms(b.deg), "house": b.house, "nakshatra": b.nak_name, "pada": b.pada,
                  "nak_lord": b.nak_lord, "sub_lord": b.sub_lord, "sub_sub_lord": b.sub_sub_lord,
                  "tara_from_moon": b.tara.name, "retro": b.retro, "combust": b.combust, "speed": _r(b.speed),
                  "dignity": b.dignity, "dignity_compound": b.dignity_compound, "avastha_baladi": b.avastha_baladi,
                  "vargottama": b.vargottama}
    return out


def constants() -> dict:
    """The tables a sentence leans on, citable as facts: the sign order, each sign's lord, and each
    planet's exaltation, debilitation and moolatrikona signs and own signs (constants.py; BPHS 3)."""
    from .constants import EXALTATION, MOOLATRIKONA, OWN_SIGNS, SIGN_LORD
    return {"signs": list(SIGNS), "sign_lords": {SIGNS[i]: p for i, p in SIGN_LORD.items()},
            "exaltation": {p: SIGNS[x[0]] for p, x in EXALTATION.items()},
            "debilitation": {p: SIGNS[(x[0] + 6) % 12] for p, x in EXALTATION.items()},
            "moolatrikona": {p: SIGNS[x[0]] for p, x in MOOLATRIKONA.items()},
            "own_signs": {p: [SIGNS[i] for i in signs] for p, signs in OWN_SIGNS.items()}}


def _houses(chart: Chart) -> dict:
    """houses.<basis>.<n>: the nth house from the lagna, the Moon and the Sun, its sign, lord and
    the bodies in it, so "Aquarius, the 10th house from the lagna" cites houses.lagna.10 and "Saturn,
    lord of the 10th" the same field. From the lagna the houses follow Meta.house_system (review
    F12): under sripati a house is the bhava, its sign the madhya's, its occupants the bodies whose
    house the chart gives as that bhava, as planets.<p>.house does; from the Moon and the Sun they
    are whole signs. `houses.system` says which."""
    from .constants import SIGN_LORD
    base = {"lagna": chart.lagnas.asc_sign, "moon": chart.bodies["Moon"].sign, "sun": chart.bodies["Sun"].sign}
    sripati = chart.meta.house_system == "sripati" and len(chart.lagnas.bhava_madhya_sripati) == 12
    out: dict[str, Any] = {"system": {"lagna": "sripati" if sripati else "whole_sign", "moon": "whole_sign",
                                      "sun": "whole_sign"}}
    for basis, first in base.items():
        out[basis] = {}
        for n in range(1, 13):
            if basis == "lagna" and sripati:
                sign = int(chart.lagnas.bhava_madhya_sripati[n - 1] * 12 / 360) % 12
                occupants = [p for p in GRAHAS if chart.bodies[p].house == n]
            else:
                sign = (first + n - 1) % 12
                occupants = [p for p in GRAHAS if chart.bodies[p].sign == sign]
            out[basis][str(n)] = {"sign": SIGNS[sign], "lord": SIGN_LORD[sign], "occupants": occupants}
    return out


# What the engine does not do (CLAUDE.md phase status, SPEC Layers 1b, 6 and 7), so a sentence saying
# so in "what the chart does not say" has a fact to cite.
NOT_COMPUTED = {
    "synastry": "needs a second chart: the engine reads one chart, describes a relationship only as this "
                "chart shows it, and says nothing of another person's own chart or life",
    "rectification": "the birth time is not rectified: each finding carries its stability over the time window instead",
    "probability": "no area has a calibrated probability: probability stays null until outcome data calibrates it",
    "score_learned": "no learned score: score_learned is null until a model is trained on outcomes",
    "special_lagnas": "the special lagnas (Hora, Ghati, Indu, Sree, Varnada) are not computed",
    "retrieval": "no corpus of the classical texts is searched: the only verses cited are those checked on rules",
    "question_routing": "a question is routed to its areas by keyword; no model translates it into a query",
    "tara_scoring": "the transit taras are tagged but not scored: the timing join leaves them out",
    "draft_placements": "a placement's effect is a draft until its verse is read: it weighs nothing and is not narrated",
    "never": "the engine never times death, diagnoses illness, advises a trade or investment, or states another "
             "person's fate",
}


def _tara_named(row: dict) -> dict:
    """A nakshatra-table row with its tara under the name that says where it is counted from."""
    return {("tara_from_moon" if k == "tara" else k): v for k, v in row.items()}


def _sensitive(chart: Chart) -> dict:
    """The sensitive-degree flags of each body (SPEC Layer 2): gandanta, pushkara navamsa and
    bhaga, marana karaka sthana, a sign or nakshatra boundary within the time window, and the
    distance from deep exaltation."""
    return {p: {"gandanta": b.gandanta, "pushkara_navamsa": b.pushkara_navamsa, "pushkara_bhaga": b.pushkara_bhaga,
                "marana_karaka_sthana": b.marana_karaka_sthana, "boundary": b.boundary,
                "deep_exalt_dist": _r(b.deep_exalt_dist, 2)} for p, b in chart.bodies.items()}


def _lagnas(chart: Chart) -> dict:
    from .display import dms
    L = chart.lagnas
    out = {"asc": {"sign": L.asc_sign_name, "deg": dms(L.asc % 30), "nakshatra": L.asc_nak, "nak_lord": L.asc_nak_lord,
                   "tara_from_moon": L.asc_tara},
           "mc": _pos(L.mc) if L.mc is not None else None,
           "kp_cusps": {f"H{h}": dict(_r(L.cusp_lords_kp.get(h, {})), cusp=_pos(lon))
                        for h, lon in sorted(L.cusps_placidus.items())},
           "sripati_madhya": {f"H{i}": _pos(lon) for i, lon in enumerate(L.bhava_madhya_sripati, 1)}}
    return out


def _vargas(chart: Chart) -> dict:
    return {v: {p: SIGNS[s] for p, s in places.items()} for v, places in chart.vargas.items()}


def _special(chart: Chart) -> dict | None:
    np_ = chart.features.nakshatra_points
    if np_ is None:
        return None
    d = np_.model_dump(exclude={"sources"})
    def conv(x):
        if isinstance(x, dict):
            return {k: (_pos(v) if k in ("start", "end") and isinstance(v, float) else conv(v)) for k, v in x.items()}
        if isinstance(x, list):
            return [conv(v) for v in x]
        return x
    return _r(conv(d))


def _dispositors(chart: Chart) -> dict:
    from .display import dispositor_panel
    d = chart.features.dispositors
    panel = dispositor_panel(chart)
    return {kind: {"chains": {r["planet"]: r["chain"] for r in panel[kind]["rows"]}, "loops": panel[kind]["loops"],
                   "final": getattr(d, f"final_{kind}")} for kind in panel} | \
        {"loop_classes": [l.model_dump() for l in d.loops]}


def _vimshottari(chart: Chart, as_of: date) -> dict:
    """Every period to the pratyantar, keyed by its lords ("Rahu", "Rahu-Saturn",
    "Rahu-Saturn-Venus"), as [start, end]; a maha or antar carries the sampler's spread of its
    start over the birth-time samples in days ("start_spread_days")."""
    from .dasha import vimshottari
    from .timing import _jd
    periods = vimshottari(chart.bodies["Moon"].lon, chart.meta.jd, levels=3, year_length=chart.meta.dasha_year)
    spread = {tuple(b.lords): b for b in (chart.uncertainty.boundaries if chart.uncertainty else [])
              if b.system == "vimshottari"}
    now = _jd(as_of)
    out, current = {}, []
    for p in periods:
        row: dict[str, Any] = {"start": _date(p.start_jd), "end": _date(p.end_jd)}
        b = spread.get(tuple(p.lords))
        if b is not None:
            row["start_spread_days"] = round(b.time_range_days, 2)
        out["-".join(p.lords)] = row
        if p.start_jd <= now < p.end_jd and len(p.lords) > len(current):
            current = list(p.lords)
    return {"current": "-".join(current), "first_maha_starts_before_birth": periods[0].start_jd < chart.meta.jd,
            "periods": out}


def _listed(chart: Chart, system: str, as_of: date) -> dict:
    from .timing import _jd
    spread = {(tuple(b.lords), round(b.start_jd, 4)): b for b in (chart.uncertainty.boundaries if chart.uncertainty else [])
              if b.system == system}
    now = _jd(as_of)
    rows, current = [], None
    for i, p in enumerate(chart.dashas.get(system, [])):
        row: dict[str, Any] = {"lords": "-".join(p.lords), "start": _date(p.start_jd), "end": _date(p.end_jd)}
        if p.names:
            row["names"] = "-".join(p.names)
        b = spread.get((tuple(p.lords), round(p.start_jd, 4)))
        if b is not None:
            row["start_spread_days"] = round(b.time_range_days, 2)
            if b.time_share < 1:
                row["exists_in_samples"] = round(b.time_share, 3)
        rows.append(row)
        if p.start_jd <= now < p.end_jd and len(p.lords) == 2:
            current = i
    return {"current": current, "periods": rows}


def _period_quality(chart: Chart) -> dict:
    """What the timing join scores a period by, per lord (timing.planet_quality) and the houses a
    lord's period activates (timing.activation_set, the Nadi activation)."""
    from .timing import activation_set, planet_quality
    out = {}
    for p in GRAHAS:
        row = {"terms": _r(planet_quality(chart, p)), "activation": activation_set(chart, p)}
        if "dignity" in row["terms"]:
            row["dignity_label"] = chart.bodies[p].dignity       # the word behind the dignity term
        out[p] = row
    return out


def _transits(chart: Chart, start: date, end: date) -> dict:
    from .timing import _jd
    from .transits import transit_timeline
    tl = transit_timeline(chart, _jd(start), _jd(end))
    rows = []
    for r in tl.rows:
        if r.body in LEFT_OUT_TRANSITS:
            continue
        row = {"body": r.body, "sign": r.sign_name, "start": _date(r.start_jd), "end": _date(r.end_jd),
               "entered": r.entered, "houses": r.houses, "bav": r.bav, "sav": r.sav,
               # The grade is from the transiting planet's own BAV bindus in the sign (Phaladeepika
               # 23.11), the good house from the natal Moon (Phaladeepika 26.2): the names say which.
               "bav_grade": r.grade, "good_from_moon": r.gochara_good, "murthi": r.murthi, "tags": r.tags,
               "vedha": [f"{v.by} {_date(v.start_jd)}..{_date(v.end_jd)}" for v in r.vedha
                         if v.by not in LEFT_OUT_TRANSITS],
               "vipareeta_vedha": [f"{v.by} {_date(v.start_jd)}..{_date(v.end_jd)}" for v in r.vipareeta_vedha
                                   if v.by not in LEFT_OUT_TRANSITS]}
        if r.clipped_start or r.clipped_end:
            row["clipped"] = [x for x, on in (("start", r.clipped_start), ("end", r.clipped_end)) if on]
        if r.body not in FAST_TRANSITS:
            row["kakshya"] = [f"{k.lord} {_date(k.start_jd)}..{_date(k.end_jd)}"
                              + ("" if k.bindu is None else (" bindu" if k.bindu else " no bindu")) for k in r.kakshya]
        rows.append(row)
    taras = [{"body": t.body, "nakshatra": t.nakshatra, "tara_from_moon": t.tara, "count": t.count, "adverse": t.adverse,
              "special": t.special, "start": _date(t.start_jd), "end": _date(t.end_jd), "tags": t.tags}
             for t in tl.tara_rows if t.body not in LEFT_OUT_TRANSITS]
    windows = [{"kind": w.kind, "start": _date(w.start_jd), "end": _date(w.end_jd), "tags": w.tags, "details": _r(w.details)}
               for w in tl.windows]
    return {"range": {"start": start.isoformat(), "end": end.isoformat()}, "rows": rows, "tara_rows": taras,
            "windows": windows, "left_out": "the Moon's rows, daily tara rows and vedha spans; Kakshya spans of the "
                                            "Sun and Mars"}


def _timing(chart: Chart, areas: list[str], start: date, end: date) -> dict:
    """The timing join's windows (timing.answer, the engine's formula) per area for the range."""
    from .models import TimingQuery
    from .scoring import AREAS
    from .timing import answer
    out = {}
    for name in areas:
        if name not in AREAS:
            continue
        ans = answer(chart, TimingQuery(area=name, start=start, end=end))
        def win(w):
            d = dict(w.derivation)
            sp = d.pop("strongest_piece", None)
            antar = (w.periods.get("vimshottari") or [None])[-1]
            return {"start": _date(w.start_jd), "end": _date(w.end_jd), "score": round(w.joint, 3),
                    # q's dignity term is the Vimshottari antar lord's (timing.period_quality_v2)
                    "dignity_of": (f"{antar} ({chart.bodies[antar].dignity})"
                                   if antar in SEVEN and "dignity" in d.get("q_terms", {}) else None),
                    "q": round(w.dasha_quality, 3), "t": round(w.transit_activation, 3), "periods": w.periods,
                    "confidence": w.confidence, "tags": w.tags,
                    "edge_spread_days": _r((w.stability or {}).get("time_range_days"), 2),
                    "q_terms": _r(d.get("q_terms", {})), "targets": d.get("targets"),
                    "strongest_piece": ({"start": _date(sp["start_jd"]), "end": _date(sp["end_jd"]),
                                         "score": round(sp["joint"], 3), "t": round(sp["t"], 3),
                                         "transit": sp.get("transit")} if sp else None)}
        out[name] = {"formula": ans.formula, "windows": [win(w) for w in ans.windows],
                     "avoid": win(ans.avoid) if ans.avoid is not None else None}
    return out


def rule_key(rule_id: str) -> str:
    """A rule id as a path key: a path splits on dots, so `place.l7_h7` is written `place-l7_h7`
    (review F3: every key under `rules` was uncitable)."""
    return rule_id.replace(".", "-")


def _fire_key(f, seen: dict) -> str:
    key = f"{rule_key(f.id)}@{f.basis}"
    if key in seen:
        key += "~" + "+".join(n for n in f.nodes if not n.startswith("H"))
    seen[key] = True
    return key


def _rules(chart: Chart) -> dict:
    """Every fire, experimental and draft included, with its status, keyed by its rule id with the
    dots written as hyphens and its basis (`rules.place-l7_h7@lagna.status`); the fire's `id` is the
    rule's own."""
    seen: dict = {}
    out = {}
    for f in chart.fired_rules:
        out[_fire_key(f, seen)] = {"id": f.id, "family": f.family, "school": f.school, "status": f.status,
                                   "basis": f.basis, "nodes": f.nodes, "scale": round(f.scale, 3),
                                   "themes": _r(f.themes), "applied": f.applied, "unknown": f.unknown,
                                   "details": _r(f.details), "stability": _st(f.stability, chart)}
    return out


def _areas(chart: Chart) -> dict:
    """Every area's score and every family vote with its derivation (the scoring layer's own)."""
    from .scoring import family_rho, family_weights
    sc = chart.scored
    rho = family_rho(chart.meta.varga_term, chart.meta.kp_vote)
    out = {}
    for name, a in sc.areas.items():
        weights = family_weights(a, rho) if a.score_classical is not None else {}
        out[name] = {"tier": a.tier, "score_classical": _r(a.score_classical), "confidence": _r(a.confidence),
                     "direction": a.direction, "emphasised": a.emphasised, "stability": _st(a.stability, chart),
                     "families_agree_w": _r(a.families_agree_w), "families_total_w": _r(a.families_total_w),
                     "lords": a.lords, "karakas": a.karakas, "main_karaka": a.karakas[0] if a.karakas else None,
                     "polarity": a.polarity,
                     "polarity_touches": a.polarity_touches, "varga_consistency": _r(a.varga_consistency),
                     "votes": {fam: {"vote": v, **family_term(a, fam), "weight": _r(weights.get(fam)),
                                     "stability": _time_st(a.vote_stability.get(fam), chart),
                                     "derivation": _r(a.vote_details.get(fam))}
                               for fam, v in a.votes.items()}}
        if a.score_classical is not None:
            out[name]["contributions"] = contributions(a, name, chart)
    return out


# A family's term in S (scoring.score_area): the lord family's vote reads its lord and dispositor
# terms together, so its term is their sum; arudha and KP vote but add nothing to S.
FAMILY_TERMS = {"house": ("house",), "lord": ("lord", "dispositor"), "karaka": ("karaka",), "varga": ("varga",),
                "panchanga": ("panchanga",)}


def family_term(a, fam: str) -> dict:
    """A family's one term, the same wherever the payload states it (review F13: the votes gave the
    lord term alone, the contributions lord plus dispositor): its value in S and the S terms it holds."""
    parts = FAMILY_TERMS.get(fam)
    if parts is None or not a.terms:
        return {"term": None, "term_holds": []}
    return {"term": round(sum(a.terms.get(t, 0.0) for t in parts), 3), "term_holds": list(parts)}


def contributions(a, area: str, chart: Chart) -> dict:
    """The families of an area by what each is on this chart. `ranked`: each family's term as it
    enters S (no confluence weight, which enters only the tier's agreement: review F4), in order.
    The terms are on different scales (the lord term sums fifteen lord rows at WEIGHTS["lord"] and
    the dispositor term), so the largest is the lord family's on most charts by construction; each
    family therefore also carries its `percentile`, where this chart's term falls among 10,000
    random charts' (scripts/family_rho.py), and `strongest` and `weakest` are by percentile: what is
    unusual on this chart. Arudha and KP vote without a term and are listed apart; the rules and
    Navatara terms of S are not families."""
    from .scoring import family_quantiles, term_percentile
    q = family_quantiles(chart.meta.varga_term, chart.meta.kp_vote).get(area, {})
    ranked = []
    for fam, parts in FAMILY_TERMS.items():
        if a.votes.get(fam) is None:
            continue
        term = sum(a.terms.get(t, 0.0) for t in parts)
        row = {"family": fam, "term": round(term, 3), "term_holds": list(parts), "vote": a.votes[fam]}
        if fam in q:
            row["percentile"] = term_percentile(q[fam], term)
        ranked.append(row)
    ranked.sort(key=lambda r: -r["term"])
    for i, r in enumerate(ranked, 1):
        r["rank_by_term"] = i
    by_pct = sorted((r for r in ranked if "percentile" in r), key=lambda r: -r["percentile"])
    return {"basis": "each family's term as it enters the area score, largest first; the terms are on different "
                     "scales and the lord term is the largest on most charts by construction, so the strongest and "
                     "the weakest are by percentile against 10,000 random charts: what is unusual on this chart",
            "ranked": ranked,
            "vote_only": [{"family": f, "vote": a.votes[f]} for f in ("arudha", "kp") if a.votes.get(f) is not None],
            "largest_term": ranked[0]["family"] if ranked else None,
            "strongest": by_pct[0]["family"] if by_pct else None,
            "strongest_percentile": by_pct[0]["percentile"] if by_pct else None,
            "weakest": by_pct[-1]["family"] if by_pct else None,
            "weakest_percentile": by_pct[-1]["percentile"] if by_pct else None,
            "against": [f for f, v in a.votes.items() if v == -1],
            "abstaining": [f for f, v in a.votes.items() if v == 0],
            "other_terms": {t: round(a.terms.get(t, 0.0), 3) for t in ("rules", "navatara")}}


def _uncertainty(chart: Chart) -> dict | None:
    u = chart.uncertainty
    if u is None:
        return None
    return {"samples": u.samples, "half_width_min": u.half_width_min, "shape": u.shape, "ayanamsas": u.ayanamsas,
            "house_systems": u.house_systems,
            "lagna_sign_by_varga": {v: _time_st(x, chart) for v, x in u.varga_stability.items()},
            "placements": {v: {p: _st(s, chart) for p, s in rows.items()} for v, rows in u.placements.items()},
            "nakshatras": {p: _st(s, chart) for p, s in (u.nakshatras or {}).items()},
            "rules_elsewhere": [{"id": r.id, "basis": r.basis, "planets": r.planets, "stability": _time_st(r.time, chart)}
                                for r in u.rules_elsewhere],
            "reading": "a stability gives the shares of the birth-time samples (time), of the ayanamsas and of "
                       "the house systems in which the finding holds, its word, and the counts"}


def payload(chart: Chart, as_of: date, start: date, end: date, areas: list[str]) -> dict[str, Any]:
    """Everything the engine computes on `chart`, under stable paths (the module docstring)."""
    from .display import nakshatra_table
    from .narrate import chart_header
    ft = chart.features
    sb, bb = ft.shadbala, ft.bhava_bala
    av = ft.ashtakavarga
    shadbala = None
    if sb is not None:
        shadbala = {p: {"sthana": _r(x.sthana.model_dump(), 1), "dig": round(x.dig, 1), "kala": _r(x.kala.model_dump(), 1),
                        "chesta": round(x.chesta, 1), "naisargika": round(x.naisargika, 1), "drik": round(x.drik, 1),
                        "total_rupas": round(x.total / 60, 2), "required_rupas": round(x.required / 60, 2),
                        "ratio": round(x.ratio, 2)} for p, x in sb.planets.items()}
        shadbala = {"unit": "virupas (60 to a rupa) unless named", "planets": shadbala, "lords": sb.lords,
                    "tribhaga_lord": sb.tribhaga_lord, "wars": [w.model_dump() for w in sb.wars]}
    bhava = None
    if bb is not None:
        def ranked(rows):
            order = sorted(rows, key=lambda h: -rows[h].rupas)        # rank 1 the strongest of the twelve
            # The madhya is a position: sign and degree within the sign, never a longitude (review F9).
            return {f"H{h}": dict(_r(x.model_dump(), 1), madhya=_pos(x.madhya), rupas=round(x.rupas, 2),
                                  rank_of_12=order.index(h) + 1) for h, x in rows.items()}
        bhava = {"birth_time": bb.birth_time} | {system: ranked(rows) for system, rows in
                                                 (("whole_sign", bb.whole_sign), ("sripati", bb.sripati))}
    pa = chart.panchanga
    return {
        "chart": {"header": _r(chart_header(chart)), "lagna": chart.lagnas.asc_sign_name, "as_of": as_of.isoformat(),
                  "signs": "sign names; houses counted from the lagna's sign unless a basis says otherwise"},
        "constants": constants(),
        "houses": _houses(chart),
        "not_computed": NOT_COMPUTED,
        "planets": _planets(chart),
        "nakshatras": {r["planet"]: _tara_named(r) for r in nakshatra_table(chart)},
        "lagnas": _lagnas(chart),
        "special_points": _special(chart),
        "sensitive": _sensitive(chart),
        "vargas": _vargas(chart),
        "lordship": {p: hs for p, hs in ft.lordship.items()},
        "roles": ft.roles,
        "aspects": {p: [h for q, h in ft.aspects if q == p] for p in dict.fromkeys(q for q, _ in ft.aspects)},
        "dispositors": _dispositors(chart),
        "jaimini": {"scheme": ft.jaimini.scheme, "karakas": ft.jaimini.karakas, "karakas_7": ft.jaimini.karakas_7,
                    "karakamsa": SIGNS[ft.jaimini.karakamsa],
                    "arudhas": {k: SIGNS[v] for k, v in ft.jaimini.arudhas.items()}},
        "ashtakavarga": {"signs": "lists run Aries to Pisces", "BAV": av.BAV, "SAV": av.SAV, "trikona": av.trikona,
                         "ekadhipatya": av.ekadhipatya, "sodhya_pinda": {p: x.model_dump() for p, x in av.pinda.items()},
                         "kakshya": av.kakshya, "kakshya_bindu": av.kakshya_bindu},
        "shadbala": shadbala,
        "bhava_bala": bhava,
        "vimsopaka": _r(ft.vimsopaka, 2),
        "ishta_kashta": ({p: _r(x.model_dump(), 2) for p, x in ft.ishta_kashta.items()} if ft.ishta_kashta else None),
        "argala": {k: _r(v.model_dump()) for k, v in ft.argala.items()},
        "sudarshana_h10": ft.sudarshana_h10,
        "panchanga": pa.model_dump() if pa is not None else None,
        "rules": _rules(chart),
        "areas": _areas(chart),
        "driver": _r(chart.scored.driver.model_dump()) if chart.scored else None,
        "vimshottari": _vimshottari(chart, as_of),
        "yogini": _listed(chart, "yogini", as_of),
        "chara": _listed(chart, "chara", as_of) | {"variant": chart.meta.chara_variant},
        "period_quality": _period_quality(chart),
        "transits": _transits(chart, start, end),
        "timing": _timing(chart, areas, start, end),
        "stability": _uncertainty(chart),
    }


def dumps(data: dict) -> str:
    """The compact serialisation the writer receives: no indentation, no spaces after separators."""
    return json.dumps(data, separators=(",", ":"), ensure_ascii=False, default=str)


PATH = re.compile(r"^[A-Za-z0-9_+\-@~]+(?:\.[A-Za-z0-9_+\-@~]+)*$")


def resolve(data: Any, path: str) -> Any:
    """The value at `path` (keys joined by dots, a list item by its index); KeyError if there is none."""
    if not PATH.match(path):
        raise KeyError(path)
    node = data
    for part in path.split("."):
        if isinstance(node, dict) and part in node:
            node = node[part]
        elif isinstance(node, list) and part.isdigit() and int(part) < len(node):
            node = node[int(part)]
        else:
            raise KeyError(path)
    return node


def chart_hash(chart: Chart) -> str:
    """SHA-256 of the chart document (the sampler's own run time left out), so a candidate rule
    can be traced to the chart it was written about without its birth data."""
    doc = chart.model_dump_json(exclude={"uncertainty": {"seconds"}})
    return hashlib.sha256(doc.encode()).hexdigest()
