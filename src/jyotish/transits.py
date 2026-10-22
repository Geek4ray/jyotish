"""Transits (gochara), SPEC Layer 4: a timeline of tagged rows for Saturn, Jupiter, Rahu,
Ketu, Mars and the Sun over a date range, read against a natal chart.

Each row is one body in one sign. Sign ingresses are found by daily sampling and refined
by bisection to under a minute; a retrograde re-entry starts a row of its own. Every row
carries the sign's house from the lagna, the Moon and the Sun, the transiting planet's
own BAV there and the SAV, the Kakshya spans (refined the same way), Vedha and Vipareeta
Vedha spans from the Moon, and, for slow planets entering a sign, the Murthi class. The
named windows (Sade Sati with Ashtakavarga grading, Kantaka and Ashtama Shani, Jupiter over
1/5/9/11 from the Moon, nodal and Saturn returns) are built from those rows.

Tara rows (SPEC Layer 2, Navatara "transit": slow planets crossing adverse taras, the daily Tara
bala), in `tara_rows`: Saturn, Jupiter, Rahu and Ketu entering a nakshatra whose tara from the
natal Moon is Vipat, Pratyak or Vadha, and every Moon nakshatra span with its tara. They are
tagged and not yet scored: the timing join leaves them out (`taras=False`).

Sampling is daily, so two crossings of one boundary less than a day apart (a planet
stationary on a sign or Kakshya edge) are not resolved; for these bodies that is rare.
Positions follow the chart's ayanamsa and node setting."""

from __future__ import annotations

import swisseph as swe

from .ashtakavarga import prastara
from .constants import (
    GOCHARA_VEDHA, GRAHAS, KAKSHYA_LORDS, MURTHI, NAKSHATRAS, SEVEN, SIGNS, VEDHA_EXEMPT,
    ashtakavarga_grade,
)
from .dignity import house_of
from .ephemeris import _BASE_FLAGS, AYANAMSAS, BODY_IDS
from .models import Chart, KakshyaSpan, TaraRow, Timeline, TimelineWindow, TransitRow, VedhaSpan

TRANSIT_BODIES = ["Saturn", "Jupiter", "Rahu", "Ketu", "Mars", "Sun"]
SLOW = {"Saturn", "Jupiter", "Rahu", "Ketu"}
# Mean sidereal periods; a return is looked for only half a period after birth.
RETURN_PERIOD_YEARS = {"Saturn": 29.46, "Rahu": 18.61}
MINUTE = 1.0 / 1440.0
STEP = 1.0   # days between samples


class Sky:
    """Sidereal longitudes for the chart's ayanamsa and node type."""

    def __init__(self, ayanamsa: str, true_node: bool):
        self.mode = AYANAMSAS[ayanamsa]
        self.node = swe.TRUE_NODE if true_node else swe.MEAN_NODE
        self.flags = (_BASE_FLAGS & ~swe.FLG_SPEED) | swe.FLG_SIDEREAL

    def lon(self, body: str, jd: float) -> float:
        swe.set_sid_mode(self.mode, 0, 0)
        if body in ("Rahu", "Ketu"):
            v = swe.calc_ut(jd, self.node, self.flags)[0][0]
            return (v + (180.0 if body == "Ketu" else 0.0)) % 360.0
        return swe.calc_ut(jd, BODY_IDS[body], self.flags)[0][0] % 360.0


def _index(lon: float, parts: int) -> int:
    """Sign (parts=12) or Kakshya (parts=96) index; parts * lon / 360 as elsewhere."""
    return int(lon * parts / 360.0) % parts


def crossings(sky: Sky, body: str, start: float, end: float, parts: int = 12, step: float = STEP):
    """(jd, index before, index after) for each change of the index in [start, end],
    each to within half a minute. `step` must be shorter than the body's time in one index."""
    out = []
    t = start
    i0 = _index(sky.lon(body, t), parts)
    while t < end:
        t2 = min(t + step, end)
        i2 = _index(sky.lon(body, t2), parts)
        if i2 == i0:
            t = t2
            continue
        lo, hi = t, t2
        while hi - lo > MINUTE:
            mid = (lo + hi) / 2.0
            if _index(sky.lon(body, mid), parts) == i0:
                lo = mid
            else:
                hi = mid
        after = _index(sky.lon(body, hi), parts)
        out.append(((lo + hi) / 2.0, i0, after))
        t, i0 = hi, after
    return out


def segments(sky: Sky, body: str, start: float, end: float, parts: int = 12, step: float = STEP):
    """Constant-index spans covering [start, end]: (index, t0, t1, entered) where entered
    is "direct", "retrograde" or None for the span clipped at `start`."""
    out, t0, entered = [], start, None
    i = _index(sky.lon(body, start), parts)
    for jd, before, after in crossings(sky, body, start, end, parts, step):
        out.append((before, t0, jd, entered))
        entered = "direct" if (after - before) % parts == 1 else "retrograde"
        t0, i = jd, after
    out.append((i, t0, end, entered))
    return out


