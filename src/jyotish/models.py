"""The chart object: a subset of the SPEC.md data schema that Phase 0-1 fills.
Every field here is produced by `chart.analyse`; fields the spec promises for later
phases are added when their layer lands, never stubbed with placeholder values."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Meta(BaseModel):
    engine: str = "0.1.0"
    ayanamsa: str = "lahiri"
    ayanamsa_value: float | None = None
    jd: float | None = None
    node: str = "true"
    node_aspects: bool = False
    house_system: str = "whole_sign"      # whole_sign | sripati (bhava chalit; needs the MC)
    kp_house_system: str = "placidus"
    dasha_year: float = 365.25
    rising_signs: str = "bphs"             # bphs | phaladeepika (Bhava Bala time bonus)
    twilight_minutes: float = 24.0         # one ghati either side of sunrise and sunset; BPHS 27.31 does not define it
    ishta_kashta: str = "bphs"             # bphs (28.2-6, Rasmis) | raman (geometric mean; unverified)
    chara_variant: str = "kn_rao"          # kn_rao | raman | rath (rules in dasha.CHARA_VARIANTS)
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
    bhava_madhya_sripati: list[float] = Field(default_factory=list)   # houses 1-12, when the MC is known
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
    """`lords` are planets (Vimshottari, Yogini) or sign names (Chara), maha first."""
    lords: list[str]
    start_jd: float
    end_jd: float
    tara: str | None = None
    names: list[str] | None = None   # Yogini: the yogini names


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


class HouseStrength(BaseModel):
    """BPHS 27.26-31, virupas."""
    madhya: float
    lord: str
    bhavadhipati: float     # the lord's Shadbala total
    dig: float
    drishti: float          # benefics +1/4, malefics -1/4, Jupiter and Mercury in full
    occupants: float        # +60 Jupiter, Mercury; -60 Saturn, Mars, Sun (each)
    time: float             # 15 by rising type and day / twilight / night birth
    total: float
    rupas: float


class IshtaKashta(BaseModel):
    ishta: float
    kashta: float
    uchcha_rasmi: float | None = None
    cheshta_rasmi: float | None = None


class BhavaBala(BaseModel):
    birth_time: str                              # day | twilight | night
    whole_sign: dict[int, HouseStrength]         # madhyas equal from the lagna degree
    sripati: dict[int, HouseStrength]


class Features(BaseModel):
    lordship: dict[str, list[int]]
    roles: dict[str, list[str]]
    aspects: list[tuple[str, int]]
    dispositors: Dispositors
    jaimini: Jaimini
    ashtakavarga: Ashtakavarga
    shadbala: Shadbala | None = None   # needs the birth moment, sunrises and (by default) the MC
    bhava_bala: BhavaBala | None = None   # needs Shadbala and the MC
    vimsopaka: dict[str, dict[str, float]]          # planet -> scheme -> 0-20 (BPHS 7.17-25)
    ishta_kashta: dict[str, IshtaKashta] | None = None   # needs Shadbala
    sudarshana_h10: dict[str, list[str]]


class Stability(BaseModel):
    """SPEC Layer 1b's three numbers, never pooled. `time`: share of the birth-time samples
    in which the finding holds. `ayanamsa`: share of Lahiri, Raman, KP. `house`: share of
    whole sign, Sripati. `label` is from `time`: unstable < 0.5 <= sensitive <= 0.8 < stable."""
    time: float
    ayanamsa: float
    house: float
    label: str


class FiredRule(BaseModel):
    """One rule fired from one basis (SPEC Layer 3). `scale` is the product of the
    modifiers in `applied`; `themes` are the rule's themes times that scale. Modifiers
    whose condition the chart could not evaluate are in `unknown`, never silently dropped.
    Stability (Layer 1b) is added by the sampler, not here."""
    id: str
    family: str
    school: str
    status: str        # experimental fires are recorded but kept out of default scoring
    basis: str
    nodes: list[str]
    scale: float
    themes: dict[str, float]
    applied: list[str] = Field(default_factory=list)
    unknown: list[str] = Field(default_factory=list)
    details: dict[str, Any] = Field(default_factory=dict)
    stability: Stability | None = None   # set by the uncertainty sampler (uncertainty.assess)


class BoundaryStability(BaseModel):
    """A dasha period's start under the three axes, in days. `time_share` is the share of
    birth-time samples in which the period exists at all (Chara and Yogini sequences can
    change with the lagna or the nakshatra)."""
    system: str
    lords: list[str]
    start_jd: float
    time_share: float
    time_range_days: float        # max - min over the samples
    time_sd_days: float
    ayanamsa_range_days: float | None   # None when the period is missing under some ayanamsa
    house_range_days: float | None


class RuleShare(BaseModel):
    """A rule that fires in some samples but not at the recorded time."""
    id: str
    basis: str
    planets: list[str]
    time: float


class Uncertainty(BaseModel):
    samples: int
    half_width_min: float
    shape: str
    center_jd: float
    ayanamsas: list[str]
    house_systems: list[str]
    varga_stability: dict[str, float]                  # the lagna's sign per varga, time axis
    placements: dict[str, dict[str, Stability]]        # varga -> body (and Asc) -> stability
    boundaries: list[BoundaryStability]
    rules_elsewhere: list[RuleShare]
    seconds: float


class KakshyaSpan(BaseModel):
    lord: str
    start_jd: float
    end_jd: float
    bindu: bool | None = None      # the lord's bindu in the transiting planet's BAV; None for nodes


class VedhaSpan(BaseModel):
    by: str
    start_jd: float
    end_jd: float


class TransitRow(BaseModel):
    """One body in one sign, ingress to egress (SPEC Layer 4 transit row). A row that
    starts or ends at the edge of the requested range is clipped there and says so."""
    kind: str = "transit"
    body: str
    sign: int
    sign_name: str
    start_jd: float
    end_jd: float
    entered: str | None            # "direct" | "retrograde"; None when clipped at range start
    clipped_start: bool = False
    clipped_end: bool = False
    houses: dict[str, int]         # from lagna, moon, sun
    bav: int | None                # transiting planet's own natal BAV in the sign; None for nodes
    sav: int
    grade: str | None              # Ashtakavarga grade from `bav` (Phaladeepika 23.11)
    gochara_good: bool             # a good house from the Moon (Phaladeepika 26.2)
    kakshya: list[KakshyaSpan]
    vedha: list[VedhaSpan] = Field(default_factory=list)
    vipareeta_vedha: list[VedhaSpan] = Field(default_factory=list)
    murthi: str | None = None      # slow planets entering a sign
    tags: list[str] = Field(default_factory=list)


class TimelineWindow(BaseModel):
    kind: str                      # sade_sati, kantaka_shani, ashtama_shani, jupiter_1_5_9_11, nodal_return, saturn_return
    start_jd: float
    end_jd: float
    tags: list[str]
    details: dict[str, Any] = Field(default_factory=dict)


class Timeline(BaseModel):
    start_jd: float
    end_jd: float
    ayanamsa: str
    node: str
    rows: list[TransitRow]
    windows: list[TimelineWindow]

    def active(self, jd: float) -> list[TimelineWindow]:
        return [w for w in self.windows if w.start_jd <= jd < w.end_jd]


class Chart(BaseModel):
    meta: Meta
    birth: Birth
    bodies: dict[str, Body]
    lagnas: Lagnas
    panchanga: PanchangaInfo | None = None
    vargas: dict[str, dict[str, int]]
    features: Features
    dashas: dict[str, list[DashaPeriod]] = Field(default_factory=dict)
    fired_rules: list[FiredRule] = Field(default_factory=list)
    uncertainty: Uncertainty | None = None   # set by uncertainty.assess
