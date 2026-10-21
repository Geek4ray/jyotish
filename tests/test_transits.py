"""Transits on the reference chart, 2001-2040 (Lahiri, mean node, as the chart)."""

import pytest
import swisseph as swe

from jyotish.chart import analyse
from jyotish.cli import print_current_transits
from jyotish.constants import GOCHARA_VEDHA, MURTHI, SIGNS
from jyotish.dignity import house_of
from jyotish.reference import (
    REFERENCE_ASC, REFERENCE_POSITIONS, REFERENCE_SPEEDS, reference_time_inputs,
)
from jyotish.transits import MINUTE, TRANSIT_BODIES, Sky, transit_timeline

START, END = swe.julday(2001, 1, 1, 0.0), swe.julday(2041, 1, 1, 0.0)


@pytest.fixture(scope="module")
def chart():
    return analyse(REFERENCE_POSITIONS, REFERENCE_ASC, speeds=REFERENCE_SPEEDS,
                   **reference_time_inputs())


@pytest.fixture(scope="module")
def tl(chart):
    return transit_timeline(chart, START, END)


@pytest.fixture(scope="module")
def sky():
    return Sky("lahiri", true_node=False)


def jd(y, m, d):
    return swe.julday(y, m, d, 0.0)


def rows(tl, body):
    return [r for r in tl.rows if r.body == body]


def test_rows_tile_the_range(tl):
    for body in TRANSIT_BODIES:
        rs = rows(tl, body)
        assert rs[0].start_jd == START and rs[0].clipped_start and rs[0].entered is None
        assert rs[-1].end_jd == END and rs[-1].clipped_end
        assert all(a.end_jd == b.start_jd for a, b in zip(rs, rs[1:])), body
        assert all(a.sign != b.sign for a, b in zip(rs, rs[1:])), body


