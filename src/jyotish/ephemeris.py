"""Swiss Ephemeris wrapper: sidereal positions, ayanamsa, lagna and cusps.

Uses the built-in Moshier model (no data files) by default; set JYOTISH_EPHE_PATH to a
directory of Swiss Ephemeris files for full precision. Licensing: Swiss Ephemeris is
AGPL-3.0 or a paid Astrodienst licence (see SPEC.md, Tech stack)."""

from __future__ import annotations

import os
from dataclasses import dataclass

import swisseph as swe

AYANAMSAS = {
    "lahiri": swe.SIDM_LAHIRI,
    "raman": swe.SIDM_RAMAN,
    "kp": swe.SIDM_KRISHNAMURTI,
    "true_chitrapaksha": swe.SIDM_TRUE_CITRA,
}

BODY_IDS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN,
}

_ephe_path = os.environ.get("JYOTISH_EPHE_PATH")
if _ephe_path:
    swe.set_ephe_path(_ephe_path)
    _BASE_FLAGS = swe.FLG_SWIEPH | swe.FLG_SPEED
else:
    _BASE_FLAGS = swe.FLG_MOSEPH | swe.FLG_SPEED


@dataclass(frozen=True)
class BodyPosition:
    lon: float      # sidereal, 0-360
    speed: float    # degrees/day, negative when retrograde
    retro: bool


@dataclass(frozen=True)
class Sky:
    jd_ut: float
    ayanamsa: str
    ayanamsa_value: float
    bodies: dict[str, BodyPosition]
    asc: float | None            # sidereal ascendant, None when no place given
    mc: float | None
    cusps_placidus: list[float]  # 12 sidereal cusps (1-based list index 0 = cusp 1), empty when no place


def julian_day(year: int, month: int, day: int, hour_ut: float) -> float:
    return swe.julday(year, month, day, hour_ut, swe.GREG_CAL)


def ayanamsa_value(jd_ut: float, ayanamsa: str = "lahiri") -> float:
    swe.set_sid_mode(AYANAMSAS[ayanamsa], 0, 0)
    return swe.get_ayanamsa_ut(jd_ut)


def compute_sky(jd_ut: float, lat: float | None = None, lon: float | None = None,
                ayanamsa: str = "lahiri", true_node: bool = True) -> Sky:
    swe.set_sid_mode(AYANAMSAS[ayanamsa], 0, 0)
    flags = _BASE_FLAGS | swe.FLG_SIDEREAL
    bodies: dict[str, BodyPosition] = {}
    for name, bid in BODY_IDS.items():
        pos, _ = swe.calc_ut(jd_ut, bid, flags)
        bodies[name] = BodyPosition(pos[0] % 360.0, pos[3], pos[3] < 0)
    node_id = swe.TRUE_NODE if true_node else swe.MEAN_NODE
    pos, _ = swe.calc_ut(jd_ut, node_id, flags)
    rahu = pos[0] % 360.0
    bodies["Rahu"] = BodyPosition(rahu, pos[3], True)
    bodies["Ketu"] = BodyPosition((rahu + 180.0) % 360.0, pos[3], True)

    asc = mc = None
    cusps_sid: list[float] = []
    if lat is not None and lon is not None:
        cusps, ascmc = swe.houses_ex(jd_ut, lat, lon, b"P", swe.FLG_SIDEREAL)
        asc, mc = ascmc[0] % 360.0, ascmc[1] % 360.0
        cusps_sid = [c % 360.0 for c in cusps[:12]]
    return Sky(jd_ut, ayanamsa, swe.get_ayanamsa_ut(jd_ut), bodies, asc, mc, cusps_sid)


