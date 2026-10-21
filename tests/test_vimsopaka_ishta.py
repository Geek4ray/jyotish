"""Vimsopaka (BPHS 7.17-25) and Ishta/Kashta (BPHS 28.2-6), Santhanam 1984."""

import random

import pytest

from jyotish.chart import analyse
from jyotish.constants import GRAHAS, VIMSOPAKA_SCHEMES, vimsopaka_label
from jyotish.reference import (
    REFERENCE_ASC, REFERENCE_POSITIONS, REFERENCE_SPEEDS, reference_time_inputs,
)
from jyotish.vimsopaka import vimsopaka


@pytest.fixture(scope="module")
def inputs():
    return reference_time_inputs()


def chart(inputs, **meta):
    kw = dict(inputs)
    kw["meta"] = kw["meta"].model_copy(update=meta)
    return analyse(REFERENCE_POSITIONS, REFERENCE_ASC, speeds=REFERENCE_SPEEDS, **kw)


@pytest.fixture(scope="module")
def ref(inputs):
    return chart(inputs)


def test_scheme_weights_sum_to_twenty():
    for scheme, w in VIMSOPAKA_SCHEMES.items():
        assert sum(w.values()) == 20, scheme
    assert len(VIMSOPAKA_SCHEMES["shodasavarga"]) == 16 and len(VIMSOPAKA_SCHEMES["dasavarga"]) == 10


def test_vimsopaka_range_on_random_charts():
    rng = random.Random(5)
    for _ in range(200):
        v = vimsopaka({g: rng.uniform(0, 360) for g in GRAHAS})
        assert all(5.0 <= x <= 20.0 for row in v.values() for x in row.values())


def test_saturn_shadvarga_by_hand(ref):
    # Saturn at 2°06' Taurus: D1 Taurus 18 (Venus, extreme friend), D2 Cancer 5 (Moon,
    # sworn enemy), D3 Taurus 18, D9 Capricorn 20 (own), D12 Taurus 18, D30 Taurus 18.
    # (6x18 + 2x5 + 4x18 + 5x20 + 2x18 + 1x18) / 20 = 17.2
    assert ref.features.vimsopaka["Saturn"]["shadvarga"] == pytest.approx(17.2)
    assert vimsopaka_label(17.2) == "full"


def test_own_sign_scores_twenty():
    # Either of a planet's own signs scores the full 20, whatever the temporal relation.
    from jyotish.vimsopaka import varga_viswa
    assert varga_viswa("Mars", 0, {"Mars": 0}) == 20 and varga_viswa("Mars", 7, {"Mars": 0}) == 20


def test_ishta_kashta_bphs_by_hand(ref):
    ik = ref.features.ishta_kashta
    sb = ref.features.shadbala.planets
    # Venus: Uchcha bala 58.89 and Cheshta 52.11 (kendra method), so Ishta is their mean.
    assert ik["Venus"].ishta == pytest.approx((sb["Venus"].sthana.uchcha + sb["Venus"].chesta) / 2)
    assert ik["Venus"].ishta == pytest.approx(55.5, abs=0.01)
    for p, x in ik.items():
        assert x.ishta + x.kashta == pytest.approx(60.0)
        assert 1.0 <= x.uchcha_rasmi <= 7.0 and 1.0 <= x.cheshta_rasmi <= 7.0
    # The Moon's Cheshta kendra is Moon - Sun (213.6° folded to 146.4°), not its Paksha bala.
    assert ik["Moon"].cheshta_rasmi == pytest.approx(1 + 146.38 / 30, abs=0.01)


def test_ishta_kashta_raman_setting(inputs):
    ik = chart(inputs, ishta_kashta="raman").features.ishta_kashta
    v = ik["Venus"]
    assert v.ishta == pytest.approx((58.89 * 52.11) ** 0.5, abs=0.05)
    assert v.uchcha_rasmi is None


def test_ishta_absent_without_shadbala():
    c = analyse(REFERENCE_POSITIONS, REFERENCE_ASC)
    assert c.features.ishta_kashta is None and c.features.vimsopaka["Saturn"]["shadvarga"] == pytest.approx(17.2)
