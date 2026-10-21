"""The reference chart from SPEC.md (Taurus lagna). Longitudes are the app's printed
sidereal positions (Lahiri). This is the Phase 1 acceptance target: `analyse` on these
longitudes must reproduce every value in SPEC.md's worked example."""

from __future__ import annotations


def dms(d: int, m: int, s: float = 0.0) -> float:
    return d + m / 60.0 + s / 3600.0


# sign index * 30 + degree within sign
REFERENCE_POSITIONS = {
    "Sun": 10 * 30 + dms(27, 47, 55),        # Aquarius
    "Moon": 6 * 30 + dms(1, 25, 19),         # Libra
    "Mars": 7 * 30 + dms(18, 37, 10),        # Scorpio
    "Mercury": 10 * 30 + dms(0, 22, 0),      # Aquarius
    "Jupiter": 1 * 30 + dms(10, 38, 44),     # Taurus
    "Venus": 11 * 30 + dms(23, 39, 19),      # Pisces (retrograde)
    "Saturn": 1 * 30 + dms(2, 6, 21),        # Taurus
    "Rahu": 2 * 30 + dms(18, 5, 56),         # Gemini
    "Ketu": 8 * 30 + dms(18, 5, 56),         # Sagittarius
}
REFERENCE_ASC = 1 * 30 + dms(6, 9, 50)       # Taurus
REFERENCE_SPEEDS = {"Venus": -0.5, "Rahu": -0.05, "Ketu": -0.05}

# The app's navamsa signs, the first external check.
REFERENCE_D9 = {
    "Asc": 10, "Sun": 2, "Moon": 6, "Mars": 8, "Mercury": 6, "Jupiter": 0,
    "Venus": 10, "Saturn": 9, "Rahu": 11, "Ketu": 5,
}
