"""Command line: print the reference chart, compute a chart, recover an instant, write a
reading (`jyotish read`: birth data and a question -> reading JSON and a Markdown page), and
re-render a reading's page from its JSON (`jyotish page --from`, no model call)."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from .chart import analyse, compute
from .constants import SIGNS
from .ephemeris import recover_instant
from .models import Chart
from .reference import REFERENCE_ASC, REFERENCE_POSITIONS, REFERENCE_SPEEDS, reference_time_inputs


def _fmt_lon(lon: float) -> str:
    sign = int(lon // 30)
    d = lon % 30
    m = (d - int(d)) * 60
    s = (m - int(m)) * 60
    return f"{int(d):02d}°{int(m):02d}'{int(round(s)):02d}\" {SIGNS[sign]}"


def print_chart(chart: Chart, scored_from: Chart | None = None) -> None:
    """The chart's sections; the Life areas from `scored_from` when given (the reference command
    prints the positions the app printed and the tiers of the true-time, assessed chart: a chart
    built from positions alone has no KP cusps but the 7th, so its KP votes are not applicable
    rather than abstentions and its tiers are not the worked example's; review 2026-10-23, F16)."""
    print(f"Lagna: {_fmt_lon(chart.lagnas.asc)} ({chart.lagnas.asc_nak}, lord {chart.lagnas.asc_nak_lord}, tara {chart.lagnas.asc_tara})")
    print(f"{'Body':8} {'Position':22} {'Nak-pada':18} {'Lord':8} {'Sub':8} {'H':>2} {'Dignity':12} {'Avastha':8} {'Tara':9} flags")
    for name, b in chart.bodies.items():
        flags = " ".join(f for f, on in (("R", b.retro), ("#", b.combust), ("edge", b.boundary),
                                         ("VG", b.vargottama), ("MKS", b.marana_karaka_sthana),
                                         ("PushN", b.pushkara_navamsa), ("PushB", b.pushkara_bhaga),
                                         ("gand", b.gandanta)) if on)
        dig = b.dignity or "-"
        if b.dignity_compound and b.dignity_compound != b.dignity:
            dig += f"/{b.dignity_compound}"
        print(f"{name:8} {_fmt_lon(b.lon):22} {b.nak_name + '-' + str(b.pada):18} {b.nak_lord:8} {b.sub_lord:8} {b.house:>2} {dig:12} {b.avastha_baladi or '-':8} {b.tara.name:9} {flags}")
    f = chart.features
    print("\nLordship:", {p: h for p, h in f.lordship.items()})
    print("Roles:", {p: r for p, r in f.roles.items() if r})
    print("D9:", {n: SIGNS[s] for n, s in chart.vargas["D9"].items()})
    d = f.dispositors
    print("\nSign chains:", d.sign)
    print("Sign loops:", d.loops, "final:", d.final_sign)
    print("Nakshatra chains:", d.nakshatra, "final:", d.final_nakshatra)
    print("Navamsa final:", d.final_navamsa)
    j = f.jaimini
    print("\nChara karakas (8):", j.karakas)
    print("Chara karakas (7):", j.karakas_7)
    print("Karakamsa:", SIGNS[j.karakamsa])
    print("Arudhas:", {k: SIGNS[v] for k, v in j.arudhas.items() if k in ("AL", "UL", "A2", "A7", "A10")})
    print("Sudarshana H10:", f.sudarshana_h10)
    print("KP cusp lords:", chart.lagnas.cusp_lords_kp)
    print_ashtakavarga(chart)
    print_shadbala(chart)
    print_bhava_bala(chart)
    print_vimsopaka_ishta(chart)
    print_argala(chart)
    print_fired_rules(chart)
    print_scored(scored_from or chart)
    if chart.meta.jd is not None:
        print_current_transits(chart)
    if chart.panchanga:
        print("\nPanchanga:", chart.panchanga.model_dump())
    if chart.dashas:
        print("\nVimshottari (maha):")
        for p in chart.dashas["vimshottari"]:
            if len(p.lords) == 1:
                print(f"  {p.lords[0]:8} jd {p.start_jd:.2f} – {p.end_jd:.2f}  ({(p.end_jd - p.start_jd) / 365.25:.1f} y) tara {p.tara}")
        print_dasha_sequence(chart)


