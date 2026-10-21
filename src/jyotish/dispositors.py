"""Dispositor chains (sign, nakshatra, navamsa), loops, final dispositors, Parivartana."""

from __future__ import annotations

from dataclasses import dataclass, field

from .constants import SEVEN, SIGN_LORD
from .dignity import DUSTHANAS, house_of, lordships
from .nakshatra import nakshatra_of
from .vargas import d9


def _chain(start: str, next_of: dict[str, str]) -> tuple[list[str], list[str] | None]:
    """Follow next_of from start until a repeat. Returns (path, loop) where loop is the
    cycle the path ends in (a single self-disposited planet is a loop of length 1)."""
    path = [start]
    seen = {start: 0}
    cur = start
    while True:
        nxt = next_of.get(cur)
        if nxt is None:
            return path, None
        if nxt in seen:
            return path, path[seen[nxt]:]
        path.append(nxt)
        seen[nxt] = len(path) - 1
        cur = nxt


@dataclass
class ChainResult:
    chains: dict[str, list[str]] = field(default_factory=dict)
    loops: list[list[str]] = field(default_factory=list)
    final: list[str] = field(default_factory=list)


def _run(next_of: dict[str, str]) -> ChainResult:
    res = ChainResult()
    for p in next_of:
        path, loop = _chain(p, next_of)
        res.chains[p] = path
        if loop:
            key = sorted(loop)
            if key not in [sorted(l) for l in res.loops]:
                res.loops.append(loop)
    finals: set[str] = set()
    for loop in res.loops:
        finals.update(loop)
    res.final = sorted(finals)
    return res


def sign_chains(positions: dict[str, float]) -> ChainResult:
    """Sign dispositor: planet -> lord of its sign. Rahu/Ketu disposit by their sign lord
    but are never dispositors themselves (primary-lord convention)."""
    next_of = {p: SIGN_LORD[int(lon // 30) % 12] for p, lon in positions.items()}
    return _run(next_of)


def nakshatra_chains(positions: dict[str, float]) -> ChainResult:
    next_of = {p: nakshatra_of(lon).lord for p, lon in positions.items()}
    return _run(next_of)


def navamsa_chains(positions: dict[str, float]) -> ChainResult:
    next_of = {p: SIGN_LORD[d9(lon)] for p, lon in positions.items()}
    return _run(next_of)


@dataclass(frozen=True)
class Parivartana:
    planets: tuple[str, str]
    houses: tuple[int, int]          # houses exchanged (whole sign)
    class_by_houses: str             # maha | kahala | dainya
    class_by_lordship: str           # same classes, judged by every house the two planets own
    taint: tuple[int, ...]           # dusthana houses owned by either planet


def _classify(houses: set[int]) -> str:
    if houses & DUSTHANAS:
        return "dainya"
    if 3 in houses:
        return "kahala"
    return "maha"


def parivartanas(positions: dict[str, float], lagna_sign: int) -> list[Parivartana]:
    """Mutual sign exchanges among the seven planets, classified two ways because the
    texts define the classes two ways (by houses exchanged, Phaladeepika; by lordships,
    Uttara Kalamrita)."""
    sign_of = {p: int(lon // 30) % 12 for p, lon in positions.items() if p in SEVEN}
    lords = lordships(lagna_sign)
    out = []
    seen = set()
    for a, sa in sign_of.items():
        b = SIGN_LORD[sa]
        if b == a or b not in sign_of:
            continue
        if SIGN_LORD[sign_of[b]] != a:
            continue
        key = tuple(sorted((a, b)))
        if key in seen:
            continue
        seen.add(key)
        ha, hb = house_of(sa, lagna_sign), house_of(sign_of[b], lagna_sign)
        owned = set(lords[a]) | set(lords[b])
        out.append(Parivartana(key, (min(ha, hb), max(ha, hb)), _classify({ha, hb}),
                               _classify(owned), tuple(sorted(owned & DUSTHANAS))))
    return out
