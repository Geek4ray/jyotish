"""Sripati bhavas (houses.py) and their effect on the reference chart."""

import pytest

from jyotish.chart import compute
from jyotish.houses import bhava_lordships, bhava_of, sripati_madhyas, sripati_sandhis
from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON


def test_madhyas_trisect_the_quadrants():
    m = sripati_madhyas(asc=10.0, mc=280.0)          # IC 100, descendant 190
    assert m[0] == 10.0 and m[3] == 100.0 and m[6] == 190.0 and m[9] == 280.0
    assert m[1] == pytest.approx(40.0) and m[2] == pytest.approx(70.0)
    assert m[10] == pytest.approx(310.0) and m[11] == pytest.approx(340.0)


def test_sandhis_are_midpoints_and_houses_tile():
    m = sripati_madhyas(asc=10.0, mc=280.0)
    s = sripati_sandhis(m)
    assert s[0] == pytest.approx(25.0) and s[11] == pytest.approx(355.0)
    for h, madhya in enumerate(m, start=1):
        assert bhava_of(madhya, m) == h
    assert bhava_of(24.9, m) == 1 and bhava_of(25.1, m) == 2 and bhava_of(354.9, m) == 12
    assert bhava_of(355.1, m) == 1                    # house 1 wraps through 0°


def test_unequal_quadrants():
    m = sripati_madhyas(asc=36.29, mc=290.28)         # the reference chart
    assert m[1] - m[0] == pytest.approx((110.28 - 36.29) / 3, abs=1e-9)
    assert (m[10] - m[9]) == pytest.approx((36.29 + 360 - 290.28) / 3, abs=1e-9)


@pytest.fixture(scope="module")
def charts():
    kw = dict(true_node=False)
    return (compute(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, **kw),
            compute(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, house_system="sripati", **kw))


def test_reference_bhavas(charts):
    whole, srip = charts
    assert srip.meta.house_system == "sripati" and len(srip.lagnas.bhava_madhya_sripati) == 12
    moved = {n: (whole.bodies[n].house, srip.bodies[n].house) for n in whole.bodies
             if whole.bodies[n].house != srip.bodies[n].house}
    assert moved == {"Sun": (10, 11), "Venus": (11, 12), "Rahu": (2, 3), "Ketu": (8, 9)}


def test_reference_bhava_lordships(charts):
    _, srip = charts
    # Madhyas in Taurus, Gemini, Gemini, Cancer, Leo, Libra, Scorpio, Sagittarius,
    # Sagittarius, Capricorn, Aquarius, Aries: the Sun rules the 5th, Saturn the 10th and
    # 11th, so Saturn is no longer yogakaraka.
    assert srip.features.lordship == bhava_lordships(srip.lagnas.bhava_madhya_sripati)
    assert srip.features.lordship["Sun"] == [5] and srip.features.lordship["Saturn"] == [10, 11]
    assert "yogakaraka" not in srip.features.roles["Saturn"]


def test_rules_read_sripati_from_the_lagna_only(charts):
    whole, srip = charts
    ids = lambda c: {(f.id, f.basis) for f in c.fired_rules}
    assert ("yoga.kendra_trikona_raja", "lagna") in ids(whole)
    assert ("yoga.kendra_trikona_raja", "lagna") not in ids(srip)   # Sun now 5th lord, Mercury 2nd/3rd
    assert ("yoga.ruchaka", "sun") in ids(srip)                       # Sun basis stays whole sign


def test_sripati_needs_the_mc():
    from jyotish.chart import analyse
    from jyotish.models import Meta
    from jyotish.reference import REFERENCE_ASC, REFERENCE_POSITIONS
    with pytest.raises(ValueError, match="needs the MC"):
        analyse(REFERENCE_POSITIONS, REFERENCE_ASC, meta=Meta(house_system="sripati"))
