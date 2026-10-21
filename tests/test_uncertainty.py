"""Layer 1b sampler on the reference birth data (true time 10:10:25 IST, ±2 minutes)."""

import time

import pytest

from jyotish.cli import print_stability
from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
from jyotish.uncertainty import assess, label


@pytest.fixture(scope="module")
def run():
    t = time.perf_counter()
    chart = assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)
    return chart, time.perf_counter() - t


def fire(chart, rule_id, basis="lagna"):
    return next(f for f in chart.fired_rules if f.id == rule_id and f.basis == basis)


def test_full_run_under_ten_seconds(run):
    chart, seconds = run
    assert seconds < 10.0 and chart.uncertainty.seconds < 10.0
    assert chart.uncertainty.samples == 200 and chart.birth.time_posterior.samples == 200
    assert chart.uncertainty.half_width_min == 2.0 and chart.uncertainty.shape == "uniform"


def test_every_fire_has_three_numbers(run):
    chart, _ = run
    for f in chart.fired_rules:
        s = f.stability
        assert s is not None and all(0.0 <= x <= 1.0 for x in (s.time, s.ayanamsa, s.house))
        assert s.label == label(s.time)


def test_ruchaka_is_stable(run):
    s = fire(run[0], "yoga.ruchaka").stability
    assert s.time == pytest.approx(1.0, abs=0.01)
    assert s.ayanamsa == 1.0 and s.house == 1.0 and s.label == "stable"


def test_raja_yoga_is_house_sensitive(run):
    # Holds in every time sample and under every ayanamsa, but not under Sripati: the axes
    # are reported apart, never pooled.
    s = fire(run[0], "yoga.kendra_trikona_raja").stability
    assert (s.time, s.ayanamsa, s.house) == (1.0, 1.0, 0.5)


def test_lagna_varga_stability(run):
    u = run[0].uncertainty
    assert u.varga_stability["D1"] == 1.0
    assert 0.6 < u.varga_stability["D9"] < 0.95     # D9 edge 22.5' ahead, ~1.4 min of clock
    assert u.varga_stability["D60"] < 0.7           # D60 cells 30' wide, ~1.8 min
    assert u.placements["D9"]["Asc"].time == u.varga_stability["D9"]
    assert u.placements["D1"]["Moon"].time == 1.0   # the Moon does not leave Libra in 4 minutes


def test_dasha_boundary_in_days(run):
    u = run[0].uncertainty
    rahu = next(b for b in u.boundaries if b.system == "vimshottari" and b.lords == ["Rahu"])
    # ±2 min moves the Moon ±0.018°, the Mars balance by about ±3.6 days.
    assert 4.0 < rahu.time_range_days < 10.0 and 1.0 < rahu.time_sd_days < 4.0
    assert rahu.time_share == 1.0
    # Raman and KP move the Moon by over a degree against Lahiri: months, not days.
    assert rahu.ayanamsa_range_days > 100
    assert rahu.house_range_days == 0.0              # Vimshottari does not read houses
    # Chara starts at birth with no balance, so its boundaries move only with the clock:
    # at most the 4-minute width of the window.
    chara = next(b for b in u.boundaries if b.system == "chara" and b.lords == ["Aries"])
    assert 0 < chara.time_range_days <= 4 / 1440 + 1e-6


def test_deterministic(run):
    again = assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)
    assert again.uncertainty.varga_stability == run[0].uncertainty.varga_stability


def test_summary_prints(run, capsys):
    print_stability(run[0])
    out = capsys.readouterr().out
    assert "yoga.ruchaka" in out and "1.00 / 1.00 / 1.00" in out
    assert "days" in out and "D60 0.4" in out
