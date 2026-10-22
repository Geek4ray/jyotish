"""The chart display (SPEC Layer 6b item 2): the engine's SVG and tables against the chart object."""

import json
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from jyotish.chart import compute
from jyotish.constants import SIGNS
from jyotish.dasha import vimshottari
from jyotish.display import DISPLAY_VARGAS, PLANETS, SEVEN, dms, placements, svg, tables
from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON

NS = {"s": "http://www.w3.org/2000/svg"}
AS_OF = date(2026, 10, 21)


@pytest.fixture(scope="module")
def chart():
    return compute(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)


@pytest.fixture(scope="module")
def drawing(chart):
    return ET.fromstring(svg(chart))


def test_every_planet_is_drawn_in_its_sign_in_d1_d9_d10(chart, drawing):
    for varga in DISPLAY_VARGAS:
        g = drawing.find(f".//s:g[@data-varga='{varga}']", NS)
        place = placements(chart, varga)
        lagna = place["Asc"]
        drawn = {t.get("data-planet"): t for t in g.iterfind(".//s:text[@data-planet]", NS)}
        assert set(drawn) == set(PLANETS) | {"Asc"}, varga                      # all nine and the ascendant
        for p, t in drawn.items():
            sign = int(t.get("data-sign"))
            assert sign == place[p], (varga, p)
            assert int(t.get("data-house")) == (sign - lagna) % 12 + 1, (varga, p)
        # Each planet sits inside the house group that carries its sign, and that house shows the
        # sign's number; house 1 holds the lagna.
        for house in g.iterfind("s:g[@data-house]", NS):
            sign = int(house.get("data-sign"))
            assert house.find("s:text", NS).text == str(sign + 1)
            for t in house.iterfind("s:text[@data-planet]", NS):
                assert int(t.get("data-sign")) == sign
        first = g.find("s:g[@data-house='1']", NS)
        assert int(first.get("data-sign")) == lagna
        assert first.find("s:text[@data-planet='Asc']", NS) is not None


def test_reference_chart_drawing(chart, drawing):
    d1 = drawing.find(".//s:g[@data-varga='D1']", NS)
    house = {t.get("data-planet"): int(t.get("data-house")) for t in d1.iterfind(".//s:text[@data-planet]", NS)}
    assert house == {"Asc": 1, "Jupiter": 1, "Saturn": 1, "Rahu": 2, "Moon": 6, "Mars": 7, "Ketu": 8,
                     "Sun": 10, "Mercury": 10, "Venus": 11}
    venus = d1.find(".//s:text[@data-planet='Venus']", NS)
    assert venus.text == "Ve 23° R" and venus.get("fill") == "#5ED1B6"          # exalted, retrograde
    assert drawing.find("s:title", NS).text.endswith("Taurus lagna")


def test_planet_table_matches_the_chart(chart):
    t = tables(chart, AS_OF)
    rows = {r["planet"]: r for r in t["planets"]}
    assert rows["Ascendant"]["sign"] == SIGNS[chart.lagnas.asc_sign] and rows["Ascendant"]["degree"] == "6°17′31″"
    for p in PLANETS:
        b, r = chart.bodies[p], rows[p]
        assert (r["sign"], r["nakshatra"], r["pada"], r["dignity"], r["retrograde"], r["combust"], r["avastha"]) == \
            (b.sign_name, b.nak_name, b.pada, b.dignity, b.retro, b.combust, b.avastha_baladi), p
        assert r["degree"] == dms(b.deg)
    assert rows["Sun"]["degree"] == "27°47′56″" and rows["Moon"]["nakshatra"] == "Chitra"