def _date(jd: float) -> str:
    import swisseph as swe
    y, m, d, _ = swe.revjul(jd, swe.GREG_CAL)
    return f"{y:04d}-{m:02d}-{d:02d}"


def print_dasha_sequence(chart: Chart) -> None:
    """Yogini and Chara: maha periods, and the antardashas running at birth."""
    birth = chart.meta.jd
    for system in ("yogini", "chara"):
        periods = chart.dashas.get(system)
        if not periods:
            continue
        label = {"yogini": "Yogini", "chara": f"Chara ({chart.meta.chara_variant})"}[system]
        print(f"\n{label} (maha; year {chart.meta.dasha_year} days):")
        mahas = [p for p in periods if len(p.lords) == 1]
        for p in mahas[:12]:
            name = f"{p.names[0]}/{p.lords[0]}" if p.names else p.lords[0]
            print(f"  {name:18} {_date(p.start_jd)} – {_date(p.end_jd)}  ({(p.end_jd - p.start_jd) / chart.meta.dasha_year:5.2f} y)")
        if birth is not None:
            now = [p for p in periods if len(p.lords) == 2 and p.start_jd <= birth < p.end_jd]
            if now:
                print(f"  at birth: {' / '.join(now[0].names or now[0].lords)}")


def print_ashtakavarga(chart: Chart) -> None:
    av = chart.features.ashtakavarga
    m = chart.meta

    def row(label: str, vals: list[int]) -> str:
        return f"  {label:9}" + "".join(f"{v:>4}" for v in vals) + f"  {sum(vals):>4}"

    print("\nAshtakavarga (BAV by sign; SAV = seven planets, lagna excluded)")
    print(f"  {'':9}" + "".join(f"{s[:3]:>4}" for s in SIGNS) + "   tot")
    for name, vals in av.BAV.items():
        print(row(name, vals))
    print(row("SAV", av.SAV))
    occ = "seven planets and nodes" if m.ekadhipatya_nodes else "seven planets"
    zero = "zero exempt" if m.ekadhipatya_zero_exempt else "no zero exemption (BPHS 68)"
    print(f"After Trikona and Ekadhipatya (occupants: {occ}; {zero}):")
    for name, vals in av.ekadhipatya.items():
        print(row(name, vals))
    print("Sodhya Pinda (rasi + graha):",
          {p: f"{x.rasi}+{x.graha}={x.sodhya}" for p, x in av.pinda.items()})
    print("Kakshya lord (bindu in own BAV):",
          {p: f"{l}{' +' if av.kakshya_bindu[p] else ' -'}" for p, l in av.kakshya.items()})


def print_shadbala(chart: Chart) -> None:
    sb = chart.features.shadbala
    if sb is None:
        print("\nShadbala: not computed (needs the birth moment, sunrises and the MC)")
        return
    m = chart.meta
    print("\nShadbala (virupas; ratio = total / required minimum)")
    print(f"  {'':8}{'sthana':>8}{'dig':>7}{'kala':>8}{'chesta':>8}{'naisarg':>8}{'drik':>7}"
          f"{'total':>8}{'req':>6}{'ratio':>7}")
    for p, x in sb.planets.items():
        print(f"  {p:8}{x.sthana.total:8.2f}{x.dig:7.2f}{x.kala.total:8.2f}{x.chesta:8.2f}"
              f"{x.naisargika:8.2f}{x.drik:7.2f}{x.total:8.2f}{x.required:6.0f}{x.ratio:7.2f}")
    print("  Sthana parts:", {p: {k: round(v, 2) for k, v in x.sthana.model_dump().items() if k != "total"}
                              for p, x in sb.planets.items()})
    print("  Kala parts:", {p: {k: round(v, 2) for k, v in x.kala.model_dump().items() if k != "total" and v}
                            for p, x in sb.planets.items()})
    print("  Lords:", sb.lords, "tribhaga:", sb.tribhaga_lord, "wars:", [w.model_dump() for w in sb.wars] or "none")
    print(f"  Settings: drekkana={m.drekkana_bala} saptavargaja={m.saptavargaja_scale} dig={m.dig_bala_points} "
          f"noon={m.nathonnata_noon} mercury={m.mercury_nature} moon_paksha_x2={m.paksha_moon_double} "
          f"ayana={m.ayana_obliquity} sun_ayana_x2={m.ayana_sun_double} chesta_luminaries={m.chesta_luminaries}")


