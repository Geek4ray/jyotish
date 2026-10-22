"""The special nakshatra points of SPEC Layer 2 (nakshatra layer), from the Moon and the lagna.

- The 64th navamsa: counting the navamsa (nakshatra pada) a body occupies as the first, the 64th;
  the point is that 3°20' span, with its sign, nakshatra and pada, and its navamsa sign's lord.
- The 88th pada: the same count to 88, which is 87 padas on (21 nakshatras and 3 padas); counted
  from a first pada it is the last pada of the 22nd nakshatra (the Vainashika). SPEC calls it the
  "88th-degree" point; no source we hold defines an 88th degree, so the 88th pada is what is
  computed, and it stays an open reading until a text is named.
- Abhijit: the intercalary nakshatra, the last quarter of Uttara Ashadha and the first fifteenth of
  Shravana (276°40' to 280°53'20''), with the bodies and the lagna inside it.
- The nakshatra lagnesha: the lord of the lagna's nakshatra, with where it stands.
The counts use the `lon * 108 / 360` style of nakshatra._nak_index. The sources are in SOURCES,
none yet checked against its edition."""

from __future__ import annotations

from .constants import GRAHAS, NAKSHATRAS, SIGN_LORD, SIGNS, nakshatra_lord
from .models import AbhijitInfo, NakLagnesha, NakshatraPoints, SpecialPoint

PADA_SPAN_DEG = 10.0 / 3.0
ABHIJIT = (276.0 + 40.0 / 60.0, 280.0 + 53.0 / 60.0 + 20.0 / 3600.0)
SOURCES = {
    "navamsa_64": {"text": "not yet located", "edition": None, "checked": False,
                   "note": "named in SPEC Layer 2; the 64th navamsa from the Moon and the lagna, read with the 22nd "
                           "drekkana as the Khara points; the reader should name the verse"},
    "pada_88": {"text": "not yet located", "edition": None, "checked": False,
                "note": "SPEC Layer 2's 88th-degree point, computed as the 88th pada (the 22nd nakshatra's matching "
                        "quarter); an open reading until a text is named"},
    "abhijit": {"text": "Muhurta Chintamani", "edition": "G.C. Sharma (edition to be confirmed by the reader)",
                "checked": False, "note": "the last quarter of Uttara Ashadha and the first fifteenth of Shravana"},
    "nakshatra_lagnesha": {"text": "KP Readers", "edition": "K.S. Krishnamurti", "checked": False,
                           "note": "the lord of the lagna's nakshatra"},
}


def _pada_index(lon: float) -> int:
    return int((lon % 360.0) * 108.0 / 360.0) % 108


def counted_pada(lon: float, n: int, origin: str) -> SpecialPoint:
    """The n-th pada counted from the pada `lon` falls in (that pada is the first)."""
    k = (_pada_index(lon) + n - 1) % 108
    start = k * PADA_SPAN_DEG
    nav = k % 12                                  # the navamsa sign of the k-th pada from Aries
    return SpecialPoint(origin=origin, count=n, start=start, end=start + PADA_SPAN_DEG, sign=SIGNS[int(start // 30)],
                        nakshatra=NAKSHATRAS[k // 4], pada=k % 4 + 1, nakshatra_lord=nakshatra_lord(k // 4),
                        navamsa_sign=SIGNS[nav], navamsa_lord=SIGN_LORD[nav])


def in_abhijit(lon: float) -> bool:
    return ABHIJIT[0] <= lon % 360.0 < ABHIJIT[1]


def nakshatra_points(positions: dict[str, float], asc: float, bodies: dict) -> NakshatraPoints:
    """`bodies` are the chart's Body objects (for the lagnesha's placement)."""
    origins = {"moon": positions["Moon"], "lagna": asc}
    lord = nakshatra_lord(int(asc * 27.0 / 360.0) % 27)
    b = bodies[lord]
    inside = [p for p in GRAHAS if in_abhijit(positions[p])] + (["Asc"] if in_abhijit(asc) else [])
    return NakshatraPoints(
        navamsa_64={k: counted_pada(v, 64, k) for k, v in origins.items()},
        pada_88={k: counted_pada(v, 88, k) for k, v in origins.items()},
        abhijit=AbhijitInfo(start=ABHIJIT[0], end=ABHIJIT[1], occupants=inside),
        nakshatra_lagnesha=NakLagnesha(planet=lord, lagna_nakshatra=NAKSHATRAS[int(asc * 27.0 / 360.0) % 27],
                                       sign=b.sign_name, house=b.house, nakshatra=b.nak_name, dignity=b.dignity),
        sources=SOURCES)
