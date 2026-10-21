"""Panchanga at birth: tithi, vara, nakshatra, nitya-yoga, karana and their lords."""

from __future__ import annotations

from dataclasses import dataclass

from .constants import (
    KARANA_NAMES, NAKSHATRA_SPAN, TITHI_LORD_ORDER, VARA_LORDS, YOGA_LORD_ORDER, YOGA_NAMES,
)
from .nakshatra import nakshatra_of


@dataclass(frozen=True)
class Panchanga:
    tithi: int            # 1-30 (1-15 shukla, 16-30 krishna)
    tithi_lord: str
    paksha: str
    vara: int             # 0 = Sunday
    vara_lord: str
    nakshatra: str
    nakshatra_lord: str
    yoga: str
    yoga_lord: str
    karana: str
    day_birth: bool | None


def _vara_from_jd(jd_ut: float, sunrise_jd: float | None) -> int:
    """Weekday counted from the previous sunrise (Vedic day) when sunrise is known,
    else from UT midnight. JD 0 was a Monday; (jd + 1.5) floor mod 7 gives 0 = Sunday."""
    ref = sunrise_jd if sunrise_jd is not None else jd_ut
    return int(ref + 1.5) % 7


def _karana(tithi_index: int, half: int) -> str:
    """Karana for tithi 1-30 and half 0/1. Fixed karanas: Kimstughna (first half of
    tithi 1), Shakuni, Chatushpada, Naga (second half of 29 through first half of 30)."""
    k = (tithi_index - 1) * 2 + half  # 0-59
    if k == 0:
        return "Kimstughna"
    if k == 57:
        return "Shakuni"
    if k == 58:
        return "Chatushpada"
    if k == 59:
        return "Naga"
    return KARANA_NAMES[(k - 1) % 7]


def panchanga(sun_lon: float, moon_lon: float, jd_ut: float,
              sunrise_jd: float | None = None, sunset_jd: float | None = None) -> Panchanga:
    elong = (moon_lon - sun_lon) % 360.0
    tithi = int(elong // 12.0) + 1
    half = int((elong % 12.0) // 6.0)
    paksha = "shukla" if tithi <= 15 else "krishna"
    tithi_lord = TITHI_LORD_ORDER[(tithi - 1) % 15]
    vara = _vara_from_jd(jd_ut, sunrise_jd)
    nak = nakshatra_of(moon_lon)
    yoga_index = int(((sun_lon + moon_lon) % 360.0) // NAKSHATRA_SPAN)
    day_birth = None
    if sunrise_jd is not None and sunset_jd is not None:
        day_birth = sunrise_jd <= jd_ut < sunset_jd
    return Panchanga(
        tithi, tithi_lord, paksha, vara, VARA_LORDS[vara], nak.name, nak.lord,
        YOGA_NAMES[yoga_index], YOGA_LORD_ORDER[yoga_index % 9], _karana(tithi, half), day_birth,
    )
