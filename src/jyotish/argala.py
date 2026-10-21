"""Argala and Virodhargala (planetary intervention and its obstruction) on every house and
on the Arudha lagna, as Jaimini's Upadesa Sutras are read by Sanjay Rath, with BPHS 31.2-9
(Santhanam 1984) for the parts his reading leaves open.

From a reference sign, planets in the 2nd, 4th and 11th cause Argala, obstructed by
planets in the 12th, 10th and 3rd; the 5th is a secondary Argala, obstructed from the 9th
(JS 1.1.4, 1.1.6, 1.1.8 in Rath's 1997 numbering; BPHS 31.2-9 agrees).

Which side prevails (JS 1.1.7, judged by the strength of signs, JS 2.3.6-9 in Rath; Jupiter's
aspect from Rath's "Argala: Planetary Intervention", srath.com): the sign with the
Atmakaraka; then more planets; then their dignity (exalted, then moolatrikona, then own);
then dual over fixed over movable; then the sign aspected by Jupiter (Jaimini sign aspect).
Equal on all of these is Bandhana (stalemate) in Rath's reading.

Malefics in the 3rd cause an Argala of their own (JS 1.1.5). Rath gives no number; BPHS
31.2-9 makes it Vipareeta Argala with three or more, which is what is flagged here.

Nodes (Meta.argala_nodes):
  - "rath" (default): "viparitam ketoh" (JS 1.1.9 in the 1997 book, 1.1.8 in the srath.com
    article). When Ketu is in the reference sign, every Argala and obstruction place is
    counted backwards from it. Rahu is not named, and nodes elsewhere count directly.
  - "reverse_position": the other reading of BPHS 31.2-9 ("the Argalas and obstructions be
    also counted accordingly in a reverse manner"): a node's own place is counted backwards
    from the reference sign.
  - "direct": nodes count like the other planets.
Rath also gives the 8th (obstructed from the 6th) and the 7th (from the 1st); those are not
computed here."""

from __future__ import annotations

from .constants import EXALTATION, GRAHAS, MOOLATRIKONA, OWN_SIGNS, SEVEN
from .dasha import rashi_aspects
from .shadbala import natural_benefics

ARGALA_PAIRS = [(2, 12, "primary"), (4, 10, "primary"), (11, 3, "primary"), (5, 9, "secondary")]
NODES = ("Rahu", "Ketu")
NODE_READINGS = ("rath", "reverse_position", "direct")


def place_from(ref_sign: int, planet: str, sign: int, nodes: str, signs: dict[str, int]) -> int:
    if nodes not in NODE_READINGS:
        raise ValueError(f"argala_nodes must be one of {NODE_READINGS}, not {nodes!r}")
    backwards = ((nodes == "rath" and signs["Ketu"] == ref_sign)
                 or (nodes == "reverse_position" and planet in NODES))
    return (ref_sign - sign) % 12 + 1 if backwards else (sign - ref_sign) % 12 + 1


def _dignity(sign: int, occupants: list[str]) -> tuple[int, int, int]:
    ex = sum(1 for p in occupants if p in SEVEN and EXALTATION[p][0] == sign)
    mt = sum(1 for p in occupants if p in SEVEN and MOOLATRIKONA[p][0] == sign)
    own = sum(1 for p in occupants if p in SEVEN and sign in OWN_SIGNS[p])
    return ex, mt, own


def sign_strength(sign: int, occupants: list[str], ak: str | None, jupiter_sign: int) -> tuple:
    """Comparable strength of a sign for Argala, highest first by the order in the module
    docstring."""
    return (int(ak in occupants), len(occupants), _dignity(sign, occupants), sign % 3,
            int(sign in rashi_aspects(jupiter_sign)))


def argala_on(ref_sign: int, signs: dict[str, int], *, nodes: str, ak: str | None,
              malefics: set[str]) -> dict:
    at: dict[int, list[str]] = {h: [] for h in range(1, 13)}
    for p in GRAHAS:
        at[place_from(ref_sign, p, signs[p], nodes, signs)].append(p)
    backwards = nodes == "rath" and signs["Ketu"] == ref_sign
    step = -1 if backwards else 1

    def sign_at(h):
        return (ref_sign + step * (h - 1)) % 12

    places = []
    for h, obs_h, kind in ARGALA_PAIRS:
        by, blocked_by = at[h], at[obs_h]
        if not by:
            continue
        if not blocked_by:
            outcome = "unobstructed"
        else:
            sa = sign_strength(sign_at(h), by, ak, signs["Jupiter"])
            sb = sign_strength(sign_at(obs_h), blocked_by, ak, signs["Jupiter"])
            outcome = "prevails" if sa > sb else "obstructed" if sa < sb else "bandhana"
        places.append({"house": h, "kind": kind, "by": by, "obstruction_house": obs_h,
                       "blocked_by": blocked_by, "outcome": outcome})
    third_malefics = [p for p in at[3] if p in malefics]
    return {"places": places, "vipareeta": len(third_malefics) >= 3,
            "third_malefics": third_malefics, "reversed": backwards}


def argala(positions: dict[str, float], lagna_sign: int, arudha_lagna: int, *,
           nodes: str = "rath", ak: str | None = None,
           mercury_nature: str = "association") -> dict[str, dict]:
    """Argala on H1-H12 (whole sign from the lagna) and on the Arudha lagna ("AL")."""
    signs = {p: int((positions[p] % 360.0) // 30) for p in GRAHAS}
    malefics = set(GRAHAS) - natural_benefics(positions, mercury_nature)
    kw = dict(nodes=nodes, ak=ak, malefics=malefics)
    out = {f"H{h}": argala_on((lagna_sign + h - 1) % 12, signs, **kw) for h in range(1, 13)}
    out["AL"] = argala_on(arudha_lagna, signs, **kw)
    return out
