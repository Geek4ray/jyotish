"""The pipeline: positions -> features (analyse), and birth data -> positions -> features
(compute). `analyse` needs no ephemeris, so the worked example in SPEC.md can be tested
from its printed longitudes alone."""

from __future__ import annotations

from datetime import datetime, timezone

from .argala import argala as compute_argala
from .ashtakavarga import ashtakavarga
from .bhava_bala import bhava_bala as compute_bhava_bala
from .constants import GRAHAS, SEVEN, SIGNS
from .dasha import chara, vimshottari, yogini
from .dignity import (
    aspects, baladi_avastha, deep_exaltation_distance, dignity, functional_roles, gandanta,
    house_of, is_boundary, is_combust, lordships, marana_karaka_sthana, pushkara_bhaga,
    pushkara_navamsa,
)
from .dispositors import navamsa_chains, nakshatra_chains, parivartanas, sign_chains
from .ephemeris import ayanamsa_value, compute_sky, julian_day, next_sunrise, sunrise_sunset
from .jaimini import all_arudhas, chara_karakas, karakamsa
from .models import (
    ArgalaOn, Ashtakavarga, BhavaBala, Birth, Body, HouseStrength, IshtaKashta, Chart, DashaPeriod, Dispositors, Features, Jaimini, Lagnas, Loop, Meta,
    KalaBala, PanchangaInfo, Pinda, PlanetShadbala, Shadbala, SthanaBala, TaraInfo,
    TimePosterior, Yuddha,
)
from .nakshatra import kp_sub_lords, nakshatra_of, navatara
from .houses import bhava_lordships, bhava_of, sripati_madhyas
from .panchanga import panchanga as compute_panchanga
from .rules import default_rules, evaluate_all
from .shadbala import ShadbalaSettings, ishta_kashta, shadbala as compute_shadbala
from .vimsopaka import vimsopaka
from .vargas import PRODUCTION_VARGAS, VARGAS, is_vargottama

ACCURACY_HALF_WIDTH_MIN = {"exact": 2.0, "within_15": 15.0, "approximate": 60.0, "unknown": 720.0}


def _tara_info(nak_index: int, moon_nak: int) -> TaraInfo:
    t = navatara(nak_index, moon_nak)
    return TaraInfo(name=t.name, count=t.count, cycle=t.cycle, adverse=t.adverse, special=t.special)


