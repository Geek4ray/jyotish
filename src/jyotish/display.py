"""The chart display (SPEC Layer 6b, order of work item 2): everything the engine computes
exactly, laid out the way a practising astrologer checks it in other software.

`svg(chart)` draws D1, D9 and D10 in the North-Indian style (fixed houses, the lagna at the
top, signs numbered 1 Aries ... 12 Pisces). `tables(chart, as_of)` gives the planet table
(sign, degree, nakshatra and pada, dignity, retrograde, combust, avastha), Vimshottari to the
pratyantar with the current period marked, Shadbala with its six balas and the ratio to the
required strength, Ashtakavarga (BAV per planet and SAV, by sign) and Bhava Bala. Both are
computed from the chart object alone (the stored chart document), never from scoring or
narration, and every value is the chart's own."""

from __future__ import annotations

from datetime import date
from typing import Any
from xml.sax.saxutils import escape

from .constants import SIGNS
from .dasha import vimshottari
from .models import Chart

PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
SEVEN = PLANETS[:7]
ABBR = {"Sun": "Su", "Moon": "Mo", "Mars": "Ma", "Mercury": "Me", "Jupiter": "Ju", "Venus": "Ve",
        "Saturn": "Sa", "Rahu": "Ra", "Ketu": "Ke", "Asc": "Asc"}
DISPLAY_VARGAS = ("D1", "D9", "D10")
VARGA_TITLE = {"D1": "D1 · Rashi (birth chart)", "D9": "D9 · Navamsa", "D10": "D10 · Dasamsa"}

# North-Indian chart, a square of side 300: house -> (planet-text centre, sign-number position).
# House 1 is the top diamond and the houses run counter-clockwise (design/mockups/Main.html).
_S = 300.0
_CENTRE = {1: (150, 80), 2: (75, 38), 3: (38, 75), 4: (80, 150), 5: (38, 225), 6: (75, 262),
           7: (150, 220), 8: (225, 262), 9: (262, 225), 10: (220, 150), 11: (262, 75), 12: (225, 38)}
_NUMBER = {1: (150, 43), 2: (107, 22), 3: (22, 107), 4: (43, 153), 5: (22, 200), 6: (107, 285),
           7: (150, 263), 8: (193, 285), 9: (278, 200), 10: (257, 153), 11: (278, 107), 12: (193, 22)}
COLOURS = {"bg": "#0F1230", "line": "#4A4E80", "number": "#7E82AE", "text": "#F3EEE2", "muted": "#B3B0C4",
           "exalted": "#5ED1B6", "debilitated": "#F28B82", "own": "#E8A33D"}


def dms(deg: float) -> str:
    """Degrees within the sign as d°m′s″ (seconds rounded, carried)."""
    total = round(deg * 3600)
    d, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"{d}°{m:02d}′{s:02d}″"


def _date(jd: float) -> str:
    import swisseph as swe
    y, m, d, _ = swe.revjul(jd, swe.GREG_CAL)
    return f"{y:04d}-{m:02d}-{d:02d}"


def _jd(day: date) -> float:
    import swisseph as swe
    return swe.julday(day.year, day.month, day.day, 0.0)


def placements(chart: Chart, varga: str) -> dict[str, int]:
    """Sign (0 Aries ... 11 Pisces) of the ascendant and the nine grahas in a varga."""
    if varga == "D1":
        out = {p: chart.bodies[p].sign for p in PLANETS}
        out["Asc"] = chart.lagnas.asc_sign
        return out
    v = chart.vargas[varga]
    return {p: v[p] for p in PLANETS} | {"Asc": v["Asc"]}


def house_of_sign(sign: int, lagna: int) -> int:
    return (sign - lagna) % 12 + 1


# --- the SVG ------------------------------------------------------------------------------

def _label(chart: Chart, varga: str, p: str) -> str:
    if varga != "D1":
        return ABBR[p]
    if p == "Asc":
        return f"Asc {int(chart.lagnas.asc % 30)}°"
    b = chart.bodies[p]
    return f"{ABBR[p]} {int(b.deg)}°" + (" R" if b.retro else "") + (" c" if b.combust else "")