def print_vimsopaka_ishta(chart: Chart) -> None:
    from .constants import vimsopaka_label
    f = chart.features
    print("\nVimsopaka (BPHS 7.17-25; 0-20)      shad  sapta  dasa  shodasa")
    for p, row in f.vimsopaka.items():
        print(f"  {p:8}" + " " * 26 + "".join(f"{row[s]:6.2f}" for s in ("shadvarga", "saptavarga", "dasavarga", "shodasavarga"))
              + f"  {vimsopaka_label(row['shodasavarga'])}")
    if f.ishta_kashta:
        print(f"Ishta / Kashta ({chart.meta.ishta_kashta}):",
              "  ".join(f"{p} {x.ishta:.1f}/{x.kashta:.1f}" for p, x in f.ishta_kashta.items()))


def print_argala(chart: Chart) -> None:
    print(f"\nArgala (Jaimini Upadesa Sutras 1.1.4-9 as read by Rath; BPHS 31.2-9; nodes: {chart.meta.argala_nodes})")
    print("  place: planets [obstructors] outcome; (rev) = counted backwards, Ketu in the sign")
    for key, a in chart.features.argala.items():
        if not a.places and not a.vipareeta:
            continue
        parts = [f"{x.house}: {' '.join(x.by)}" + (f" [{' '.join(x.blocked_by)}]" if x.blocked_by else "")
                 + f" {x.outcome}" for x in a.places]
        extra = f"  Vipareeta ({' '.join(a.third_malefics)})" if a.vipareeta else ""
        print(f"  {key:4} " + "; ".join(parts) + extra + ("  (rev)" if a.reversed else ""))


def print_bhava_bala(chart: Chart) -> None:
    bb = chart.features.bhava_bala
    if bb is None:
        return
    print(f"\nBhava Bala (BPHS 27.26-31; rupas; {bb.birth_time} birth; rising signs {chart.meta.rising_signs})")
    print("  " + " " * 8 + "".join(f"{'H' + str(h):>6}" for h in range(1, 13)))
    for name, table in (("whole", bb.whole_sign), ("sripati", bb.sripati)):
        print(f"  {name:8}" + "".join(f"{table[h].rupas:6.2f}" for h in range(1, 13)))


def print_scored(chart: Chart) -> None:
    sc = chart.scored
    if sc is None:
        return
    print(f"\nLife areas (Layer 5, weights {sc.weights}; tiers are agreement between signal families, not outcomes)")
    for name, a in sorted(sc.areas.items(), key=lambda kv: (kv[1].emphasised is False, -(kv[1].score_classical or 0))):
        if a.score_classical is None or not a.emphasised:
            print(f"  {name:14} {a.tier}")
            continue
        flags = f"  [{', '.join(a.polarity)}]" if a.polarity else ""
        st = a.stability
        stab = f"  stability {st.time:.2f}/{st.ayanamsa:.2f}/{st.house:.2f}" if st else ""
        print(f"  {name:14} {a.tier:14} {a.direction:10} S {a.score_classical:6.2f}  agreement "
              f"{a.confidence:.2f}{flags}{stab}{'' if a.narrate else '  (not narrated: unstable)'}")
    d = sc.driver
    print(f"  Top: {', '.join(sc.top)}.  Driver ({d.formula}): {d.driver}"
          f" (alternates from the dispositor graph: {', '.join(d.alternates) or 'none'})")
    print("  Driver ranking:", ", ".join(f"{r['planet']} {r['score']:.2f}" for r in d.ranking))


def print_fired_rules(chart: Chart) -> None:
    print("\nFired rules (scale = product of applied modifiers; stability not yet sampled)")
    if not chart.fired_rules:
        print("  none")
    for f in chart.fired_rules:
        print(f"  {f.id:26} {f.basis:6} {' '.join(f.nodes):24} scale {f.scale:.3f}")
        for a in f.applied:
            print(f"      applied: {a}")
        for u in f.unknown:
            print(f"      not evaluated (feature not computed): {u}")
        extra = {k: v for k, v in f.details.items() if k != "relations"}
        if extra or f.details.get("relations"):
            print(f"      {', '.join(f.details.get('relations', []))} {extra if extra else ''}".rstrip())


