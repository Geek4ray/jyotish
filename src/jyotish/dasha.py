"""Vimshottari dasha to any depth. Dates are Julian days; the year length is a setting
(Layer 4 of the spec: 365.25 solar, 360 savana, 365.2564 sidereal)."""

from __future__ import annotations

from dataclasses import dataclass

from .constants import VIMSHOTTARI_ORDER, VIMSHOTTARI_TOTAL, VIMSHOTTARI_YEARS
from .nakshatra import nakshatra_of

YEAR_LENGTHS = {"solar": 365.25, "savana": 360.0, "sidereal": 365.2564}


@dataclass(frozen=True)
class Period:
    lords: tuple[str, ...]   # (maha,) or (maha, antar) or deeper
    start_jd: float
    end_jd: float

    @property
    def level(self) -> int:
        return len(self.lords)

    @property
    def lord(self) -> str:
        return self.lords[-1]


def _sequence_from(lord: str) -> list[str]:
    i = VIMSHOTTARI_ORDER.index(lord)
    return VIMSHOTTARI_ORDER[i:] + VIMSHOTTARI_ORDER[:i]


def vimshottari(moon_lon: float, birth_jd: float, levels: int = 2,
                year_length: float = 365.25) -> list[Period]:
    """All periods from birth through the full 120-year cycle, to `levels` deep,
    starting with the balance of the birth nakshatra lord."""
    pos = nakshatra_of(moon_lon)
    first = pos.lord
    balance_fraction = 1.0 - pos.fraction
    periods: list[Period] = []
    cursor = birth_jd
    for i, maha in enumerate(_sequence_from(first)):
        years = VIMSHOTTARI_YEARS[maha]
        length_days = years * year_length
        if i == 0:
            # The elapsed part of the first maha dasha lies before birth; sub-periods are
            # laid out from the true start so that the antar at birth is correct.
            true_start = cursor - (1.0 - balance_fraction) * length_days
        else:
            true_start = cursor
        end = true_start + length_days
        periods.append(Period((maha,), true_start, end))
        if levels >= 2:
            periods.extend(_subdivide((maha,), true_start, length_days, levels, 2))
        cursor = end
    # Drop sub-periods that ended before birth; keep the maha so the balance is visible.
    return [p for p in periods if p.end_jd > birth_jd or p.level == 1]


def _subdivide(lords: tuple[str, ...], start: float, length_days: float,
               max_level: int, level: int) -> list[Period]:
    out: list[Period] = []
    cursor = start
    for sub in _sequence_from(lords[-1]):
        sub_len = length_days * VIMSHOTTARI_YEARS[sub] / VIMSHOTTARI_TOTAL
        p = Period(lords + (sub,), cursor, cursor + sub_len)
        out.append(p)
        if level < max_level:
            out.extend(_subdivide(p.lords, cursor, sub_len, max_level, level + 1))
        cursor += sub_len
    return out


def period_at(periods: list[Period], jd: float, level: int) -> Period | None:
    for p in periods:
        if p.level == level and p.start_jd <= jd < p.end_jd:
            return p
    return None