def _colour(chart: Chart, varga: str, p: str) -> str:
    if varga != "D1" or p == "Asc":
        return COLOURS["text"] if p != "Asc" else COLOURS["muted"]
    d = chart.bodies[p].dignity
    return {"exalted": COLOURS["exalted"], "debilitated": COLOURS["debilitated"], "own": COLOURS["own"],
            "moolatrikona": COLOURS["own"]}.get(d, COLOURS["text"])


def _one_chart(chart: Chart, varga: str, x0: float) -> str:
    place = placements(chart, varga)
    lagna = place["Asc"]
    s = _S
    out = [f'<g data-varga="{varga}" transform="translate({x0},28)">',
           f'<text x="{s / 2}" y="-10" text-anchor="middle" fill="{COLOURS["muted"]}" font-size="13">'
           f'{escape(VARGA_TITLE[varga])}</text>',
           f'<rect x="0.75" y="0.75" width="{s - 1.5}" height="{s - 1.5}" fill="{COLOURS["bg"]}" '
           f'stroke="{COLOURS["line"]}" stroke-width="1.5"/>',
           f'<path d="M0 0L{s} {s}M{s} 0L0 {s}M{s / 2} 0L{s} {s / 2}L{s / 2} {s}L0 {s / 2}Z" fill="none" '
           f'stroke="{COLOURS["line"]}" stroke-width="1.5"/>']
    for house in range(1, 13):
        sign = (lagna + house - 1) % 12
        nx, ny = _NUMBER[house]
        cx, cy = _CENTRE[house]
        here = [p for p in ["Asc"] + PLANETS if place[p] == sign]
        out.append(f'<g data-house="{house}" data-sign="{sign}">')
        out.append(f'<text x="{nx}" y="{ny + 4}" text-anchor="middle" font-size="11" fill="{COLOURS["number"]}">'
                   f'{sign + 1}</text>')
        top = cy - (len(here) - 1) * 7.5
        for i, p in enumerate(here):
            out.append(f'<text x="{cx}" y="{top + i * 15 + 4:.1f}" text-anchor="middle" font-size="12" '
                       f'font-weight="600" fill="{_colour(chart, varga, p)}" data-planet="{p}" data-sign="{sign}" '
                       f'data-house="{house}">{escape(_label(chart, varga, p))}</text>')
        out.append("</g>")
    out.append("</g>")
    return "\n".join(out)


def svg(chart: Chart, vargas: tuple[str, ...] = DISPLAY_VARGAS) -> str:
    """D1, D9 and D10 (or the `vargas` named, of those) side by side, North-Indian style; each
    planet carries data-varga, data-planet, data-sign (0 Aries ... 11 Pisces) and data-house, so
    the drawing can be checked against the chart object."""
    if not vargas or set(vargas) - set(DISPLAY_VARGAS):
        raise ValueError(f"vargas are drawn from {', '.join(DISPLAY_VARGAS)}")
    gap = 28
    width = int(len(vargas) * _S + (len(vargas) - 1) * gap + 2)
    lines = ["Signs numbered 1 Aries to 12 Pisces · houses fixed, the lagna at the top · D1: degree in sign, "
             "R retrograde, c combust; exalted, own sign and debilitated in colour"]
    if len(vargas) < 3:                       # a narrower drawing: the legend on two lines
        lines = ["Signs numbered 1 Aries to 12 Pisces · houses fixed, the lagna at the top",
                 "D1: degree in sign, R retrograde, c combust; exalted, own sign and debilitated in colour"]
    height = int(_S + 42 + 14 * len(lines))
    lagna = SIGNS[chart.lagnas.asc_sign]
    charts = "\n".join(_one_chart(chart, v, 1 + i * (_S + gap)) for i, v in enumerate(vargas))
    legend = "\n".join(f'<text x="1" y="{height - 6 - 14 * (len(lines) - 1 - i)}" font-size="11" '
                       f'fill="{COLOURS["muted"]}">{escape(t)}</text>' for i, t in enumerate(lines))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
            f'role="img" aria-labelledby="chart-title" font-family="Inter, system-ui, sans-serif">\n'
            f'<title id="chart-title">North-Indian charts {escape(", ".join(vargas[:-1]) + " and " + vargas[-1] if len(vargas) > 1 else vargas[0])}, '
            f'{escape(lagna)} lagna</title>\n'
            f'<rect width="100%" height="100%" fill="{COLOURS["bg"]}"/>\n{charts}\n{legend}\n</svg>\n')


