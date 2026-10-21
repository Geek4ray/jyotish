"""Vimsopaka bala (BPHS 7.17-25, Santhanam 1984): the 20-point varga strength of each of
the seven planets under the Shadvarga, Saptavarga, Dasavarga and Shodasavarga schemes.
Each varga contributes its weight x Varga Viswa / 20 (constants.VIMSOPAKA_SCHEMES and
VARGA_VISWA)."""

from __future__ import annotations

from .constants import OWN_SIGNS, SEVEN, SIGN_LORD, VARGA_VISWA, VIMSOPAKA_SCHEMES
from .dignity import compound_relation, natural_relation, temporal_relation
from .vargas import VARGAS


def varga_viswa(planet: str, varga_sign: int, d1_signs: dict[str, int]) -> int:
    if varga_sign in OWN_SIGNS[planet]:
        return VARGA_VISWA["own"]
    lord = SIGN_LORD[varga_sign]
    rel = compound_relation(natural_relation(planet, lord),
                            temporal_relation(d1_signs[planet], d1_signs[lord]))
    return VARGA_VISWA[rel]


def vimsopaka(positions: dict[str, float]) -> dict[str, dict[str, float]]:
    """planet -> scheme -> 0-20."""
    d1 = {p: int((positions[p] % 360.0) // 30) for p in SEVEN}
    out = {}
    for p in SEVEN:
        lon = positions[p] % 360.0
        out[p] = {scheme: sum(w * varga_viswa(p, VARGAS[v](lon), d1) for v, w in weights.items()) / 20.0
                  for scheme, weights in VIMSOPAKA_SCHEMES.items()}
    return out
