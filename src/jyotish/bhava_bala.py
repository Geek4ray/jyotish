"""Bhava Bala, BPHS 27.26-31 (Santhanam 1984, read in the archive.org scan), in virupas,
for whole-sign madhyas (equal houses from the lagna degree, so each madhya sits in its
house's sign) and for Sripati madhyas (houses.py).

Total = Bhavadhipati (the lord's Shadbala) + Dig + Drishti + occupants + time of birth.
  - Dig: the madhya's distance from the descendant, IC, ascendant or MC, chosen by the
    madhya's sign (constants.BHAVA_DIG_POINT), folded to 0-180 and divided by 3.
  - Drishti: each of the seven's sphuta drishti on the madhya (shadbala.drishti). A
    benefic's adds a quarter, a malefic's takes a quarter, Jupiter's and Mercury's are
    added in full. Benefics are shadbala.natural_benefics, so a Mercury malefic by
    association counts as a malefic here too.
  - Occupants (27.30): +60 for each of Jupiter and Mercury in the bhava, -60 for each of
    Saturn, Mars and the Sun.
  - Time (27.31): +15 for a bhava in a head-rising sign at a day birth, a dual sign at a
    twilight birth, a back-rising sign at a night birth (constants.RISING_SIGNS)."""

from __future__ import annotations

from .constants import (
    BHAVA_DIG_POINT, BHAVA_OCCUPANT, BHAVA_TIME_BONUS, DUAL_SIGNS, RISING_SIGNS, SEVEN,
    SIGN_LORD,
)
from .houses import bhava_of
from .shadbala import _fold, drishti, natural_benefics


def whole_sign_madhyas(asc: float) -> list[float]:
    return [(asc + 30.0 * k) % 360.0 for k in range(12)]


def dig_point(madhya: float) -> str:
    sign = int(madhya // 30) % 12
    half = int((madhya % 30) // 15)
    return BHAVA_DIG_POINT.get(sign) or BHAVA_DIG_POINT[(sign, half)]


def birth_time_class(jd: float, sunrise: float, sunset: float, next_sunrise: float,
                     twilight_minutes: float) -> str:
    tw = twilight_minutes / 1440.0
    if any(abs(jd - t) <= tw for t in (sunrise, sunset, next_sunrise)):
        return "twilight"
    return "day" if sunrise <= jd < sunset else "night"


def time_bonus(sign: int, when: str, rising: str) -> float:
    r = RISING_SIGNS[rising]
    if when == "twilight":
        return BHAVA_TIME_BONUS if sign in DUAL_SIGNS else 0.0
    wanted = r["head"] if when == "day" else r["back"]
    return BHAVA_TIME_BONUS if sign in wanted or sign in r["both"] else 0.0


def bhava_strengths(madhyas: list[float], house_of_planet: dict[str, int], *,
                    positions: dict[str, float], asc: float, mc: float,
                    shadbala_totals: dict[str, float], when: str, rising: str,
                    mercury_nature: str) -> dict[int, dict[str, float | str]]:
    points = {"asc": asc, "desc": asc + 180.0, "mc": mc, "ic": mc + 180.0}
    benefics = natural_benefics(positions, mercury_nature)
    out = {}
    for h, m in enumerate(madhyas, start=1):
        sign = int(m // 30) % 12
        lord = SIGN_LORD[sign]
        dig = _fold(m - points[dig_point(m)]) / 3.0
        dr = 0.0
        for p in SEVEN:
            v = drishti(p, m - positions[p])
            if p in benefics:
                dr += v if p in ("Jupiter", "Mercury") else v / 4.0
            else:
                dr -= v / 4.0
        occ = sum(BHAVA_OCCUPANT.get(p, 0.0) for p in SEVEN if house_of_planet[p] == h)
        tb = time_bonus(sign, when, rising)
        total = shadbala_totals[lord] + dig + dr + occ + tb
        out[h] = dict(madhya=m, lord=lord, bhavadhipati=shadbala_totals[lord], dig=dig,
                      drishti=dr, occupants=occ, time=tb, total=total, rupas=total / 60.0)
    return out


def bhava_bala(positions: dict[str, float], asc: float, mc: float, sripati: list[float],
               shadbala_totals: dict[str, float], *, jd: float, sunrise: float, sunset: float,
               next_sunrise: float, rising: str = "bphs", twilight_minutes: float = 24.0,
               mercury_nature: str = "association") -> dict:
    when = birth_time_class(jd, sunrise, sunset, next_sunrise, twilight_minutes)
    lagna = int(asc // 30)
    whole_houses = {p: (int(positions[p] // 30) - lagna) % 12 + 1 for p in SEVEN}
    sripati_houses = {p: bhava_of(positions[p], sripati) for p in SEVEN}
    kw = dict(positions=positions, asc=asc, mc=mc, shadbala_totals=shadbala_totals,
              when=when, rising=rising, mercury_nature=mercury_nature)
    return {"birth_time": when,
            "whole_sign": bhava_strengths(whole_sign_madhyas(asc), whole_houses, **kw),
            "sripati": bhava_strengths(sripati, sripati_houses, **kw)}