def sunrise_sunset(jd_ut: float, lat: float, lon: float) -> tuple[float, float]:
    """Julian days of the sunrise before-or-at and the sunset after the given moment's
    local day, for panchanga day/night birth and the vara."""
    geopos = (lon, lat, 0.0)
    _, t_rise = swe.rise_trans(jd_ut - 1.0, swe.SUN, swe.CALC_RISE, geopos, flags=_BASE_FLAGS & ~swe.FLG_SPEED)
    rise = t_rise[0]
    if rise > jd_ut:
        _, t_rise = swe.rise_trans(jd_ut - 2.0, swe.SUN, swe.CALC_RISE, geopos, flags=_BASE_FLAGS & ~swe.FLG_SPEED)
        rise = t_rise[0]
    _, t_set = swe.rise_trans(rise, swe.SUN, swe.CALC_SET, geopos, flags=_BASE_FLAGS & ~swe.FLG_SPEED)
    return rise, t_set[0]


def next_sunrise(after_jd: float, lat: float, lon: float) -> float:
    """Julian day of the first sunrise after `after_jd` (the end of a birth night)."""
    geopos = (lon, lat, 0.0)
    _, t_rise = swe.rise_trans(after_jd, swe.SUN, swe.CALC_RISE, geopos, flags=_BASE_FLAGS & ~swe.FLG_SPEED)
    return t_rise[0]


def recover_instant(targets: dict[str, float], year_from: int, year_to: int,
                    ayanamsa: str = "lahiri", tolerance_deg: float = 0.1) -> list[float]:
    """Find Julian days in [year_from, year_to] at which the given sidereal longitudes
    (at least Sun and Moon; slow planets narrow the year) all hold. Used to recover the
    UTC instant of a chart from a printed position table."""
    swe.set_sid_mode(AYANAMSAS[ayanamsa], 0, 0)
    flags = _BASE_FLAGS | swe.FLG_SIDEREAL

    def lon_of(jd: float, body: str) -> float:
        bid = BODY_IDS.get(body, swe.TRUE_NODE)
        v = swe.calc_ut(jd, bid, flags)[0][0] % 360.0
        return (v + 180.0) % 360.0 if body == "Ketu" else v

    def diff(a: float, b: float) -> float:
        return abs((a - b + 180.0) % 360.0 - 180.0)

    sun_t = targets["Sun"] % 360.0
    moon_t = targets.get("Moon")
    slow = {b: v for b, v in targets.items() if b in ("Jupiter", "Saturn", "Rahu", "Ketu")}
    found: list[float] = []
    for year in range(year_from, year_to + 1):
        jd0 = julian_day(year, 1, 1, 0.0)
        prev = (lon_of(jd0, "Sun") - sun_t) % 360.0
        for day in range(1, 367):
            jd2 = jd0 + day
            cur = (lon_of(jd2, "Sun") - sun_t) % 360.0
            if prev > 300.0 and cur < 60.0:  # Sun crossed the target longitude today
                lo, hi = jd2 - 1, jd2
                for _ in range(30):
                    mid = (lo + hi) / 2
                    if (lon_of(mid, "Sun") - sun_t) % 360.0 > 300.0:
                        lo = mid
                    else:
                        hi = mid
                jd_sun = (lo + hi) / 2
                # Slow planets rule the year in or out at the Sun crossing (2° allows ephemeris
                # and ayanamsa differences between programs).
                if slow and any(diff(lon_of(jd_sun, b), v) > 2.0 for b, v in slow.items()):
                    break
                if moon_t is None:
                    found.append(jd_sun)
                    break
                # The Sun moves ~1°/day and the Moon ~13°/day: within the tolerance window
                # around jd_sun, solve the Moon by bisection on its longitude difference.
                window = tolerance_deg / 1.0  # days the Sun stays within tolerance
                lo, hi = jd_sun - window, jd_sun + window
                m_lo = (lon_of(lo, "Moon") - moon_t + 180.0) % 360.0 - 180.0
                m_hi = (lon_of(hi, "Moon") - moon_t + 180.0) % 360.0 - 180.0
                if m_lo <= 0.0 <= m_hi:
                    for _ in range(30):
                        mid = (lo + hi) / 2
                        if (lon_of(mid, "Moon") - moon_t + 180.0) % 360.0 - 180.0 < 0.0:
                            lo = mid
                        else:
                            hi = mid
                    t = (lo + hi) / 2
                    if all(diff(lon_of(t, b), v) < 1.0 for b, v in slow.items()):
                        found.append(t)
                break
            prev = cur
    return found
