"""Jaimini: chara karakas (7- and 8-karaka schemes), arudha padas, karakamsa."""

from __future__ import annotations

from .constants import SEVEN, SIGN_LORD
from .vargas import d9

KARAKAS_8 = ["AK", "AmK", "BK", "MK", "PiK", "PK", "GK", "DK"]
# In the 7-karaka scheme the Matri and Pitri karakas merge into MK.
KARAKAS_7 = ["AK", "AmK", "BK", "MK", "PK", "GK", "DK"]


def chara_karakas(positions: dict[str, float], scheme: int = 8) -> dict[str, str]:
    """Planets ranked by degree within sign. Rahu, when included, counts 30° minus its
    degree. Returns karaka -> planet."""
    deg = {p: positions[p] % 30 for p in SEVEN}
    if scheme == 8:
        deg["Rahu"] = 30.0 - (positions["Rahu"] % 30)
        names = KARAKAS_8
    elif scheme == 7:
        names = KARAKAS_7
    else:
        raise ValueError("scheme must be 7 or 8")
    ranked = sorted(deg, key=lambda p: deg[p], reverse=True)
    return dict(zip(names, ranked))


def arudha_pada(house: int, lagna_sign: int, positions: dict[str, float]) -> int:
    """Arudha of a house (1-12) for a lagna sign, with the Jaimini exception: a pada that
    falls in the house itself or in the 7th from it moves to the 10th from where it fell.
    Primary sign lords are used for Scorpio and Aquarius."""
    sign = (lagna_sign + house - 1) % 12
    lord = SIGN_LORD[sign]
    lord_sign = int(positions[lord] // 30) % 12
    d = (lord_sign - sign) % 12
    pada = (lord_sign + d) % 12
    # Exception (Jaimini Sutra 1.1.30-31): a pada in the house's own sign or its 7th
    # moves to the 10th from where it fell. That happens when the lord is 1st, 4th,
    # 7th or 10th from the house.
    if (pada - sign) % 12 in (0, 6):
        pada = (pada + 9) % 12
    return pada


def all_arudhas(lagna_sign: int, positions: dict[str, float]) -> dict[str, int]:
    out = {f"A{h}": arudha_pada(h, lagna_sign, positions) for h in range(1, 13)}
    out["AL"] = out["A1"]
    out["UL"] = out["A12"]
    return out


def karakamsa(positions: dict[str, float], scheme: int = 8) -> int:
    ak = chara_karakas(positions, scheme)["AK"]
    return d9(positions[ak])