def analyse(positions: dict[str, float], asc: float, *, speeds: dict[str, float] | None = None,
            meta: Meta | None = None, birth: Birth | None = None, jd: float | None = None,
            mc: float | None = None, cusps: list[float] | None = None,
            sunrise: float | None = None, sunset: float | None = None,
            next_sunrise: float | None = None, dasha_levels: int = 2,
            rules=None) -> Chart:
    """Build the chart object from sidereal longitudes (all nine grahas) and the ascendant.
    `rules` is the rule library to evaluate (default: every rules/*.yaml); pass [] to skip."""
    meta = meta or Meta()
    birth = birth or Birth()
    speeds = speeds or {}
    asc = asc % 360.0
    lagna_sign = int(asc // 30)
    moon_nak = nakshatra_of(positions["Moon"]).index
    sun_lon = positions["Sun"]
    madhyas = sripati_madhyas(asc, mc) if mc is not None else []
    if meta.house_system == "sripati":
        if not madhyas:
            raise ValueError("house_system='sripati' needs the MC")
        house_lords = bhava_lordships(madhyas)
    elif meta.house_system == "whole_sign":
        house_lords = lordships(lagna_sign)
    else:
        raise ValueError(f"unknown house_system {meta.house_system!r}")

    bodies: dict[str, Body] = {}
    for name in GRAHAS:
        lon = positions[name] % 360.0
        sign = int(lon // 30)
        nak = nakshatra_of(lon)
        house = bhava_of(lon, madhyas) if meta.house_system == "sripati" else house_of(sign, lagna_sign)
        speed = speeds.get(name)
        retro = (speed is not None and speed < 0) or name in ("Rahu", "Ketu")
        body = Body(
            lon=lon, sign=sign, sign_name=SIGNS[sign], deg=lon % 30,
            nak=nak.index, nak_name=nak.name, pada=nak.pada, nak_lord=nak.lord,
            sub_lord=nak.sub_lord, sub_sub_lord=nak.sub_sub_lord,
            tara=_tara_info(nak.index, moon_nak), house=house, speed=speed, retro=retro,
            combust=is_combust(name, lon, sun_lon, retro) if name != "Sun" else False,
            boundary=is_boundary(lon), avastha_baladi=baladi_avastha(lon),
            vargottama=is_vargottama(lon),
            marana_karaka_sthana=marana_karaka_sthana(name, house),
            gandanta=gandanta(lon), pushkara_navamsa=pushkara_navamsa(lon),
            pushkara_bhaga=pushkara_bhaga(lon),
        )
        if name in SEVEN:
            body.dignity = dignity(name, lon)
            body.dignity_compound = dignity(name, lon, positions, compound=True)
            body.deep_exalt_dist = deep_exaltation_distance(name, lon)
        bodies[name] = body

    asc_nak = nakshatra_of(asc)
    cusps_map = {i + 1: c for i, c in enumerate(cusps)} if cusps else {}
    cusp_lords = {}
    for h, c in cusps_map.items():
        n = nakshatra_of(c)
        cusp_lords[h] = {"star": n.lord, "sub": n.sub_lord, "sub_sub": n.sub_sub_lord}
    # Whole-sign 7th cusp always available for KP reading when Placidus is not.
    if 7 not in cusp_lords:
        n7 = nakshatra_of((asc + 180.0) % 360.0)
        cusp_lords[7] = {"star": n7.lord, "sub": n7.sub_lord, "sub_sub": n7.sub_sub_lord}
    lagnas = Lagnas(
        asc=asc, asc_sign=lagna_sign, asc_sign_name=SIGNS[lagna_sign], asc_nak=asc_nak.name,
        asc_nak_lord=asc_nak.lord, asc_tara=navatara(asc_nak.index, moon_nak).name, mc=mc,
        cusps_placidus=cusps_map, cusp_lords_kp=cusp_lords, bhava_madhya_sripati=madhyas,
    )

    vargas = {v: {name: VARGAS[v](positions[name]) for name in GRAHAS} for v in PRODUCTION_VARGAS}
    for v in PRODUCTION_VARGAS:
        vargas[v]["Asc"] = VARGAS[v](asc)

    sc, nc, vc = sign_chains(positions), nakshatra_chains(positions), navamsa_chains(positions)
    loops = [Loop(planets=l) for l in sc.loops]
    for p in parivartanas(positions, lagna_sign):
        for loop in loops:
            if sorted(loop.planets) == list(p.planets):
                loop.houses = list(p.houses)
                loop.class_by_houses = p.class_by_houses
                loop.class_by_lordship = p.class_by_lordship
                loop.taint = list(p.taint)
    dispositors = Dispositors(
        sign=sc.chains, nakshatra=nc.chains, navamsa=vc.chains, loops=loops,
        final_sign=sc.final, final_nakshatra=nc.final, final_navamsa=vc.final,
    )

    planet_houses = {name: b.house for name, b in bodies.items()}
    sun_sign, moon_sign = bodies["Sun"].sign, bodies["Moon"].sign
    sudarshana_h10 = {
        "from_lagna": [n for n, b in bodies.items() if house_of(b.sign, lagna_sign) == 10],
        "from_moon": [n for n, b in bodies.items() if house_of(b.sign, moon_sign) == 10],
        "from_sun": [n for n, b in bodies.items() if house_of(b.sign, sun_sign) == 10],
    }
    sb_model, sb_raw = _shadbala(positions, asc, meta, birth, jd, mc, sunrise, sunset, next_sunrise)
    av = ashtakavarga(positions, asc, nodes_occupy=meta.ekadhipatya_nodes,
                      zero_exempt=meta.ekadhipatya_zero_exempt)
    features = Features(
        lordship=house_lords, roles=functional_roles(lagna_sign, house_lords),
        aspects=aspects(planet_houses), dispositors=dispositors,
        jaimini=Jaimini(scheme=meta.karaka_scheme, karakas=chara_karakas(positions, 8),
                        karakas_7=chara_karakas(positions, 7),
                        karakamsa=karakamsa(positions, meta.karaka_scheme),
                        arudhas=all_arudhas(lagna_sign, positions)),
        ashtakavarga=Ashtakavarga(
            BAV=av.bav, SAV=av.sav, trikona=av.trikona, ekadhipatya=av.ekadhipatya,
            pinda={p: Pinda(rasi=x.rasi, graha=x.graha, sodhya=x.sodhya) for p, x in av.pinda.items()},
            kakshya=av.kakshya, kakshya_bindu=av.kakshya_bindu),
        sudarshana_h10=sudarshana_h10,
        shadbala=sb_model,
        vimsopaka=vimsopaka(positions),
        argala={k: ArgalaOn(**v) for k, v in compute_argala(
            positions, lagna_sign, all_arudhas(lagna_sign, positions)["AL"], nodes=meta.argala_nodes,
            ak=chara_karakas(positions, meta.karaka_scheme)["AK"],
            mercury_nature=meta.mercury_nature).items()},
    )

    pinfo = None
    if jd is not None:
        p = compute_panchanga(sun_lon, positions["Moon"], jd, sunrise, sunset)
        pinfo = PanchangaInfo(tithi=p.tithi, tithi_lord=p.tithi_lord, paksha=p.paksha,
                              vara_lord=p.vara_lord, nakshatra=p.nakshatra,
                              nakshatra_lord=p.nakshatra_lord, yoga=p.yoga, yoga_lord=p.yoga_lord,
                              karana=p.karana, day_birth=p.day_birth)

    dashas = {}
    if jd is not None:
        periods = vimshottari(positions["Moon"], jd, levels=dasha_levels, year_length=meta.dasha_year)
        dashas["vimshottari"] = [
            DashaPeriod(lords=list(p.lords), start_jd=p.start_jd, end_jd=p.end_jd,
                        tara=bodies[p.lord].tara.name)
            for p in periods
        ]
        dashas["yogini"] = [
            DashaPeriod(lords=list(p.lords), start_jd=p.start_jd, end_jd=p.end_jd,
                        tara=bodies[p.lord].tara.name, names=list(p.names))
            for p in yogini(positions["Moon"], jd, levels=min(dasha_levels, 2),
                            year_length=meta.dasha_year)
        ]
        dashas["chara"] = [
            DashaPeriod(lords=list(p.lords), start_jd=p.start_jd, end_jd=p.end_jd)
            for p in chara(positions, lagna_sign, jd, levels=min(dasha_levels, 2),
                           year_length=meta.dasha_year, variant=meta.chara_variant)
        ]

    if sb_raw is not None:
        aya = meta.ayanamsa_value if meta.ayanamsa_value is not None else ayanamsa_value(jd, meta.ayanamsa)
        features.ishta_kashta = {p: IshtaKashta(**v) for p, v in
                                 ishta_kashta(positions, jd, aya, sb_raw, meta.ishta_kashta).items()}
    if features.shadbala is not None and mc is not None:
        bb = compute_bhava_bala(
            positions, asc, mc, madhyas, {p: x.total for p, x in features.shadbala.planets.items()},
            jd=jd, sunrise=sunrise, sunset=sunset, next_sunrise=next_sunrise,
            rising=meta.rising_signs, twilight_minutes=meta.twilight_minutes,
            mercury_nature=meta.mercury_nature)
        features.bhava_bala = BhavaBala(
            birth_time=bb["birth_time"],
            whole_sign={h: HouseStrength(**x) for h, x in bb["whole_sign"].items()},
            sripati={h: HouseStrength(**x) for h, x in bb["sripati"].items()})

    chart = Chart(meta=meta, birth=birth, bodies=bodies, lagnas=lagnas, panchanga=pinfo,
                  vargas=vargas, features=features, dashas=dashas)
    # Layer 3 reads only the finished feature object, never raw longitudes.
    library = default_rules() if rules is None else rules
    chart.fired_rules = evaluate_all(library, chart)
    from .scoring import score
    chart.scored = score(chart, library)
    return chart


def _shadbala(positions, asc, meta, birth, jd, mc, sunrise, sunset, next_sunrise):
    """Shadbala needs the birth moment and the day's sunrises (Kala bala), and the MC
    unless Dig bala is read from equal houses. Without them the field is absent."""
    if None in (jd, sunrise, sunset, next_sunrise):
        return None, None
    if mc is None and meta.dig_bala_points == "cusps":
        return None, None
    aya = meta.ayanamsa_value if meta.ayanamsa_value is not None else ayanamsa_value(jd, meta.ayanamsa)
    r = compute_shadbala(positions, asc, mc=mc, jd=jd, sunrise=sunrise, sunset=sunset,
                         next_sunrise=next_sunrise, ayanamsa=aya, geo_lon=birth.lon,
                         settings=ShadbalaSettings.from_obj(meta))
    model = Shadbala(
        planets={p: PlanetShadbala(sthana=SthanaBala(**x.sthana), dig=x.dig, kala=KalaBala(**x.kala),
                                   chesta=x.chesta, naisargika=x.naisargika, drik=x.drik,
                                   total=x.total, required=x.required, ratio=x.ratio)
                 for p, x in r.planets.items()},
        lords=r.lords, tribhaga_lord=r.tribhaga_lord,
        wars=[Yuddha(planets=list(w.planets), winner=w.winner, bala=w.bala) for w in r.wars])
    return model, r


def compute(utc: datetime, lat: float, lon: float, *, ayanamsa: str = "lahiri",
            true_node: bool = True, time_accuracy: str = "exact", tz: str | None = None,
            dasha_levels: int = 2, house_system: str = "whole_sign", rules=None) -> Chart:
    """Birth moment (UTC) and place -> chart."""
    utc = utc.astimezone(timezone.utc) if utc.tzinfo else utc.replace(tzinfo=timezone.utc)
    hour = utc.hour + utc.minute / 60 + utc.second / 3600
    jd = julian_day(utc.year, utc.month, utc.day, hour)
    sky = compute_sky(jd, lat, lon, ayanamsa=ayanamsa, true_node=true_node)
    rise, sset = sunrise_sunset(jd, lat, lon)
    rise_next = next_sunrise(sset, lat, lon)
    positions = {n: b.lon for n, b in sky.bodies.items()}
    speeds = {n: b.speed for n, b in sky.bodies.items()}
    meta = Meta(ayanamsa=ayanamsa, ayanamsa_value=sky.ayanamsa_value, jd=jd,
                node="true" if true_node else "mean", time_accuracy=time_accuracy,
                house_system=house_system)
    birth = Birth(utc=utc.isoformat(), lat=lat, lon=lon, tz=tz,
                  time_posterior=TimePosterior(shape="uniform" if time_accuracy != "approximate" else "gaussian",
                                               half_width_min=ACCURACY_HALF_WIDTH_MIN[time_accuracy],
                                               samples=0))
    return analyse(positions, sky.asc, speeds=speeds, meta=meta, birth=birth, jd=jd, mc=sky.mc,
                   cusps=sky.cusps_placidus, sunrise=rise, sunset=sset, next_sunrise=rise_next,
                   dasha_levels=dasha_levels, rules=rules)
