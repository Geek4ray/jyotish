"""Lordship for a lagna, five-fold dignity, natural and compound relationships,
avasthas, sensitive degrees, aspects. Feature-engine pieces that need no ephemeris."""

from __future__ import annotations

from .constants import (
    AIR, BALADI, COMBUST_ORB, EARTH, EXALTATION, FIRE, GANDANTA_SPAN, MARANA_KARAKA_STHANA,
    MOOLATRIKONA, NATURAL_ENEMIES, NATURAL_FRIENDS, PUSHKARA_BHAGA, PUSHKARA_NAVAMSA,
    SEVEN, SIGN_LORD, SPECIAL_ASPECTS, WATER, is_odd_sign,
)

KENDRAS = {1, 4, 7, 10}
TRIKONAS = {1, 5, 9}
DUSTHANAS = {6, 8, 12}


def house_of(sign: int, lagna_sign: int) -> int:
    """Whole-sign house (1-12) of a sign for a lagna sign."""
    return (sign - lagna_sign) % 12 + 1


def house_lords(lagna_sign: int) -> dict[int, str]:
    return {h: SIGN_LORD[(lagna_sign + h - 1) % 12] for h in range(1, 13)}


def lordships(lagna_sign: int) -> dict[str, list[int]]:
    out: dict[str, list[int]] = {p: [] for p in SEVEN}
    for h, lord in house_lords(lagna_sign).items():
        out[lord].append(h)
    return out


def functional_roles(lagna_sign: int) -> dict[str, list[str]]:
    """Yogakaraka (owns a kendra other than the lagna and a trikona), maraka (owns 2 or 7),
    lagna lord. Other functional malefic/benefic rules are in the rule library."""
    roles: dict[str, list[str]] = {p: [] for p in SEVEN}
    for planet, houses in lordships(lagna_sign).items():
        hs = set(houses)
        if 1 in hs:
            roles[planet].append("lagna_lord")
        if (hs & (KENDRAS - {1})) and (hs & (TRIKONAS - {1})):
            roles[planet].append("yogakaraka")
        if (hs & {2, 7}) and "lagna_lord" not in roles[planet]:
            roles[planet].append("maraka")
    return roles


def natural_relation(planet: str, other: str) -> str:
    if other in NATURAL_FRIENDS[planet]:
        return "friend"
    if other in NATURAL_ENEMIES[planet]:
        return "enemy"
    return "neutral"


def temporal_relation(planet_sign: int, other_sign: int) -> str:
    """Tatkalika: planets in 2,3,4,10,11,12 from a planet are temporary friends."""
    d = (other_sign - planet_sign) % 12 + 1
    return "friend" if d in {2, 3, 4, 10, 11, 12} else "enemy"


def compound_relation(natural: str, temporal: str) -> str:
    table = {
        ("friend", "friend"): "great_friend", ("friend", "enemy"): "neutral",
        ("neutral", "friend"): "friend", ("neutral", "enemy"): "enemy",
        ("enemy", "friend"): "neutral", ("enemy", "enemy"): "great_enemy",
    }
    return table[(natural, temporal)]


def dignity(planet: str, lon: float, positions: dict[str, float] | None = None,
            compound: bool = False) -> str:
    """Five-fold dignity of one of the seven planets at a sidereal longitude.
    With `compound=True` and the other planets' longitudes, friend/enemy use the
    compound relationship instead of the natural one."""
    if planet not in SEVEN:
        return "node"
    sign, deg = int(lon // 30) % 12, lon % 30
    ex_sign, _ = EXALTATION[planet]
    if sign == ex_sign:
        return "exalted"
    if sign == (ex_sign + 6) % 12:
        return "debilitated"
    mt_sign, lo, hi = MOOLATRIKONA[planet]
    if sign == mt_sign and lo <= deg < hi:
        return "moolatrikona"
    lord = SIGN_LORD[sign]
    if lord == planet:
        return "own"
    rel = natural_relation(planet, lord)
    if compound and positions is not None and lord in positions:
        rel = compound_relation(rel, temporal_relation(sign, int(positions[lord] // 30) % 12))
        rel = {"great_friend": "friend", "great_enemy": "enemy"}.get(rel, rel)
    return rel


def deep_exaltation_distance(planet: str, lon: float) -> float | None:
    ex_sign, ex_deg = EXALTATION[planet]
    if int(lon // 30) % 12 != ex_sign:
        return None
    return ex_deg - (lon % 30)


def baladi_avastha(lon: float) -> str:
    sign, deg = int(lon // 30) % 12, lon % 30
    k = min(int(deg // 6), 4)
    return BALADI[k] if is_odd_sign(sign) else BALADI[4 - k]


def is_combust(planet: str, lon: float, sun_lon: float, retro: bool) -> bool:
    if planet not in COMBUST_ORB:
        return False
    orb = COMBUST_ORB[planet][1 if retro else 0]
    diff = abs((lon - sun_lon + 180) % 360 - 180)
    return diff <= orb


def is_boundary(lon: float, orb: float = 3.0) -> bool:
    deg = lon % 30
    return deg < orb or deg > 30 - orb


def gandanta(lon: float) -> bool:
    sign, deg = int(lon // 30) % 12, lon % 30
    return (sign in WATER and deg >= 30 - GANDANTA_SPAN) or (sign in FIRE and deg < GANDANTA_SPAN)


def pushkara_navamsa(lon: float) -> bool:
    sign, deg = int(lon // 30) % 12, lon % 30
    element = "fire" if sign in FIRE else "earth" if sign in EARTH else "air" if sign in AIR else "water"
    return any(lo <= deg < hi for lo, hi in PUSHKARA_NAVAMSA[element])


def pushkara_bhaga(lon: float, orb: float = 1.0) -> bool:
    sign, deg = int(lon // 30) % 12, lon % 30
    return abs(deg - PUSHKARA_BHAGA[sign]) <= orb


def marana_karaka_sthana(planet: str, house: int) -> bool:
    return MARANA_KARAKA_STHANA.get(planet) == house


def aspected_houses(planet: str, house: int) -> list[int]:
    """Whole-sign graha drishti: 7th for all, plus the Parashari specials."""
    offsets = [7] + SPECIAL_ASPECTS.get(planet, [])
    return sorted({(house + o - 2) % 12 + 1 for o in offsets})


def aspects(planet_houses: dict[str, int]) -> list[tuple[str, int]]:
    """List of (planet, house aspected) for every planet by whole-sign drishti.
    Rahu/Ketu aspects are a setting and are not included here."""
    out = []
    for planet, house in planet_houses.items():
        if planet in SEVEN:
            for h in aspected_houses(planet, house):
                out.append((planet, h))
    return out