# --- the tables -----------------------------------------------------------------------------

def _vimshottari(chart: Chart, as_of: date) -> dict[str, Any]:
    periods = vimshottari(chart.bodies["Moon"].lon, chart.meta.jd, levels=3, year_length=chart.meta.dasha_year)
    now = _jd(as_of)
    tree: list[dict] = []
    current: list[str] = []
    for p in periods:
        row = {"lords": list(p.lords), "start": _date(max(p.start_jd, chart.meta.jd)) if p.level == 1 else _date(p.start_jd),
               "end": _date(p.end_jd), "current": p.start_jd <= now < p.end_jd}
        if row["current"] and len(p.lords) > len(current):
            current = list(p.lords)
        if p.level == 1:
            tree.append(dict(row, start_true=_date(p.start_jd), antars=[]))
        elif p.level == 2:
            tree[-1]["antars"].append(dict(row, pratyantars=[]))
        else:
            tree[-1]["antars"][-1]["pratyantars"].append(row)
    return {"as_of": as_of.isoformat(), "current": current, "mahas": tree,
            "note": "The first maha starts before birth (start_true); its start is shown as the birth date."}


def tables(chart: Chart, as_of: date | None = None) -> dict[str, Any]:
    as_of = as_of or date.today()
    asc = chart.lagnas
    from .nakshatra import nakshatra_of
    planets = [{"planet": "Ascendant", "sign": SIGNS[asc.asc_sign], "degree": dms(asc.asc % 30),
                "nakshatra": asc.asc_nak, "pada": nakshatra_of(asc.asc).pada, "dignity": None, "retrograde": None, "combust": None,
                "avastha": None}]
    for p in PLANETS:
        b = chart.bodies[p]
        planets.append({"planet": p, "sign": b.sign_name, "degree": dms(b.deg), "nakshatra": b.nak_name,
                        "pada": b.pada, "dignity": b.dignity, "retrograde": b.retro, "combust": b.combust,
                        "avastha": b.avastha_baladi})
    sb = chart.features.shadbala
    shadbala = []
    for p in SEVEN:
        x = sb.planets[p]
        shadbala.append({"planet": p, "sthana": round(x.sthana.total / 60, 2), "dig": round(x.dig / 60, 2),
                         "kala": round(x.kala.total / 60, 2), "chesta": round(x.chesta / 60, 2),
                         "naisargika": round(x.naisargika / 60, 2), "drik": round(x.drik / 60, 2),
                         "total": round(x.total / 60, 2), "required": round(x.required / 60, 2),
                         "ratio": round(x.ratio, 2)})
    av = chart.features.ashtakavarga
    bb = chart.features.bhava_bala.whole_sign
    bhava = [{"house": h, "sign": SIGNS[(asc.asc_sign + h - 1) % 12], "lord": bb[h].lord, "rupas": round(bb[h].rupas, 2)}
             for h in range(1, 13)]
    return {
        "chart": {"lagna": SIGNS[asc.asc_sign], "ascendant_degree": dms(asc.asc % 30), "ascendant_nakshatra": asc.asc_nak,
                  "birth_utc": chart.birth.utc, "ayanamsa": chart.meta.ayanamsa, "node": chart.meta.node,
                  "house_system": chart.meta.house_system, "engine": chart.meta.engine},
        "planets": planets,
        "vimshottari": _vimshottari(chart, as_of),
        "shadbala": {"unit": "rupas (60 virupas)", "rows": shadbala},
        "ashtakavarga": {"signs": list(SIGNS), "bav": {p: list(av.BAV[p]) for p in SEVEN}, "sav": list(av.SAV)},
        "bhava_bala": {"unit": "rupas", "house_system": "whole_sign", "rows": bhava},
    }
