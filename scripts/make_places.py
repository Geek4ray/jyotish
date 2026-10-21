"""Build src/jyotish/data/places.tsv.gz, the place list behind the birth form's Place field.

Source: GeoNames (https://www.geonames.org), the dump at https://download.geonames.org/export/dump/:
cities15000.zip (every place with a population of 15,000 or more), countryInfo.txt and
admin1CodesASCII.txt. Licence: Creative Commons Attribution 4.0 (CC BY 4.0); the website's
footer carries the attribution. GeoNames' coordinates are the town's, not a hospital's or a
street's: the form shows them and lets the person correct them.

Run, with the three files downloaded into a directory of their own:
    .venv/bin/python -I scripts/make_places.py <download dir>
Columns: geonameid, name, ascii name, state (admin1), country code, country, latitude,
longitude, timezone (IANA), population, a few ASCII alternate names (for "Bombay",
"Calcutta"), sorted by population, largest first."""

from __future__ import annotations

import csv
import gzip
import io
import re
import sys
import zipfile
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "src" / "jyotish" / "data" / "places.tsv.gz"
ASCII_NAME = re.compile(r"^[A-Za-z][A-Za-z .'\-]{1,40}$")
COLUMNS = ["id", "name", "ascii", "admin1", "cc", "country", "lat", "lon", "tz", "population", "alt"]


def main(src: str) -> None:
    d = Path(src)
    countries = {}
    for line in (d / "countryInfo.txt").read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#"):
            f = line.split("\t")
            countries[f[0]] = f[4]
    admin1 = {}
    for line in (d / "admin1CodesASCII.txt").read_text(encoding="utf-8").splitlines():
        f = line.split("\t")
        if len(f) >= 2:
            admin1[f[0]] = f[1]
    with zipfile.ZipFile(d / "cities15000.zip") as z:
        text = z.read("cities15000.txt").decode("utf-8")
    rows = []
    for line in text.splitlines():
        f = line.split("\t")
        if len(f) < 19:
            continue
        gid, name, ascii_name, alts, lat, lon, cc, a1, pop, tz = f[0], f[1], f[2], f[3], f[4], f[5], f[8], f[10], f[14], f[17]
        if not tz:
            continue
        alt = []
        for a in alts.split(","):
            if ASCII_NAME.match(a) and a.lower() not in (name.lower(), ascii_name.lower()) and a not in alt:
                alt.append(a)
        rows.append([gid, name, ascii_name, admin1.get(f"{cc}.{a1}", ""), cc, countries.get(cc, cc),
                     f"{float(lat):.4f}", f"{float(lon):.4f}", tz, pop or "0", "|".join(alt[:8])])
    rows.sort(key=lambda r: -int(r[9]))
    buf = io.StringIO()
    w = csv.writer(buf, delimiter="\t", lineterminator="\n")
    w.writerow(COLUMNS)
    w.writerows(rows)
    OUT.write_bytes(gzip.compress(buf.getvalue().encode("utf-8"), mtime=0))
    print(f"{len(rows)} places -> {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main(sys.argv[1])
