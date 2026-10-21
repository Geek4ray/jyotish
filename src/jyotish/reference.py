"""The reference chart from SPEC.md (Taurus lagna), used with the owner's consent to test
everything the engine builds. Longitudes are the reference app's printed sidereal
positions (Lahiri, mean node). This is the Phase 1 acceptance target: `analyse` on these
longitudes must reproduce every value in SPEC.md's worked example, and `compute` on the
birth data must reproduce the longitudes."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

# Birth data. The reference app dropped the 25 seconds (it computed 10:10:00), which moves
# the Moon by 15" and the ascendant by 7'; tests compare against the app at 10:10:00 and
# keep the true seconds for everything else.
REFERENCE_BIRTH_LOCAL = datetime(2001, 3, 12, 10, 10, 25, tzinfo=timezone(timedelta(hours=5, minutes=30)))
REFERENCE_BIRTH_UTC = REFERENCE_BIRTH_LOCAL.astimezone(timezone.utc)
REFERENCE_APP_UTC = REFERENCE_BIRTH_UTC.replace(second=0)
REFERENCE_LAT, REFERENCE_LON = 28.1989, 76.6170   # Rewari, Haryana, India
REFERENCE_TZ = "Asia/Kolkata"


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