def _clip_spans(spans, t0, t1):
    return [(by, max(a, t0), min(b, t1)) for by, a, b in spans if b > t0 and a < t1]


def _exempt(a: str, b: str) -> bool:
    return any({a, b} == pair for pair in VEDHA_EXEMPT)


def _occupants(occupancy, sign: int, t0: float, t1: float, body: str) -> list[VedhaSpan]:
    """Spans in [t0, t1] during which another planet (not exempt with `body`) is in `sign`."""
    spans = []
    for other, segs in occupancy.items():
        if other == body or _exempt(body, other):
            continue
        for s, a, b, _ in segs:
            if s == sign and b > t0 and a < t1:
                spans.append(VedhaSpan(by=other, start_jd=max(a, t0), end_jd=min(b, t1)))
    return sorted(spans, key=lambda v: (v.start_jd, v.by))


def exact_returns(sky: Sky, body: str, target: float, start: float, end: float) -> list[float]:
    """Instants the body's longitude equals `target`, to within half a minute."""
    def f(t):
        return (sky.lon(body, t) - target + 180.0) % 360.0 - 180.0
    out, t, f0 = [], start, f(start)
    while t < end:
        t2 = min(t + STEP, end)
        f2 = f(t2)
        if (f0 < 0) != (f2 < 0) and abs(f0) < 90 and abs(f2) < 90:
            lo, hi, flo = t, t2, f0
            while hi - lo > MINUTE:
                mid = (lo + hi) / 2.0
                fm = f(mid)
                if (fm < 0) == (flo < 0):
                    lo, flo = mid, fm
                else:
                    hi = mid
            out.append((lo + hi) / 2.0)
        t, f0 = t2, f2
    return out


TARA_SLOW = ["Saturn", "Jupiter", "Rahu", "Ketu"]
MOON_STEP = 0.25      # days: the Moon spends at least 21 hours in a nakshatra


def tara_rows(chart: Chart, sky: Sky, start_jd: float, end_jd: float) -> list[TaraRow]:
    """Slow planets entering an adverse tara from the natal Moon, and the Moon's daily tara."""
    from .nakshatra import navatara
    moon = chart.bodies["Moon"].nak
    out = []
    for body, step in [(b, STEP) for b in TARA_SLOW] + [("Moon", MOON_STEP)]:
        for k, t0, t1, entered in segments(sky, body, start_jd, end_jd, parts=27, step=step):
            t = navatara(k, moon)
            if body != "Moon" and (not t.adverse or entered is None):
                continue
            out.append(TaraRow(body=body, nakshatra=NAKSHATRAS[k], tara=t.name, count=t.count, cycle=t.cycle,
                               adverse=t.adverse, special=t.special, start_jd=t0, end_jd=t1, entered=entered,
                               clipped_start=entered is None, clipped_end=t1 == end_jd,
                               tags=[f"body:{body}", f"tara:{t.name.lower()}"] + (["adverse"] if t.adverse else [])
                                    + (["daily"] if body == "Moon" else [])))
    out.sort(key=lambda r: (r.start_jd, r.body != "Moon"))
    return out


def transit_timeline(chart: Chart, start_jd: float, end_jd: float, taras: bool = True) -> Timeline:
    if end_jd <= start_jd:
        raise ValueError("end must be after start")
    sky = Sky(chart.meta.ayanamsa, chart.meta.node == "true")
    av = chart.features.ashtakavarga
    natal_signs = {p: chart.bodies[p].sign for p in SEVEN} | {"Asc": chart.lagnas.asc_sign}
    basis = {"lagna": chart.lagnas.asc_sign, "moon": chart.bodies["Moon"].sign,
             "sun": chart.bodies["Sun"].sign}
    moon_sign = basis["moon"]

    occupancy = {b: segments(sky, b, start_jd, end_jd) for b in GRAHAS}
    rows: list[TransitRow] = []
    for body in TRANSIT_BODIES:
        grid = prastara(body, natal_signs) if body in av.BAV else None
        kak = segments(sky, body, start_jd, end_jd, parts=96)
        for sign, t0, t1, entered in occupancy[body]:
            h_moon = house_of(sign, moon_sign)
            table = GOCHARA_VEDHA[body]
            bav = av.BAV[body][sign] if body in av.BAV else None
            kspans = []
            for k, a, b, _ in kak:
                if b > t0 and a < t1 and k // 8 == sign:
                    lord = KAKSHYA_LORDS[k % 8]
                    kspans.append(KakshyaSpan(lord=lord, start_jd=max(a, t0), end_jd=min(b, t1),
                                              bindu=bool(grid[lord][sign]) if grid else None))
            vedha = (_occupants(occupancy, (moon_sign + table[h_moon] - 1) % 12, t0, t1, body)
                     if h_moon in table else [])
            relieving = [g for g, v in table.items() if v == h_moon]
            vipareeta = []
            for g in relieving:
                vipareeta += _occupants(occupancy, (moon_sign + g - 1) % 12, t0, t1, body)
            murthi = None
            if body in SLOW and entered is not None:
                murthi = MURTHI[house_of(_index(sky.lon("Moon", t0), 12), moon_sign)]
            rows.append(TransitRow(
                body=body, sign=sign, sign_name=SIGNS[sign], start_jd=t0, end_jd=t1,
                entered=entered, clipped_start=entered is None, clipped_end=t1 == end_jd,
                houses={k: house_of(sign, s) for k, s in basis.items()}, bav=bav,
                sav=av.SAV[sign], grade=ashtakavarga_grade(bav) if bav is not None else None,
                gochara_good=h_moon in table, kakshya=kspans, vedha=vedha,
                vipareeta_vedha=sorted(vipareeta, key=lambda v: (v.start_jd, v.by)),
                murthi=murthi,
                tags=[f"body:{body}", f"house_moon:{h_moon}"] + ([f"murthi:{murthi}"] if murthi else [])))
    rows.sort(key=lambda r: (r.start_jd, TRANSIT_BODIES.index(r.body)))
    return Timeline(start_jd=start_jd, end_jd=end_jd, ayanamsa=chart.meta.ayanamsa,
                    node=chart.meta.node, rows=rows, windows=_windows(chart, sky, rows, start_jd, end_jd),
                    tara_rows=tara_rows(chart, sky, start_jd, end_jd) if taras else [])


