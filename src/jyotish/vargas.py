"""Divisional charts (vargas). Each function maps a sidereal longitude (0-360) to the
sign index (0 = Aries) of the division. Rules follow BPHS ch. 6 unless noted.

All sixteen Parashari vargas plus D11 (Rudramsa). D150 (Nadiamsa) is in the
rectification tier and is a plain 150-fold count."""

from __future__ import annotations

from .constants import AIR, DUAL, EARTH, FIRE, FIXED, MOVABLE, WATER, is_odd_sign


def _split(lon: float):
    lon = lon % 360.0
    sign = int(lon // 30)
    deg = lon - 30 * sign
    return sign, deg


def _part(deg: float, n: int) -> int:
    k = int(deg / (30.0 / n))
    return min(k, n - 1)


def d1(lon):
    return _split(lon)[0]


def d2(lon):
    """Hora: odd signs Sun's hora (Leo) first; even signs Moon's hora (Cancer) first."""
    sign, deg = _split(lon)
    first_half = deg < 15.0
    sun_first = is_odd_sign(sign)
    return 4 if (first_half == sun_first) else 3


def d3(lon):
    sign, deg = _split(lon)
    return (sign + 4 * _part(deg, 3)) % 12


def d4(lon):
    sign, deg = _split(lon)
    return (sign + 3 * _part(deg, 4)) % 12


def d7(lon):
    sign, deg = _split(lon)
    start = sign if is_odd_sign(sign) else (sign + 6) % 12
    return (start + _part(deg, 7)) % 12


def d9(lon):
    sign, deg = _split(lon)
    if sign in MOVABLE:
        start = sign
    elif sign in FIXED:
        start = (sign + 8) % 12
    else:
        start = (sign + 4) % 12
    return (start + _part(deg, 9)) % 12


def d10(lon):
    sign, deg = _split(lon)
    start = sign if is_odd_sign(sign) else (sign + 8) % 12
    return (start + _part(deg, 10)) % 12


def d11(lon):
    """Rudramsa: counted from the 12th sign from the sign, moving backwards.
    Convention varies between texts; this follows BPHS 6.26 as read by Rath."""
    sign, deg = _split(lon)
    start = (sign + 11) % 12
    return (start - _part(deg, 11)) % 12


def d12(lon):
    sign, deg = _split(lon)
    return (sign + _part(deg, 12)) % 12


def d16(lon):
    sign, deg = _split(lon)
    start = 0 if sign in MOVABLE else (4 if sign in FIXED else 8)
    return (start + _part(deg, 16)) % 12


def d20(lon):
    sign, deg = _split(lon)
    start = 0 if sign in MOVABLE else (8 if sign in FIXED else 4)
    return (start + _part(deg, 20)) % 12


def d24(lon):
    sign, deg = _split(lon)
    start = 4 if is_odd_sign(sign) else 3
    return (start + _part(deg, 24)) % 12


def d27(lon):
    sign, deg = _split(lon)
    start = 0 if sign in FIRE else (3 if sign in EARTH else (6 if sign in AIR else 9))
    return (start + _part(deg, 27)) % 12


_D30_ODD = [(5.0, 0), (10.0, 10), (18.0, 8), (25.0, 2), (30.0, 6)]   # Mars, Saturn, Jupiter, Mercury, Venus
_D30_EVEN = [(5.0, 1), (12.0, 5), (20.0, 11), (25.0, 9), (30.0, 7)]  # Venus, Mercury, Jupiter, Saturn, Mars


def d30(lon):
    sign, deg = _split(lon)
    table = _D30_ODD if is_odd_sign(sign) else _D30_EVEN
    for upper, target in table:
        if deg < upper:
            return target
    return table[-1][1]


def d40(lon):
    sign, deg = _split(lon)
    start = 0 if is_odd_sign(sign) else 6
    return (start + _part(deg, 40)) % 12


def d45(lon):
    sign, deg = _split(lon)
    start = 0 if sign in MOVABLE else (4 if sign in FIXED else 8)
    return (start + _part(deg, 45)) % 12


def d60(lon):
    sign, deg = _split(lon)
    return (sign + _part(deg, 60)) % 12


def d150(lon):
    sign, deg = _split(lon)
    return (sign + _part(deg, 150)) % 12


VARGAS = {
    "D1": d1, "D2": d2, "D3": d3, "D4": d4, "D7": d7, "D9": d9, "D10": d10, "D11": d11,
    "D12": d12, "D16": d16, "D20": d20, "D24": d24, "D27": d27, "D30": d30, "D40": d40,
    "D45": d45, "D60": d60,
}
PRODUCTION_VARGAS = [k for k in VARGAS if k != "D150"]


def all_vargas(lon: float) -> dict[str, int]:
    return {name: fn(lon) for name, fn in VARGAS.items()}


def is_vargottama(lon: float) -> bool:
    return d1(lon) == d9(lon)


def d60_index(lon: float) -> int:
    """0-59 shashtiamsa index within the sign, for deity lookup."""
    return _part(_split(lon)[1], 60)
