"""Command line: print the reference chart, compute a chart, recover an instant."""

from __future__ import annotations

import argparse
import json
from datetime import datetime

from .chart import analyse, compute
from .constants import SIGNS
from .ephemeris import recover_instant
from .models import Chart
from .reference import REFERENCE_ASC, REFERENCE_POSITIONS, REFERENCE_SPEEDS


def _fmt_lon(lon: float) -> str:
    sign = int(lon // 30)
    d = lon % 30
    m = (d - int(d)) * 60
    s = (m - int(m)) * 60
    return f"{int(d):02d}°{int(m):02d}'{int(round(s)):02d}\" {SIGNS[sign]}"


def print_chart(chart: Chart) -> None:
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
    if chart.panchanga:
        print("\nPanchanga:", chart.panchanga.model_dump())
    if chart.dashas:
        print("\nVimshottari (maha):")
        for p in chart.dashas["vimshottari"]:
            if len(p.lords) == 1:
                print(f"  {p.lords[0]:8} jd {p.start_jd:.2f} – {p.end_jd:.2f}  ({(p.end_jd - p.start_jd) / 365.25:.1f} y) tara {p.tara}")


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
    r = sub.add_parser("recover", help="find the UTC instant matching printed Sun/Moon (and slow planets)")
    r.add_argument("--sun", type=float, required=True, help="sidereal longitude 0-360")
    r.add_argument("--moon", type=float, required=True)
    r.add_argument("--jupiter", type=float)
    r.add_argument("--saturn", type=float)
    r.add_argument("--rahu", type=float)
    r.add_argument("--from-year", type=int, default=1940)
    r.add_argument("--to-year", type=int, default=2030)
    args = ap.parse_args(argv)

    if args.cmd == "reference":
        chart = analyse(REFERENCE_POSITIONS, REFERENCE_ASC, speeds=REFERENCE_SPEEDS)
        print_chart(chart)
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