SADE_SATI_PHASE = {12: "rising", 1: "peak", 2: "setting"}


def _windows(chart: Chart, sky: Sky, rows: list[TransitRow], start: float, end: float):
    out: list[TimelineWindow] = []
    saturn = [r for r in rows if r.body == "Saturn"]

    # Sade Sati: each unbroken run of Saturn through the 12th, 1st and 2nd from the Moon.
    run: list[TransitRow] = []
    for r in saturn + [None]:
        if r is not None and r.houses["moon"] in SADE_SATI_PHASE:
            run.append(r)
            continue
        if run:
            phases = [{"phase": SADE_SATI_PHASE[x.houses["moon"]], "sign": x.sign_name,
                       "start_jd": x.start_jd, "end_jd": x.end_jd, "bav": x.bav, "sav": x.sav,
                       "grade": x.grade} for x in run]
            out.append(TimelineWindow(
                kind="sade_sati", start_jd=run[0].start_jd, end_jd=run[-1].end_jd,
                tags=["sade_sati"] + sorted({f"grade:{p['grade']}" for p in phases}),
                details={"phases": phases}))
            run = []

    for r in saturn:
        h = r.houses["moon"]
        if h in (4, 7, 10):
            out.append(TimelineWindow(kind="kantaka_shani", start_jd=r.start_jd, end_jd=r.end_jd,
                                      tags=["kantaka_shani", f"house_moon:{h}", f"grade:{r.grade}"],
                                      details={"sign": r.sign_name, "bav": r.bav, "sav": r.sav}))
        elif h == 8:
            out.append(TimelineWindow(kind="ashtama_shani", start_jd=r.start_jd, end_jd=r.end_jd,
                                      tags=["ashtama_shani", f"grade:{r.grade}"],
                                      details={"sign": r.sign_name, "bav": r.bav, "sav": r.sav}))

    for r in rows:
        if r.body == "Jupiter" and r.houses["moon"] in (1, 5, 9, 11):
            out.append(TimelineWindow(kind="jupiter_1_5_9_11", start_jd=r.start_jd, end_jd=r.end_jd,
                                      tags=["jupiter_1_5_9_11", f"house_moon:{r.houses['moon']}",
                                            f"grade:{r.grade}"],
                                      details={"sign": r.sign_name, "bav": r.bav, "sav": r.sav}))

    # Returns: the body back in its natal sign at least half a revolution after birth, with
    # the exact instants it crosses its natal longitude. Needs the birth moment.
    birth = chart.meta.jd
    for body, kind in (("Rahu", "nodal_return"), ("Saturn", "saturn_return")):
        if birth is None:
            break
        natal = chart.bodies[body]
        earliest = birth + RETURN_PERIOD_YEARS[body] * 365.25 / 2.0
        exact = exact_returns(sky, body, natal.lon, max(start, earliest), end)
        for r in rows:
            if r.body == body and r.sign == natal.sign and r.end_jd > earliest:
                hits = [t for t in exact if r.start_jd <= t < r.end_jd]
                out.append(TimelineWindow(kind=kind, start_jd=r.start_jd, end_jd=r.end_jd,
                                          tags=[kind], details={"sign": r.sign_name, "exact_jd": hits}))
    return sorted(out, key=lambda w: (w.start_jd, w.kind))