def test_strength_tables_match_the_chart(chart):
    t = tables(chart, AS_OF)
    sb = {r["planet"]: r for r in t["shadbala"]["rows"]}
    assert set(sb) == set(SEVEN)
    for p in SEVEN:
        x = chart.features.shadbala.planets[p]
        assert sb[p]["total"] == round(x.total / 60, 2) and sb[p]["required"] == round(x.required / 60, 2)
        assert sb[p]["ratio"] == round(x.ratio, 2)
        assert abs(sum(sb[p][k] for k in ("sthana", "dig", "kala", "chesta", "naisargika", "drik")) - sb[p]["total"]) < 0.05
    assert sb["Venus"]["ratio"] == 1.33 and sb["Saturn"]["ratio"] == 0.69
    av = chart.features.ashtakavarga
    assert t["ashtakavarga"]["sav"] == list(av.SAV) and sum(t["ashtakavarga"]["sav"]) == 337
    assert all(t["ashtakavarga"]["bav"][p] == list(av.BAV[p]) for p in SEVEN)
    bb = {r["house"]: r for r in t["bhava_bala"]["rows"]}
    for h in range(1, 13):
        assert bb[h]["rupas"] == round(chart.features.bhava_bala.whole_sign[h].rupas, 2)
        assert bb[h]["sign"] == SIGNS[(chart.lagnas.asc_sign + h - 1) % 12]
    assert bb[10] == {"house": 10, "sign": "Aquarius", "lord": "Saturn", "rupas": 4.51}


def test_vimshottari_to_the_pratyantar_with_the_current_period(chart):
    v = tables(chart, AS_OF)["vimshottari"]
    assert v["current"] == ["Jupiter", "Mercury", "Mercury"]                     # Jupiter-Mercury, as the reading says
    mahas = v["mahas"]
    stored = [p for p in chart.dashas["vimshottari"] if len(p.lords) == 1]
    assert [m["lords"][0] for m in mahas] == [p.lords[0] for p in stored]
    full = vimshottari(chart.bodies["Moon"].lon, chart.meta.jd, levels=3, year_length=chart.meta.dasha_year)
    assert sum(len(a["pratyantars"]) for m in mahas for a in m["antars"]) == sum(1 for p in full if p.level == 3)
    assert all(len(a["pratyantars"]) == 9 for m in mahas[1:] for a in m["antars"])
    assert [m["lords"] for m in mahas if m["current"]] == [["Jupiter"]]
    jup = next(m for m in mahas if m["current"])
    cur = next(a for a in jup["antars"] if a["current"])
    assert cur["lords"] == ["Jupiter", "Mercury"] and sum(x["current"] for x in cur["pratyantars"]) == 1
    assert mahas[0]["start"] == "2001-03-12" and mahas[0]["start_true"] < mahas[0]["start"]   # the birth balance


def test_api_serves_the_svg_and_tables(tmp_path):
    from jyotish.api import create_app
    fixture = str(Path(__file__).parent / "fixtures" / "narration_career_edited.json")
    app = create_app(f"sqlite:///{tmp_path / 'd.db'}", model_fixture=fixture)
    body = {"date": "2001-03-12", "time": "10:10:25", "tz": "Asia/Kolkata", "lat": REFERENCE_LAT, "lon": REFERENCE_LON,
            "node": "mean", "question": "How will my career go?", "depth": "astrologer"}
    with TestClient(app) as c:
        rid = c.post("/readings", json=body).json()["id"]
        import time
        for _ in range(400):
            s = c.get(f"/readings/{rid}").json()
            if s["status"] in ("done", "failed"):
                break
            time.sleep(0.05)
        cid = s["chart_id"]
        r = c.get(f"/charts/{cid}/chart.svg")
        assert r.status_code == 200 and r.headers["content-type"].startswith("image/svg+xml")
        assert ET.fromstring(r.text).find(".//s:g[@data-varga='D10']", NS) is not None
        t = c.get(f"/charts/{cid}/tables.json", params={"as_of": "2026-10-21"}).json()
        assert t["vimshottari"]["current"] == ["Jupiter", "Mercury", "Mercury"] and len(t["planets"]) == 10
        assert c.get("/charts/nope/chart.svg").status_code == 404
        assert c.get(f"/charts/{cid}/tables.json", params={"as_of": "tomorrow"}).status_code == 422
