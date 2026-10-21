"""Ashtakavarga (SPEC Layer 2, strength modules): Bhinnashtakavarga for the seven planets
and the lagna, Sarvashtakavarga, Trikona and Ekadhipatya reductions, Sodhya Pinda, and the
Kakshya of each body's degree. Tables and the points where texts differ are in
`constants.py`; signs are 0 = Aries throughout and every list is indexed by sign."""

from __future__ import annotations

from dataclasses import dataclass

from .constants import (
    ASHTAKAVARGA_BENEFIC, ASHTAKAVARGA_CONTRIBUTORS, EKADHIPATYA_PAIRS, GRAHA_GUNAKARA,
    GRAHAS, KAKSHYA_LORDS, RASI_GUNAKARA, SEVEN,
)

TRINES = [(0, 4, 8), (1, 5, 9), (2, 6, 10), (3, 7, 11)]


def prastara(target: str, signs: dict[str, int]) -> dict[str, list[int]]:
    """The contributor-by-sign grid (0/1) behind one Bhinnashtakavarga. `signs` maps each
    contributor (the seven planets and "Asc") to its D1 sign."""
    grid = {}
    for c in ASHTAKAVARGA_CONTRIBUTORS:
        row = [0] * 12
        for h in ASHTAKAVARGA_BENEFIC[target][c]:
            row[(signs[c] + h - 1) % 12] = 1
        grid[c] = row
    return grid


def bhinnashtakavarga(target: str, signs: dict[str, int]) -> list[int]:
    grid = prastara(target, signs)
    return [sum(grid[c][s] for c in ASHTAKAVARGA_CONTRIBUTORS) for s in range(12)]


def sarvashtakavarga(bav: dict[str, list[int]]) -> list[int]:
    """Sum of the seven planets' tables per sign; the lagna's table is not included."""
    return [sum(bav[p][s] for p in SEVEN) for s in range(12)]


def trikona_shodhana(bav: list[int]) -> list[int]:
    """BPHS 67.4-5: subtract the least of each trine from all three. A trine holding a 0
    is unchanged and an all-equal trine clears, both of which subtracting the minimum gives."""
    out = list(bav)
    for trine in TRINES:
        m = min(bav[s] for s in trine)
        for s in trine:
            out[s] -= m
    return out


def _ekadhipatya_pair(a: int, b: int, occ_a: bool, occ_b: bool) -> tuple[int, int]:
    """BPHS 68 case table for one pair of signs (a, b are bindus after Trikona)."""
    if occ_a and occ_b:
        return a, b
    if occ_a or occ_b:
        occ, vac = (a, b) if occ_a else (b, a)
        vac = occ if occ < vac else 0      # occupied fewer: vacant down to it; else clear vacant
        return (occ, vac) if occ_a else (vac, occ)
    if a == b:
        return 0, 0
    m = min(a, b)
    return m, m


def ekadhipatya_shodhana(bav: list[int], occupied: set[int], *, zero_exempt: bool = False) -> list[int]:
    """Reduce the five pairs of signs with one lord. `bav` is the table after Trikona
    Shodhana; `occupied` is the set of signs holding an occupant (see Meta settings)."""
    out = list(bav)
    for a, b in EKADHIPATYA_PAIRS.values():
        if zero_exempt and (out[a] == 0 or out[b] == 0):
            continue
        out[a], out[b] = _ekadhipatya_pair(out[a], out[b], a in occupied, b in occupied)
    return out


@dataclass(frozen=True)
class PindaResult:
    rasi: int
    graha: int

    @property
    def sodhya(self) -> int:
        return self.rasi + self.graha


def sodhya_pinda(reduced: list[int], planet_signs: dict[str, int]) -> PindaResult:
    """BPHS 69: Rasi Pinda = sum over signs of reduced bindus x sign multiplier; Graha Pinda
    = for each of the seven planets, reduced bindus in its sign x its multiplier."""
    rasi = sum(reduced[s] * RASI_GUNAKARA[s] for s in range(12))
    graha = sum(reduced[planet_signs[p]] * GRAHA_GUNAKARA[p] for p in SEVEN)
    return PindaResult(rasi=rasi, graha=graha)


def kakshya_index(lon: float) -> int:
    """0-7 within the sign; 96 * lon / 360 avoids dividing by 3.75 (see nakshatra._nak_index)."""
    return int((lon % 360.0) * 96.0 / 360.0) % 8


def kakshya_lord(lon: float) -> str:
    return KAKSHYA_LORDS[kakshya_index(lon)]


@dataclass
class AshtakavargaResult:
    bav: dict[str, list[int]]
    sav: list[int]
    trikona: dict[str, list[int]]
    ekadhipatya: dict[str, list[int]]
    pinda: dict[str, PindaResult]
    kakshya: dict[str, str]
    kakshya_bindu: dict[str, bool]


def ashtakavarga(positions: dict[str, float], asc: float, *, nodes_occupy: bool = False,
                 zero_exempt: bool = False) -> AshtakavargaResult:
    """Everything for one chart. `positions` are sidereal longitudes of the grahas."""
    lon = {p: positions[p] % 360.0 for p in SEVEN}
    lon["Asc"] = asc % 360.0
    signs = {c: int(l // 30) for c, l in lon.items()}

    grids = {t: prastara(t, signs) for t in ASHTAKAVARGA_BENEFIC}
    bav = {t: [sum(g[c][s] for c in ASHTAKAVARGA_CONTRIBUTORS) for s in range(12)]
           for t, g in grids.items()}

    occupants = GRAHAS if nodes_occupy else SEVEN
    occupied = {int((positions[p] % 360.0) // 30) for p in occupants}
    planet_signs = {p: signs[p] for p in SEVEN}
    trikona = {p: trikona_shodhana(bav[p]) for p in SEVEN}
    ekadhi = {p: ekadhipatya_shodhana(trikona[p], occupied, zero_exempt=zero_exempt) for p in SEVEN}
    pinda = {p: sodhya_pinda(ekadhi[p], planet_signs) for p in SEVEN}

    # The kakshya lord "gives" its kakshya when it put a bindu in that sign of the body's
    # own table (the transit reading of the same idea uses the transiting planet's table).
    kak = {c: kakshya_lord(l) for c, l in lon.items()}
    kak_bindu = {c: bool(grids[c][kak[c]][signs[c]]) for c in lon}

    return AshtakavargaResult(bav=bav, sav=sarvashtakavarga(bav), trikona=trikona,
                              ekadhipatya=ekadhi, pinda=pinda, kakshya=kak, kakshya_bindu=kak_bindu)
