"""The place list behind the birth form (data/places.tsv.gz, built by scripts/make_places.py
from GeoNames cities15000: every place of 15,000 people or more, with its state, country,
coordinates and IANA timezone). Place data © GeoNames (geonames.org), CC BY 4.0.

`search("rewari")` returns the best matches, largest first after exact names: a name, ASCII
name or alternate name ("Bombay", "Calcutta") that starts with the query, accents ignored; a
query "name, state" or "name, country" narrows by the part after the comma."""

from __future__ import annotations

import csv
import gzip
import io
import unicodedata
from functools import lru_cache
from pathlib import Path

PLACES_FILE = Path(__file__).with_name("data") / "places.tsv.gz"
ATTRIBUTION = "Place names and coordinates: GeoNames (geonames.org), CC BY 4.0"


def fold(s: str) -> str:
    """Lowercase without accents: "Rewāri" -> "rewari"."""
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c)).casefold().strip()


@lru_cache(maxsize=1)
def places() -> list[dict]:
    text = gzip.decompress(PLACES_FILE.read_bytes()).decode("utf-8")
    out = []
    for r in csv.DictReader(io.StringIO(text), delimiter="\t"):
        names = {fold(r["name"]), fold(r["ascii"])} | {fold(a) for a in r["alt"].split("|") if a}
        out.append({"id": int(r["id"]), "name": r["name"], "admin1": r["admin1"], "country_code": r["cc"],
                    "country": r["country"], "lat": float(r["lat"]), "lon": float(r["lon"]), "timezone": r["tz"],
                    "population": int(r["population"]), "_names": names,
                    "_where": fold(f"{r['admin1']} {r['country']} {r['cc']}")})
    return out


def label(p: dict) -> str:
    return ", ".join(x for x in (p["name"], p["admin1"], p["country"]) if x)


def search(query: str, limit: int = 10) -> list[dict]:
    head, _, where = query.partition(",")
    q, w = fold(head), fold(where)
    if len(q) < 2:
        return []
    exact, starts = [], []
    for p in places():                                  # already largest first
        if w and w not in p["_where"]:
            continue
        if q in p["_names"]:
            exact.append(p)
        elif any(n.startswith(q) for n in p["_names"]):
            starts.append(p)
        if len(exact) >= limit:
            break
    found = (exact + starts)[:limit]
    return [{k: v for k, v in p.items() if not k.startswith("_")} | {"label": label(p)} for p in found]