def print_current_transits(chart: Chart, now_jd: float | None = None) -> None:
    """Transit rows and named windows in force now (or at `now_jd`), from a timeline
    spanning ten years either side so that long windows are seen whole."""
    from datetime import datetime, timezone
    from .transits import transit_timeline
    if now_jd is None:
        u = datetime.now(timezone.utc)
        import swisseph as swe
        now_jd = swe.julday(u.year, u.month, u.day, u.hour + u.minute / 60)
    tl = transit_timeline(chart, now_jd - 3652.5, now_jd + 3652.5)
    print(f"\nTransits on {_date(now_jd)} (from the Moon's sign; Phaladeepika 26)")
    for r in tl.rows:
        if r.start_jd <= now_jd < r.end_jd:
            v = [x.by for x in r.vedha if x.start_jd <= now_jd < x.end_jd]
            k = next((x for x in r.kakshya if x.start_jd <= now_jd < x.end_jd), None)
            print(f"  {r.body:8} {r.sign_name:12} {_date(r.start_jd)} – {_date(r.end_jd)}  "
                  f"H(lagna/moon/sun) {r.houses['lagna']}/{r.houses['moon']}/{r.houses['sun']}  "
                  f"BAV {r.bav if r.bav is not None else '-'} SAV {r.sav}  "
                  f"{'good' if r.gochara_good else 'not good'}"
                  f"{' (vedha: ' + ', '.join(v) + ')' if v else ''}"
                  f"  kakshya {k.lord if k else '-'}  murthi {r.murthi or '-'}")
    active = tl.active(now_jd)
    print("  Windows now:", "none" if not active else "")
    for w in active:
        print(f"    {w.kind:18} {_date(w.start_jd)} – {_date(w.end_jd)}  {' '.join(w.tags[1:])}")


def print_timing(chart: Chart, query) -> None:
    from .timing import answer
    ans = answer(chart, query)
    st = ans.area_stability
    print(f"\nTiming ({ans.formula}): {query.area}, {query.start} to {query.end} "
          f"({', '.join(query.systems)}; basis {query.basis})")
    print(f"  area {ans.area_tier} (S {ans.area_score:.2f}"
          + (f", stability {st.time:.2f}/{st.ayanamsa:.2f}/{st.house:.2f}" if st else "") + "), narrated beside the windows")
    print("  joint = 0.6 q + 0.4 t" if ans.formula in ("v2", "v2.1") else "  joint = (S / population p90) x dasha quality + transit activation")

    def line(w, label=""):
        per = "; ".join(f"{k} {'/'.join(v)}" for k, v in w.periods.items())
        stab = (f"  edges ±{w.stability['time_range_days'] / 2:.1f} d (ayanamsa {w.stability['ayanamsa_range_days']:.0f} d)"
                if w.stability else "")
        conf = f" {w.confidence}" if w.confidence else ""
        marks = "".join(f"  {t.replace('dasha_', '')}" for t in w.tags)
        print(f"  {label}{_date(w.start_jd)} – {_date(w.end_jd)}  joint {w.joint:.2f} (q {w.dasha_quality:.2f}, "
              f"t {w.transit_activation:.2f}){conf}  [{per}]{stab}{marks}")
        sp = w.derivation.get("strongest_piece")
        if sp and (sp["start_jd"], sp["end_jd"]) != (w.start_jd, w.end_jd):
            print(f"      strongest {_date(sp['start_jd'])} – {_date(sp['end_jd'])}: joint {sp['joint']:.2f} (t {sp['t']:.2f})")
    for w in ans.windows:
        line(w)
    if ans.avoid is not None:
        line(ans.avoid, "avoid: ")


