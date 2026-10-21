"""Shadbala (BPHS ch. 27), in virupas: Sthana, Dig, Kala, Chesta, Naisargika and Drik
bala for the seven planets, each with its required minimum and the ratio to it.

Positions are sidereal; times are Julian days (UT). Every point where texts differ is a
field of `ShadbalaSettings`, mirrored one-to-one by `Meta`, and documented with its
sources in `constants.py`."""

from __future__ import annotations

import math
from dataclasses import dataclass, field, fields

from .constants import (
    AYANA_NORTH, AYANA_SOUTH, BIMBA_DIAMETER, CHALDEAN_ORDER, DIG_STRONG_POINT,
    DREKKANA_BALA_DECANATE, EXALTATION, KALA_LORD_BALA, KALI_EPOCH_JDN, MEAN_LONGITUDE,
    MERCURY_SPOILERS, MOOLATRIKONA, NAISARGIKA, NATHONNATA_DAY, NATHONNATA_NIGHT,
    PAKSHA_BENEFICS, PARAMA_KRANTI, SAPTAVARGA, SAPTAVARGAJA_SCALES, SEVEN,
    SHADBALA_REQUIRED, SIGN_LORD, SPECIAL_ASPECTS, TRIBHAGA_DAY, TRIBHAGA_NIGHT, VARA_LORDS,
    YUDDHA_ORB, YUDDHA_PLANETS, is_odd_sign,
)
from .dignity import compound_relation, house_of, natural_relation, temporal_relation
from .vargas import VARGAS, d9


@dataclass(frozen=True)
class ShadbalaSettings:
    """Conventions where the texts differ. Field names match `Meta`."""
    drekkana_bala: str = "bphs"            # bphs | phaladeepika
    saptavargaja_scale: str = "bphs"       # bphs | raman
    dig_bala_points: str = "cusps"         # cusps (asc, MC) | equal (asc + 90° steps)
    nathonnata_noon: str = "apparent"      # apparent (mid sunrise-sunset) | mean (local mean noon)
    mercury_nature: str = "association"    # association | benefic
    paksha_moon_double: bool = True
    ayana_obliquity: str = "bphs"          # bphs (24°) | true (mean obliquity of date)
    ayana_sun_double: bool = True
    chesta_luminaries: str = "bphs"        # bphs (Sun = ayana, Moon = paksha) | zero

    @classmethod
    def from_obj(cls, obj) -> "ShadbalaSettings":
        return cls(**{f.name: getattr(obj, f.name) for f in fields(cls)})


def _fold(angle: float) -> float:
    """Angular distance 0-180."""
    a = angle % 360.0
    return 360.0 - a if a > 180.0 else a


