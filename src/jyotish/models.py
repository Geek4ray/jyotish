"""The chart object: a subset of the SPEC.md data schema that Phase 0-1 fills.
Every field here is produced by `chart.analyse`; fields the spec promises for later
phases are added when their layer lands, never stubbed with placeholder values."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Meta(BaseModel):
    engine: str = "0.1.0"
    ayanamsa: str = "lahiri"
    ayanamsa_value: float | None = None
    jd: float | None = None
    node: str = "true"
    node_aspects: bool = False
    house_system: str = "whole_sign"
    kp_house_system: str = "placidus"
    dasha_year: float = 365.25
    karaka_scheme: int = 8
    ekadhipatya_nodes: bool = False
    ekadhipatya_zero_exempt: bool = False
    # Shadbala conventions where texts differ (sources in constants.py, Shadbala section).
    drekkana_bala: str = "bphs"            # bphs | phaladeepika
    saptavargaja_scale: str = "bphs"       # bphs | raman
    dig_bala_points: str = "cusps"         # cusps (asc, MC) | equal (asc + 90° steps)
    nathonnata_noon: str = "apparent"      # apparent (mid sunrise-sunset) | mean (LMT noon)
    mercury_nature: str = "association"    # association (malefic with a malefic) | benefic
    paksha_moon_double: bool = True
    ayana_obliquity: str = "bphs"          # bphs (24°) | true (mean obliquity of date)
    ayana_sun_double: bool = True
    chesta_luminaries: str = "bphs"        # bphs (Sun = ayana, Moon = paksha) | zero
    time_accuracy: str = "exact"


class TimePosterior(BaseModel):
    shape: str
    half_width_min: float
    samples: int
    rectified: bool = False


class Birth(BaseModel):
    utc: str | None = None
    lat: float | None = None
    lon: float | None = None
    tz: str | None = None
    time_posterior: TimePosterior | None = None


class TaraInfo(BaseModel):
    name: str
    count: int
    cycle: int
    adverse: bool
    special: str | None = None


class Body(BaseModel):
    lon: float
    sign: int
    sign_name: str
    deg: float
    nak: int
    nak_name: str
    pada: int
    nak_lord: str
    sub_lord: str
    sub_sub_lord: str
    tara: TaraInfo
    house: int
    speed: float | None = None
    retro: bool = False
    combust: bool = False
    boundary: bool = False
    dignity: str | None = None
    dignity_compound: str | None = None
    deep_exalt_dist: float | None = None
    avastha_baladi: str | None = None
    vargottama: bool = False
    marana_karaka_sthana: bool = False
    gandanta: bool = False
    pushkara_navamsa: bool = False
    pushkara_bhaga: bool = False


class Lagnas(BaseModel):
    asc: float
    asc_sign: int
    asc_sign_name: str
    asc_nak: str
    asc_nak_lord: str
    asc_tara: str
    mc: float | None = None
    cusps_placidus: dict[int, float] = Field(default_factory=dict)
    cusp_lords_kp: dict[int, dict[str, str]] = Field(default_factory=dict)


class PanchangaInfo(BaseModel):
    tithi: int
    tithi_lord: str
    paksha: str
    vara_lord: str
    nakshatra: str
    nakshatra_lord: str
    yoga: str
    yoga_lord: str
    karana: str
    day_birth: bool | None = None


class Loop(BaseModel):
    planets: list[str]
    houses: list[int] | None = None
    class_by_houses: str | None = None
    class_by_lordship: str | None = None
    taint: list[int] = Field(default_factory=list)


class Dispositors(BaseModel):
    sign: dict[str, list[str]]
    nakshatra: dict[str, list[str]]
    navamsa: dict[str, list[str]]
    loops: list[Loop]
    final_sign: list[str]
    final_nakshatra: list[str]
    final_navamsa: list[str]


class Jaimini(BaseModel):
    scheme: int
    karakas: dict[str, str]
    karakas_7: dict[str, str]
    karakamsa: int
    arudhas: dict[str, int]


class DashaPeriod(BaseModel):
    lords: list[str]
    start_jd: float
    end_jd: float
    tara: str | None = None


class Pinda(BaseModel):
    rasi: int
    graha: int
    sodhya: int


class Ashtakavarga(BaseModel):
    """Lists are indexed by sign, 0 = Aries. BAV has the seven planets and "Asc"; SAV,
    the reductions and the pindas cover the seven planets only."""
    BAV: dict[str, list[int]]
    SAV: list[int]
    trikona: dict[str, list[int]]
    ekadhipatya: dict[str, list[int]]
    pinda: dict[str, Pinda]
    kakshya: dict[str, str]
    kakshya_bindu: dict[str, bool]


class SthanaBala(BaseModel):
    uchcha: float
    saptavargaja: float
    ojhayugma: float
    kendra: float
    drekkana: float
    total: float


class KalaBala(BaseModel):
    nathonnata: float
    paksha: float
    tribhaga: float
    abda: float
    masa: float
    vara: float
    hora: float
    ayana: float
    yuddha: float
    total: float


class PlanetShadbala(BaseModel):
    """Virupas (60 = 1 rupa). `ratio` is total / required."""
    sthana: SthanaBala
    dig: float
    kala: KalaBala
    chesta: float
    naisargika: float
    drik: float
    total: float
    required: float
    ratio: float


class Yuddha(BaseModel):
    planets: list[str]
    winner: str
    bala: float


class Shadbala(BaseModel):
    planets: dict[str, PlanetShadbala]
    lords: dict[str, str]          # abda, masa, vara, hora
    tribhaga_lord: str
    wars: list[Yuddha] = Field(default_factory=list)


class Features(BaseModel):
    lordship: dict[str, list[int]]
    roles: dict[str, list[str]]
    aspects: list[tuple[str, int]]
    dispositors: Dispositors
    jaimini: Jaimini
    ashtakavarga: Ashtakavarga
    shadbala: Shadbala | None = None   # needs the birth moment, sunrises and (by default) the MC
    sudarshana_h10: dict[str, list[str]]


class Chart(BaseModel):
    meta: Meta
    birth: Birth
    bodies: dict[str, Body]
    lagnas: Lagnas
    panchanga: PanchangaInfo | None = None
    vargas: dict[str, dict[str, int]]
    features: Features
    dashas: dict[str, list[DashaPeriod]] = Field(default_factory=dict)
    uncertainty: dict | None = None