def print_stability(chart: Chart) -> None:
    """Layer 1b summary: three numbers per finding (time / ayanamsa / house), never pooled."""
    u = chart.uncertainty
    if u is None:
        return
    print(f"\nStability (Layer 1b): {u.samples} birth times, {u.shape} ±{u.half_width_min:g} min; "
          f"ayanamsas {', '.join(u.ayanamsas)}; houses {', '.join(u.house_systems)}; {u.seconds:.1f} s")
    print("  numbers are time / ayanamsa / house; label from time (stable > 0.8 >= sensitive >= 0.5 > unstable)")
    for f in chart.fired_rules:
        st = f.stability
        print(f"  {f.id:30} {f.basis:6} {st.time:4.2f} / {st.ayanamsa:4.2f} / {st.house:4.2f}  {st.label}")
    for r in u.rules_elsewhere:
        print(f"  (fires in {r.time:.0%} of samples only) {r.id} {r.basis} {' '.join(r.planets)}")
    lag = {v: u.placements[v]["Asc"] for v in ("D1", "D9", "D10", "D12", "D30", "D60")}
    print("  Lagna by varga:", "  ".join(f"{v} {x.time:.2f}/{x.ayanamsa:.2f}" for v, x in lag.items()))
    shaky = sorted(((x.time, v, b) for v, row in u.placements.items() for b, x in row.items()
                    if b != "Asc" and x.time < 0.8), key=lambda t: t[0])
    if shaky:
        print("  Planet placements below 0.8:", ", ".join(f"{b} {v} {t:.2f}" for t, v, b in shaky[:8]))
    mahas = [b for b in u.boundaries if b.system == "vimshottari" and len(b.lords) == 1]
    if mahas:
        b = mahas[1]
        print(f"  Vimshottari maha starts: ±{b.time_range_days / 2:.1f} days over the samples "
              f"(sd {b.time_sd_days:.1f}); {b.ayanamsa_range_days:.0f} days across ayanamsas")
    if chart.scored is not None:
        rows = [(n, a) for n, a in chart.scored.areas.items() if a.stability is not None and a.emphasised]
        print("  Life-area tiers:", "  ".join(f"{n} {a.tier} {a.stability.time:.2f}/{a.stability.ayanamsa:.2f}/"
                                              f"{a.stability.house:.2f}" for n, a in rows))
    moved = [b for b in u.boundaries if b.time_share < 1.0]
    if moved:
        print(f"  {len(moved)} dasha periods do not exist in every sample (sequence changes)")


def _birth_utc(day: str, clock: str, tz: str):
    from .service import birth_utc
    return birth_utc(day, clock, tz)


def _birth(args):
    import sys
    from pydantic import ValidationError
    from .service import BirthInput
    try:
        return _birth_input(args, BirthInput)
    except ValidationError as e:
        for err in e.errors():
            print(f"birth data refused: {err['msg']}", file=sys.stderr)
        raise SystemExit(2)


def _birth_input(args, BirthInput):
    return BirthInput(date=args.date, time=args.time, tz=args.tz, lat=args.lat, lon=args.lon,
                      accuracy=args.accuracy, node=args.node, place=args.place, seed=args.seed)


def _assess(args):
    """The assessed chart, from the cache when this birth data, these conventions and this
    seed have been run before (jyotish.cache)."""
    import sys
    from .service import assess_birth
    chart, source, _ = assess_birth(_birth(args))
    print(f"chart: {source}" + (" (cached run of the 200-sample assess)" if source != "computed" else ""),
          file=sys.stderr)
    return chart


def _birth_flags(p) -> None:
    p.add_argument("--date", required=True, help="local birth date, YYYY-MM-DD")
    p.add_argument("--time", required=True, help="local birth time, HH:MM[:SS]")
    p.add_argument("--tz", required=True, help="IANA timezone (Asia/Kolkata) or UTC offset (+05:30)")
    p.add_argument("--lat", type=float, required=True)
    p.add_argument("--lon", type=float, required=True)
    p.add_argument("--accuracy", default="exact", choices=["exact", "within_15", "approximate", "unknown"])
    p.add_argument("--node", default="true", choices=["true", "mean"],
                   help="lunar node (engine default true; the reference app uses mean)")
    p.add_argument("--place", help="place name for the header, e.g. 'Rewari, Haryana' (positions use --lat/--lon)")
    p.add_argument("--seed", type=int, default=0, help="birth-time sampler seed (default 0)")