def _sign(lon: float) -> int:
    return int((lon % 360.0) // 30)


# --- Sthana bala ---------------------------------------------------------------------

def uchcha_bala(planet: str, lon: float) -> float:
    ex_sign, ex_deg = EXALTATION[planet]
    debilitation = ex_sign * 30.0 + ex_deg + 180.0
    return _fold(lon - debilitation) / 3.0


def varga_dignity(planet: str, varga: str, lon: float, d1_signs: dict[str, int]) -> str:
    """Moolatrikona (D1 by degree), own, or the five-fold compound relation with the
    varga sign's lord, the temporal half read from the D1 signs."""
    s = VARGAS[varga](lon)
    if varga == "D1":
        mt_sign, lo, hi = MOOLATRIKONA[planet]
        if s == mt_sign and lo <= lon % 30.0 < hi:
            return "moolatrikona"
    lord = SIGN_LORD[s]
    if lord == planet:
        return "own"
    return compound_relation(natural_relation(planet, lord),
                             temporal_relation(d1_signs[planet], d1_signs[lord]))


def saptavargaja_bala(planet: str, lon: float, d1_signs: dict[str, int], scale: str) -> float:
    values = SAPTAVARGAJA_SCALES[scale]
    return sum(values[varga_dignity(planet, v, lon, d1_signs)] for v in SAPTAVARGA)


def ojhayugma_bala(planet: str, lon: float) -> float:
    """15 each for D1 and D9 sign of the planet's parity: even for the Moon and Venus,
    odd for the rest."""
    want_odd = planet not in ("Moon", "Venus")
    return sum(15.0 for s in (_sign(lon), d9(lon)) if is_odd_sign(s) == want_odd)


def kendra_bala(sign: int, lagna_sign: int) -> float:
    h = house_of(sign, lagna_sign)
    return 60.0 if h in (1, 4, 7, 10) else 30.0 if h in (2, 5, 8, 11) else 15.0


def drekkana_index(lon: float) -> int:
    """0-2 within the sign; 36 * lon / 360 avoids dividing by 10 after a subtraction."""
    return int((lon % 360.0) * 36.0 / 360.0) % 3


def drekkana_bala(planet: str, lon: float, convention: str) -> float:
    return 15.0 if drekkana_index(lon) == DREKKANA_BALA_DECANATE[convention][planet] else 0.0


# --- Dig bala ------------------------------------------------------------------------

def dig_points(asc: float, mc: float | None, convention: str) -> dict[str, float]:
    if convention == "cusps":
        if mc is None:
            raise ValueError("dig_bala_points='cusps' needs the MC")
    elif convention == "equal":
        mc = asc + 270.0
    else:
        raise ValueError(convention)
    return {"asc": asc % 360.0, "desc": (asc + 180.0) % 360.0,
            "mc": mc % 360.0, "ic": (mc + 180.0) % 360.0}


def dig_bala(planet: str, lon: float, points: dict[str, float]) -> float:
    weakest = points[DIG_STRONG_POINT[planet]] + 180.0
    return _fold(lon - weakest) / 3.0


# --- Kala bala -----------------------------------------------------------------------

def moon_elongation(sun: float, moon: float) -> float:
    """Moon from the Sun folded to 0-180 (0 new, 180 full)."""
    return _fold(moon - sun)


def mercury_is_benefic(positions: dict[str, float], nature: str) -> bool:
    if nature == "benefic":
        return True
    if nature != "association":
        raise ValueError(nature)
    s = _sign(positions["Mercury"])
    return not any(_sign(positions[p]) == s for p in MERCURY_SPOILERS if p in positions)


def paksha_bala(planet: str, positions: dict[str, float], settings: ShadbalaSettings) -> float:
    benefic_value = moon_elongation(positions["Sun"], positions["Moon"]) / 3.0
    if planet == "Moon":
        return benefic_value * (2.0 if settings.paksha_moon_double else 1.0)
    benefic = planet in PAKSHA_BENEFICS or (
        planet == "Mercury" and mercury_is_benefic(positions, settings.mercury_nature))
    return benefic_value if benefic else 60.0 - benefic_value


def nathonnata_bala(planet: str, jd: float, noon_jd: float) -> float:
    """Ghatis from noon g (0-30): day planets 60 - 2g, night planets 2g, Mercury 60."""
    g = 60.0 * abs((jd - noon_jd + 0.5) % 1.0 - 0.5)
    if planet in NATHONNATA_DAY:
        return 60.0 - 2.0 * g
    if planet in NATHONNATA_NIGHT:
        return 2.0 * g
    return 60.0


def tribhaga_lord(jd: float, sunrise: float, sunset: float, next_sunrise: float) -> str:
    if sunrise <= jd < sunset:
        return TRIBHAGA_DAY[min(int(3.0 * (jd - sunrise) / (sunset - sunrise)), 2)]
    return TRIBHAGA_NIGHT[min(int(3.0 * (jd - sunset) / (next_sunrise - sunset)), 2)]


def _weekday_lord(jdn: int) -> str:
    return VARA_LORDS[(jdn + 1) % 7]


def kala_lords(jd: float, sunrise: float) -> dict[str, str]:
    """Lords of the year, month, weekday and hora at birth. The day is the Vedic day from
    sunrise, numbered as the panchanga numbers it (Julian Day Number of sunrise, UT)."""
    day = int(sunrise + 0.5)
    ahargana = day - KALI_EPOCH_JDN
    hora = int((jd - sunrise) * 24.0)
    vara = _weekday_lord(day)
    return {"abda": _weekday_lord(day - ahargana % 360), "masa": _weekday_lord(day - ahargana % 30),
            "vara": vara, "hora": CHALDEAN_ORDER[(CHALDEAN_ORDER.index(vara) + hora) % 7]}


def _centuries(jd: float) -> float:
    return (jd - 2451545.0) / 36525.0


def declination(sayana_lon: float, jd: float, obliquity: str) -> float:
    if obliquity == "bphs":
        eps = PARAMA_KRANTI
    elif obliquity == "true":
        eps = 23.439291 - 0.0130042 * _centuries(jd)
    else:
        raise ValueError(obliquity)
    return math.degrees(math.asin(math.sin(math.radians(eps)) * math.sin(math.radians(sayana_lon))))


def ayana_bala(planet: str, sidereal_lon: float, ayanamsa: float, jd: float,
               settings: ShadbalaSettings) -> float:
    d = declination(sidereal_lon + ayanamsa, jd, settings.ayana_obliquity)
    if planet in AYANA_SOUTH:
        d = -d
    elif planet not in AYANA_NORTH:
        d = abs(d)                     # Mercury
    bala = (24.0 + d) / 48.0 * 60.0
    if planet == "Sun" and settings.ayana_sun_double:
        bala *= 2.0
    return bala


# --- Chesta bala ---------------------------------------------------------------------

def mean_longitude(body: str, jd: float) -> float:
    l0, rate = MEAN_LONGITUDE[body]
    return (l0 + rate * _centuries(jd)) % 360.0


def chesta_kendra(planet: str, sayana_lon: float, jd: float) -> float:
    """Seeghrochcha minus the mean of the mean and true planet, folded to 0-180."""
    sun = mean_longitude("Sun", jd)
    own = mean_longitude(planet, jd)
    if planet in ("Mercury", "Venus"):
        seeghrochcha, mean = own, sun
    else:
        seeghrochcha, mean = sun, own
    middle = mean + ((sayana_lon - mean + 180.0) % 360.0 - 180.0) / 2.0
    return _fold(seeghrochcha - middle)


# --- Drik bala -----------------------------------------------------------------------

def drishti(aspecting: str, angle: float) -> float:
    """Sphuta drishti in virupas for an aspected point `angle` degrees ahead of the
    aspecting planet, with the Parashari special aspects raised to full strength
    at the start of their range (Mars +15, Jupiter +30, Saturn +45)."""
    d = angle % 360.0
    if d < 30.0 or d >= 300.0:
        v = 0.0
    elif d < 60.0:
        v = (d - 30.0) / 2.0
    elif d < 90.0:
        v = d - 60.0 + 15.0
    elif d < 120.0:
        v = (120.0 - d) / 2.0 + 30.0
    elif d < 150.0:
        v = 150.0 - d
    elif d < 180.0:
        v = (d - 150.0) * 2.0
    else:
        v = (300.0 - d) / 2.0
    houses = SPECIAL_ASPECTS.get(aspecting, [])
    bonus = {4: 15.0, 8: 15.0, 5: 30.0, 9: 30.0, 3: 45.0, 10: 45.0}
    for h in houses:
        lo = (h - 1) * 30.0
        if lo <= d < lo + 30.0:
            v += bonus[h]
    return v


def natural_benefics(positions: dict[str, float], mercury_nature: str) -> set[str]:
    """The natural benefics of a chart: Jupiter, Venus, the Moon when waxing, and Mercury
    unless `mercury_nature` makes it malefic by association. The one definition used by
    Drik bala and by the rule library (e.g. yoga.gaja_kesari_bphs)."""
    out = set(PAKSHA_BENEFICS)
    if (positions["Moon"] - positions["Sun"]) % 360.0 < 180.0:
        out.add("Moon")
    if mercury_is_benefic(positions, mercury_nature):
        out.add("Mercury")
    return out


def drik_bala(planet: str, positions: dict[str, float], settings: ShadbalaSettings) -> float:
    """(Drishti from benefics - drishti from malefics) / 4, over the other six planets,
    benefics as `natural_benefics`."""
    benefics = natural_benefics(positions, settings.mercury_nature)
    total = 0.0
    for other in SEVEN:
        if other == planet:
            continue
        benefic = other in benefics
        v = drishti(other, positions[planet] - positions[other])
        total += v if benefic else -v
    return total / 4.0


# --- Assembly ------------------------------------------------------------------------

@dataclass
class PlanetShadbala:
    sthana: dict[str, float]
    dig: float
    kala: dict[str, float]
    chesta: float
    naisargika: float
    drik: float
    required: float

    @property
    def total(self) -> float:
        return (self.sthana["total"] + self.dig + self.kala["total"] + self.chesta
                + self.naisargika + self.drik)

    @property
    def ratio(self) -> float:
        return self.total / self.required


@dataclass
class War:
    planets: tuple[str, str]
    winner: str
    bala: float


@dataclass
class ShadbalaResult:
    planets: dict[str, PlanetShadbala]
    lords: dict[str, str]
    tribhaga_lord: str
    wars: list[War] = field(default_factory=list)


def shadbala(positions: dict[str, float], asc: float, *, mc: float | None, jd: float,
             sunrise: float, sunset: float, next_sunrise: float, ayanamsa: float,
             geo_lon: float | None = None,
             settings: ShadbalaSettings = ShadbalaSettings()) -> ShadbalaResult:
    pos = {p: v % 360.0 for p, v in positions.items()}
    d1_signs = {p: _sign(pos[p]) for p in SEVEN}
    lagna_sign = _sign(asc)
    points = dig_points(asc, mc, settings.dig_bala_points)

    if settings.nathonnata_noon == "apparent":
        noon = (sunrise + sunset) / 2.0
    elif settings.nathonnata_noon == "mean":
        if geo_lon is None:
            raise ValueError("nathonnata_noon='mean' needs the birth longitude")
        noon = math.floor(jd + 0.5 + geo_lon / 360.0) - geo_lon / 360.0
    else:
        raise ValueError(settings.nathonnata_noon)
    lords = kala_lords(jd, sunrise)
    tri = tribhaga_lord(jd, sunrise, sunset, next_sunrise)

    sthana, kala, dig, chesta = {}, {}, {}, {}
    for p in SEVEN:
        lon = pos[p]
        s = {"uchcha": uchcha_bala(p, lon),
             "saptavargaja": saptavargaja_bala(p, lon, d1_signs, settings.saptavargaja_scale),
             "ojhayugma": ojhayugma_bala(p, lon),
             "kendra": kendra_bala(d1_signs[p], lagna_sign),
             "drekkana": drekkana_bala(p, lon, settings.drekkana_bala)}
        s["total"] = sum(s.values())
        sthana[p] = s
        dig[p] = dig_bala(p, lon, points)
        k = {"nathonnata": nathonnata_bala(p, jd, noon),
             "paksha": paksha_bala(p, pos, settings),
             "tribhaga": 60.0 if p in (tri, "Jupiter") else 0.0}
        for name, value in KALA_LORD_BALA.items():
            k[name] = value if lords[name] == p else 0.0
        k["ayana"] = ayana_bala(p, lon, ayanamsa, jd, settings)
        k["yuddha"] = 0.0
        kala[p] = k

    wars = []
    for i, a in enumerate(YUDDHA_PLANETS):
        for b in YUDDHA_PLANETS[i + 1:]:
            if _fold(pos[a] - pos[b]) > YUDDHA_ORB:
                continue
            pre = {x: sthana[x]["total"] + dig[x] + sum(kala[x].values()) for x in (a, b)}
            win, lose = (a, b) if pre[a] >= pre[b] else (b, a)
            bala = abs(pre[a] - pre[b]) / abs(BIMBA_DIAMETER[a] - BIMBA_DIAMETER[b])
            kala[win]["yuddha"] += bala
            kala[lose]["yuddha"] -= bala
            wars.append(War(planets=(a, b), winner=win, bala=bala))
    for p in SEVEN:
        kala[p]["total"] = sum(kala[p].values())

    for p in SEVEN:
        if p == "Sun":
            chesta[p] = kala[p]["ayana"] if settings.chesta_luminaries == "bphs" else 0.0
        elif p == "Moon":
            chesta[p] = kala[p]["paksha"] if settings.chesta_luminaries == "bphs" else 0.0
        else:
            chesta[p] = chesta_kendra(p, pos[p] + ayanamsa, jd) / 3.0

    planets = {p: PlanetShadbala(sthana=sthana[p], dig=dig[p], kala=kala[p], chesta=chesta[p],
                                 naisargika=NAISARGIKA[p], drik=drik_bala(p, pos, settings),
                                 required=SHADBALA_REQUIRED[p]) for p in SEVEN}
    return ShadbalaResult(planets=planets, lords=lords, tribhaga_lord=tri, wars=wars)