def test_ingresses_exact_to_the_minute(tl, sky):
    for body in TRANSIT_BODIES:
        for a, b in zip(rows(tl, body), rows(tl, body)[1:]):
            t = b.start_jd
            assert int(sky.lon(body, t - MINUTE) // 30) == a.sign, (body, t)
            assert int(sky.lon(body, t + MINUTE) // 30) == b.sign, (body, t)


# Saturn's sidereal (Lahiri) ingresses as published in Indian ephemerides, IST date; the
# engine's UT instants must fall within a day.
SATURN_INGRESSES = [
    ("Virgo", (2009, 9, 9)), ("Libra", (2011, 11, 15)), ("Virgo", (2012, 5, 16)),
    ("Libra", (2012, 8, 4)), ("Scorpio", (2014, 11, 2)), ("Sagittarius", (2017, 1, 26)),
    ("Scorpio", (2017, 6, 21)), ("Sagittarius", (2017, 10, 26)), ("Capricorn", (2020, 1, 24)),
    ("Aquarius", (2022, 4, 29)), ("Capricorn", (2022, 7, 12)), ("Aquarius", (2023, 1, 17)),
    ("Pisces", (2025, 3, 29)),
]


@pytest.mark.parametrize("sign,date", SATURN_INGRESSES)
def test_saturn_ingresses(tl, sign, date):
    r = next(r for r in rows(tl, "Saturn") if r.sign_name == sign and abs(r.start_jd - jd(*date)) < 2)
    assert abs(r.start_jd - jd(*date)) <= 1.0


def test_retrograde_reentries_are_separate_rows(tl):
    sc = [r for r in rows(tl, "Saturn") if r.sign_name == "Scorpio"]
    assert [r.entered for r in sc] == ["direct", "retrograde"]          # 2014 and June 2017
    assert all(r.entered == "retrograde" for r in rows(tl, "Rahu")[1:])  # mean node


def test_houses_bav_sav(tl, chart):
    lib = next(r for r in rows(tl, "Saturn") if r.sign_name == "Libra")
    assert lib.houses == {"lagna": 6, "moon": 1, "sun": 9}
    av = chart.features.ashtakavarga
    for r in tl.rows:
        assert r.sav == av.SAV[r.sign]
        if r.body in ("Rahu", "Ketu"):
            assert r.bav is None and r.grade is None
        else:
            assert r.bav == av.BAV[r.body][r.sign]
    assert lib.bav == 5 and lib.grade == "favourable"      # Phaladeepika 23.11: 5-8
    sc = next(r for r in rows(tl, "Saturn") if r.sign_name == "Scorpio")
    assert sc.bav == 2 and sc.grade == "adverse"


def test_kakshya_spans(tl, sky):
    for r in tl.rows:
        assert r.kakshya[0].start_jd == r.start_jd and r.kakshya[-1].end_jd == r.end_jd
        assert all(a.end_jd == b.start_jd for a, b in zip(r.kakshya, r.kakshya[1:]))
        for k in r.kakshya:
            mid = (k.start_jd + k.end_jd) / 2
            lon = sky.lon(r.body, mid)
            from jyotish.constants import KAKSHYA_LORDS
            assert KAKSHYA_LORDS[int(lon * 96 / 360) % 8] == k.lord
            assert (k.bindu is None) == (r.body in ("Rahu", "Ketu"))


def test_vedha_and_vipareeta(tl, sky, chart):
    moon = chart.bodies["Moon"].sign
    for r in tl.rows:
        table = GOCHARA_VEDHA[r.body]
        h = r.houses["moon"]
        assert r.gochara_good == (h in table)
        if not r.gochara_good:
            assert r.vedha == []
        if h not in table.values():
            assert r.vipareeta_vedha == []
        for v in r.vedha:
            assert r.start_jd <= v.start_jd < v.end_jd <= r.end_jd
            mid = (v.start_jd + v.end_jd) / 2
            assert house_of(int(sky.lon(v.by, mid) // 30), moon) == table[h]
            assert {r.body, v.by} not in ({"Sun", "Saturn"}, {"Rahu", "Ketu"})
    leo = next(r for r in rows(tl, "Saturn") if r.sign_name == "Leo" and r.entered == "direct"
               and r.end_jd - r.start_jd > 365)
    assert leo.vedha and "Sun" not in {v.by for v in leo.vedha}   # 11th; Sun cannot obstruct Saturn


def test_murthi(tl, sky, chart):
    moon = chart.bodies["Moon"].sign
    for r in tl.rows:
        if r.body in ("Saturn", "Jupiter", "Rahu", "Ketu") and r.entered:
            assert r.murthi == MURTHI[house_of(int(sky.lon("Moon", r.start_jd) // 30), moon)]
        else:
            assert r.murthi is None


def windows(tl, kind):
    return [w for w in tl.windows if w.kind == kind]


def test_sade_sati(tl):
    ss = windows(tl, "sade_sati")
    # Libra Moon: Saturn in Virgo from 2009-09-09, out of Scorpio 2017-01-26; back into
    # Scorpio 2017-06-21 to 2017-10-26; into Virgo again 2038.
    assert abs(ss[0].start_jd - jd(2009, 9, 9)) <= 1 and abs(ss[0].end_jd - jd(2017, 1, 26)) <= 1
    assert [p["phase"] for p in ss[0].details["phases"]] == ["rising", "peak", "rising", "peak", "setting"]
    assert [p["grade"] for p in ss[0].details["phases"]][-1] == "adverse"   # Saturn BAV 2 in Scorpio
    assert abs(ss[1].start_jd - jd(2017, 6, 21)) <= 1
    assert ss[1].details["phases"][0]["phase"] == "setting"
    assert ss[2].start_jd > jd(2038, 1, 1)


def test_kantaka_and_ashtama(tl):
    k = windows(tl, "kantaka_shani")
    assert {w.details["sign"] for w in k} == {"Cancer", "Capricorn", "Aries"}   # 10th, 4th, 7th
    a = windows(tl, "ashtama_shani")
    assert {w.details["sign"] for w in a} == {"Taurus"}
    assert a[0].start_jd == START            # Saturn in Taurus, 8th from the Moon, at birth


def test_jupiter_windows(tl):
    j = windows(tl, "jupiter_1_5_9_11")
    assert j and {w.tags[1] for w in j} <= {"house_moon:1", "house_moon:5", "house_moon:9", "house_moon:11"}
    assert {w.details["sign"] for w in j} == {"Libra", "Aquarius", "Gemini", "Leo"}


def test_returns(tl, chart, sky):
    birth = chart.meta.jd
    nodal = windows(tl, "nodal_return")
    exact_n = [t for w in nodal for t in w.details["exact_jd"]]
    assert all(t > birth + 9 * 365 for t in exact_n)
    assert len(exact_n) == 2                                   # ~2019 and ~2038 (mean node)
    assert abs((exact_n[1] - exact_n[0]) / 365.25 - 18.6) < 0.1
    sat = windows(tl, "saturn_return")
    exact_s = [t for w in sat for t in w.details["exact_jd"]]
    assert exact_s and all(jd(2029, 1, 1) < t < jd(2032, 1, 1) for t in exact_s)
    for t in exact_n + exact_s:
        body = "Rahu" if t in exact_n else "Saturn"
        assert abs((sky.lon(body, t) - chart.bodies[body].lon + 180) % 360 - 180) < 0.01


def test_current_windows_print(chart, capsys):
    print_current_transits(chart, now_jd=jd(2012, 1, 1))
    out = capsys.readouterr().out
    assert "Saturn   Libra" in out
    assert "sade_sati" in out and "jupiter_1_5_9_11" not in out.split("Windows now:")[0]
