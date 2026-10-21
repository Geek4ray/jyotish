"""Nakshatras, padas, Vimshottari and KP lords, Navatara."""

from __future__ import annotations

from dataclasses import dataclass

from .constants import (
    NAKSHATRA_SPAN, NAKSHATRAS, PADA_SPAN, SPECIAL_TARAS, TARA_ADVERSE, TARA_NAMES,
    VIMSHOTTARI_ORDER, VIMSHOTTARI_TOTAL, VIMSHOTTARI_YEARS, nakshatra_lord,
)


@dataclass(frozen=True)
class NakPosition:
    index: int          # 0 = Ashwini
    name: str
    pada: int           # 1-4
    lord: str
    fraction: float     # 0-1 progress through the nakshatra
    sub_lord: str
    sub_sub_lord: str


def _nak_index(lon: float) -> int:
    """27 * lon / 360 avoids the float error of dividing by 13.333...; 40° is Rohini exactly."""
    return int(lon * 27.0 / 360.0) % 27


def nakshatra_of(lon: float) -> NakPosition:
    lon = lon % 360.0
    idx = _nak_index(lon)
    within = lon - idx * NAKSHATRA_SPAN
    pada = int(lon * 108.0 / 360.0) % 4 + 1
    sub, subsub = kp_sub_lords(lon)
    return NakPosition(idx, NAKSHATRAS[idx], min(pada, 4), nakshatra_lord(idx),
                       within / NAKSHATRA_SPAN, sub, subsub)


def _sub_sequence(start_lord: str) -> list[str]:
    i = VIMSHOTTARI_ORDER.index(start_lord)
    return VIMSHOTTARI_ORDER[i:] + VIMSHOTTARI_ORDER[:i]


def _lord_at(offset: float, span: float, start_lord: str) -> tuple[str, float, float]:
    """Return (lord, sub_start, sub_span) for the Vimshottari-proportioned division of
    `span` starting with `start_lord`, at `offset` degrees into it."""
    cursor = 0.0
    for lord in _sub_sequence(start_lord):
        sub_span = span * VIMSHOTTARI_YEARS[lord] / VIMSHOTTARI_TOTAL
        if offset < cursor + sub_span or lord == _sub_sequence(start_lord)[-1]:
            return lord, cursor, sub_span
        cursor += sub_span
    raise AssertionError("unreachable")


def kp_sub_lords(lon: float) -> tuple[str, str]:
    """KP sub lord and sub-sub lord of a longitude."""
    lon = lon % 360.0
    idx = _nak_index(lon)
    within = max(lon - idx * NAKSHATRA_SPAN, 0.0)
    star = nakshatra_lord(idx)
    sub, sub_start, sub_span = _lord_at(within, NAKSHATRA_SPAN, star)
    subsub, _, _ = _lord_at(within - sub_start, sub_span, sub)
    return sub, subsub


@dataclass(frozen=True)
class Tara:
    count: int      # 1-27 from the Moon's nakshatra
    cycle: int      # 1-3
    index: int      # 1-9 within the cycle
    name: str
    adverse: bool
    special: str | None


def navatara(nak_index: int, moon_nak_index: int) -> Tara:
    count = (nak_index - moon_nak_index) % 27 + 1
    cycle = (count - 1) // 9 + 1
    index = (count - 1) % 9 + 1
    name = TARA_NAMES[index - 1]
    return Tara(count, cycle, index, name, name in TARA_ADVERSE, SPECIAL_TARAS.get(count))


def vimshottari_balance(moon_lon: float, year_days: float = 365.25) -> tuple[str, float]:
    """Lord of the first maha dasha and the years of it remaining at birth."""
    pos = nakshatra_of(moon_lon)
    remaining = (1.0 - pos.fraction) * VIMSHOTTARI_YEARS[pos.lord]
    return pos.lord, remaining
