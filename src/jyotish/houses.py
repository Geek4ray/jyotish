"""Bhava (house) placement. Whole sign is the default (`Meta.house_system`); Sripati is
the bhava-chalit alternative used for house-robustness (SPEC Layer 1b).

Sripati: the four kendra madhyas are the ascendant, the IC, the descendant and the MC;
each quadrant between them is trisected for the other eight madhyas; the sandhis
(house boundaries) are the midpoints between neighbouring madhyas. A planet is in the
bhava whose sandhis enclose it, and a bhava's lord is the lord of the sign on its madhya.
Source: Sripati Paddhati as commonly summarised; the verse locus is not checked here."""

from __future__ import annotations

from .constants import SEVEN, SIGN_LORD

HOUSE_SYSTEMS = ("whole_sign", "sripati")


def _arc(a: float, b: float) -> float:
    """Forward arc from a to b, 0-360."""
    return (b - a) % 360.0


def sripati_madhyas(asc: float, mc: float) -> list[float]:
    """Twelve bhava madhyas, index 0 = house 1 (the ascendant), in increasing longitude."""
    ic, desc = (mc + 180.0) % 360.0, (asc + 180.0) % 360.0
    out = []
    for start, end in ((asc, ic), (ic, desc), (desc, mc), (mc, asc)):
        span = _arc(start, end)
        out += [(start + span * k / 3.0) % 360.0 for k in range(3)]
    return out


def sripati_sandhis(madhyas: list[float]) -> list[float]:
    """Sandhi k (index k-1) is the end of house k: midway from madhya k to madhya k+1."""
    return [(m + _arc(m, madhyas[(i + 1) % 12]) / 2.0) % 360.0 for i, m in enumerate(madhyas)]


def bhava_of(lon: float, madhyas: list[float]) -> int:
    sandhis = sripati_sandhis(madhyas)
    for k in range(12):
        start, end = sandhis[k - 1], sandhis[k]   # house k+1 runs from sandhi k to sandhi k+1
        if _arc(start, lon % 360.0) < _arc(start, end):
            return k + 1
    raise AssertionError("sandhis do not cover the circle")


def bhava_lordships(madhyas: list[float]) -> dict[str, list[int]]:
    """Houses each of the seven rules: the lord of the sign on each madhya."""
    out: dict[str, list[int]] = {p: [] for p in SEVEN}
    for h, m in enumerate(madhyas, start=1):
        out[SIGN_LORD[int(m // 30) % 12]].append(h)
    return out