def cmd_page(args) -> int:
    """Re-render the Markdown page from an existing reading JSON: recompute the chart from the
    birth-data flags (the learner tables are the engine's, so they need the chart), check it
    against the reading's Chart header, and render. No model call."""
    import sys
    from pathlib import Path
    from .narrate import Reading, chart_header
    from .page import render
    src = Path(args.from_)
    reading = Reading(**json.loads(src.read_text()))
    chart = _assess(args)
    want, got = reading.chart, chart_header(chart)
    diff = [k for k in ("birth_utc", "lat", "lon", "accuracy", "conventions", "sampler") if want.get(k) != got.get(k)]
    if want.get("seed") is not None and want["seed"] != args.seed:
        diff.append("seed")
    if reading.engine != chart.meta.engine:
        diff.append("engine")
    if diff:
        print(f"the birth-data flags do not reproduce {src}: {', '.join(diff)} differ", file=sys.stderr)
        for k in diff:
            print(f"  {k}: reading {want.get(k, reading.engine)!r} != flags {got.get(k, chart.meta.engine)!r}",
                  file=sys.stderr)
        return 2
    try:
        page = render(reading, chart)
        if args.json_out:
            from .narrate import upgrade_reading
            upgraded = upgrade_reading(reading, chart)
            Path(args.json_out).write_text(json.dumps(upgraded.model_dump(), indent=1, ensure_ascii=False,
                                                      default=str) + "\n")
            print(f"wrote {args.json_out}: the reading with the current engine-derived fields (learner blocks, "
                  "timing line); the model's text is unchanged")
    except (ValueError, KeyError) as e:
        print(str(e), file=sys.stderr)
        return 2
    out = Path(args.out) if args.out else src.with_suffix(".md")
    out.write_text(page)
    print(f"wrote {out} from {src} (no model call)")
    return 0


def cmd_read(args) -> int:
    """assess -> score -> route -> narrate -> <out>.json and <out>.md. Returns the exit code."""
    import sys
    from pathlib import Path
    from .narrate import NarrationError
    from .service import make_reading
    chart = _assess(args)
    try:
        reading, page = make_reading(_birth(args), args.question, chart=chart, as_of=args.as_of,
                                     model_fixture=args.model_fixture, depth=args.depth,
                                     writer_model=args.writer_model, writer_effort=args.writer_effort)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 2
    except NarrationError as e:
        print(f"narration failed: {e}", file=sys.stderr)
        for err in e.errors:
            print(f"  - {err}", file=sys.stderr)
        return 2
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".json").write_text(json.dumps(reading.model_dump(), indent=1, ensure_ascii=False, default=str) + "\n")
    out.with_suffix(".md").write_text(page)
    print(f"wrote {out.with_suffix('.json')} and {out.with_suffix('.md')} ({', '.join(a.name for a in reading.areas)}; "
          f"writer {reading.writer['model'] + ' at ' + reading.writer['effort'] if not args.model_fixture else 'replayed'}, "
          f"{reading.attempts} attempt(s))")
    if not reading.narration_complete:
        gaps = [g["finding_id"] for a in reading.areas for g in a.narration_gaps]
        print(f"narration incomplete: {len(gaps)} finding(s) not narrated within the checks"
              + (f" ({', '.join(gaps)})" if gaps else "")
              + ("; the summary is the engine's own" if reading.summary.source == "engine" else ""), file=sys.stderr)
    return 0


def cmd_outcomes(args) -> int:
    import os
    from . import outcomes as oc
    if args.cmd == "outcomes" and args.ocmd == "status":
        t = oc.rule_testability()
        n = sum(1 for v in t.values() if v["status"] == "testable")
        print(f"{n} of {len(t)} rules testable against measured outcomes; {len(t) - n} not_testable_yet")
        for rid, v in sorted(t.items()):
            if v["status"] == "not_testable_yet":
                print(f"  not_testable_yet  {rid}  (outcomes map to nothing measured)")
        return 0
    url = args.database or os.environ.get("JYOTISH_DATABASE_URL", "sqlite:///jyotish.db")
    Session = oc.sessionmaker_for(url)
    with Session.begin() as s:
        if args.cmd == "subject":
            counts = oc.erase(s, args.subject_id, args.by)
            print(f"erased subject {args.subject_id}: " + ", ".join(f"{v} {k}" for k, v in counts.items()) + " (logged)")
            return 0
        if args.ocmd == "consent":
            oc.add_consent(s, args.consent_id, args.subject, args.form, args.track, args.by)
            print(f"consent {args.consent_id} recorded for {args.subject}")
            return 0
        if args.ocmd == "withdraw":
            oc.withdraw_consent(s, args.consent_id)
            print(f"consent {args.consent_id} withdrawn")
            return 0
        res = oc.import_rows(s, oc.read_sheet(Path(args.csv)), entered_by=args.entered_by)
    print(f"{res.accepted} event rows stored ({res.subjects_created} new subjects); {len(res.refused)} refused")
    for x in res.refused:
        print(f"  row {x['row']} ({x['subject_id']}): {'; '.join(x['reasons'])}")
    return 1 if res.refused else 0


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="jyotish")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("reference", help="print the SPEC.md reference chart from its printed longitudes")
    c = sub.add_parser("compute", help="compute a chart from birth data")
    c.add_argument("--utc", required=True, help="ISO datetime in UTC, e.g. 2001-03-12T01:15:00")
    c.add_argument("--lat", type=float, required=True)
    c.add_argument("--lon", type=float, required=True)
    c.add_argument("--ayanamsa", default="lahiri")
    c.add_argument("--accuracy", default="exact", choices=["exact", "within_15", "approximate", "unknown"])
    c.add_argument("--json", action="store_true")
    rd = sub.add_parser("read", help="birth data and a question -> reading JSON and a Markdown page")
    _birth_flags(rd)
    rd.add_argument("--question", required=True)
    rd.add_argument("--depth", default="curious", choices=["curious", "learner", "astrologer", "full"],
                    help="curious (default): a plain-language paragraph per area above the claims; "
                         "learner and astrologer: the claims and learner panels; full: the whole chart to the "
                         "writer, every field citable as [fact:<path>]")
    from .narrate import EFFORTS, WRITER_MODELS
    rd.add_argument("--writer-model", choices=WRITER_MODELS,
                    help="the writer's model (default narrate.CONFIG.model); the checker's never changes")
    rd.add_argument("--writer-effort", choices=EFFORTS,
                    help="the writer's effort (default: max at depth full, narrate.CONFIG.effort otherwise)")
    rd.add_argument("--as-of", help="date the reading is for, YYYY-MM-DD (default today)")
    rd.add_argument("--out", default="reading", help="output path without extension: writes .json and .md")
    rd.add_argument("--model-fixture", help="replay a recorded narration (tests/fixtures/*.json) instead of "
                                            "calling the model; offline")
    pg = sub.add_parser("page", help="re-render the Markdown page from a reading JSON (no model call)")
    pg.add_argument("--from", dest="from_", required=True, help="reading JSON written by `jyotish read`")
    _birth_flags(pg)
    pg.add_argument("--out", help="Markdown path (default: the JSON path with .md)")
    pg.add_argument("--json-out", help="also write the reading JSON with the engine-derived fields a reading "
                                       "written before them lacks (learner blocks, timing line)")
    ex = sub.add_parser("export-reviews", help="the review step's judgements as preference files "
                                                "(data/preferences/; judgements, not outcomes)")
    ex.add_argument("--database", help="database URL (default JYOTISH_DATABASE_URL, else sqlite:///jyotish.db)")
    ex.add_argument("--out", default="data/preferences")
    ex.add_argument("--with-birth-data", action="store_true", help="include each chart's birth data (left out by default)")
    oc = sub.add_parser("outcomes", help="outcome capture: consents, the clerk's intake sheet, testability")
    osub = oc.add_subparsers(dest="ocmd", required=True)
    oi = osub.add_parser("import", help="the clerk's sheet (docs/intake_template.csv): one row per event")
    oi.add_argument("csv")
    oi.add_argument("--entered-by", required=True, help="the clerk's name or id")
    oca = osub.add_parser("consent", help="record a consent")
    oca.add_argument("consent_id")
    oca.add_argument("--subject", required=True)
    oca.add_argument("--form", required=True, help="consent form version")
    oca.add_argument("--track", required=True, choices=["backlog", "new"])
    oca.add_argument("--by", required=True, help="who recorded it")
    ow = osub.add_parser("withdraw", help="withdraw a consent")
    ow.add_argument("consent_id")
    osub.add_parser("status", help="which rules are testable against measured outcomes")
    for x in (oi, oca, ow):
        x.add_argument("--database", help="database URL (default JYOTISH_DATABASE_URL, else sqlite:///jyotish.db)")
    sj = sub.add_parser("subject", help="a subject's data")
    ssub = sj.add_subparsers(dest="scmd", required=True)
    se = ssub.add_parser("erase", help="erase a subject's chart, readings, reviews and events (DPDP right of erasure)")
    se.add_argument("subject_id")
    se.add_argument("--by", required=True, help="who carried out the request")
    se.add_argument("--database")
    r = sub.add_parser("recover", help="find the UTC instant matching printed Sun/Moon (and slow planets)")
    r.add_argument("--sun", type=float, required=True, help="sidereal longitude 0-360")
    r.add_argument("--moon", type=float, required=True)
    r.add_argument("--jupiter", type=float)
    r.add_argument("--saturn", type=float)
    r.add_argument("--rahu", type=float)
    r.add_argument("--from-year", type=int, default=1940)
    r.add_argument("--to-year", type=int, default=2030)
    args = ap.parse_args(argv)

    if args.cmd == "read":
        raise SystemExit(cmd_read(args))
    if args.cmd in ("outcomes", "subject"):
        raise SystemExit(cmd_outcomes(args))
    if args.cmd == "export-reviews":
        import os
        from .export import export_reviews
        url = args.database or os.environ.get("JYOTISH_DATABASE_URL", "sqlite:///jyotish.db")
        n = export_reviews(url, args.out, with_birth_data=args.with_birth_data)
        print(f"{n['rewrites']} accepted rewrites, {n['judgements']} judgement rows -> {args.out} "
              f"(judgements, not outcomes{'; with birth data' if args.with_birth_data else '; no birth data'})")
        raise SystemExit(0)
    if args.cmd == "page":
        raise SystemExit(cmd_page(args))
    if args.cmd == "reference":
        from .reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
        from .uncertainty import assess
        chart = analyse(REFERENCE_POSITIONS, REFERENCE_ASC, speeds=REFERENCE_SPEEDS,
                        **reference_time_inputs())
        assessed = assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)
        # The positions, features and fires are the app's printed chart (10:10:00); the Life areas,
        # stability and timing are the true-time chart's (10:10:25), the worked example's engine result.
        print_chart(chart, scored_from=assessed)
        print("\n(The Life areas above, and the stability and timing below, are computed from the birth data at the "
              "true time, 10:10:25 IST; the positions, features and fires are the app's printed chart at 10:10:00.)")
        print_stability(assessed)
        from .models import TimingQuery
        print_timing(assessed, TimingQuery(area="career", start="2026-01-01", end="2036-01-01",
                                           question="When is career most activated?"))
    elif args.cmd == "compute":
        chart = compute(datetime.fromisoformat(args.utc), args.lat, args.lon,
                        ayanamsa=args.ayanamsa, time_accuracy=args.accuracy)
        if args.json:
            print(json.dumps(chart.model_dump(), indent=1, default=str))
        else:
            print_chart(chart)
    elif args.cmd == "recover":
        targets = {"Sun": args.sun, "Moon": args.moon}
        for k in ("jupiter", "saturn", "rahu"):
            if getattr(args, k) is not None:
                targets[k.capitalize()] = getattr(args, k)
        import swisseph as swe
        for jd in recover_instant(targets, args.from_year, args.to_year):
            y, m, d, h = swe.revjul(jd, swe.GREG_CAL)
            total = int(round(h * 3600))
            hh, mm, ss = total // 3600, (total % 3600) // 60, total % 60
            print(f"jd {jd:.5f} = {y:04d}-{m:02d}-{d:02d} {hh:02d}:{mm:02d}:{ss:02d} UTC")


if __name__ == "__main__":
    main()
