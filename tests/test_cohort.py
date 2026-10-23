"""jyotish.cohort: the chart features a cohort run reads, and SPEC Layer 6 test 4's covariate, the
engine's own windows. The activation years come from the pieces the timing join builds its windows
from (timing.window_pieces), so the two cannot drift apart; the best third of the life by joint is
active, so a third of the person-years are active for everyone (the dasha gate alone covered nine in
ten: review 2026-10-23, F1)."""

import json
from datetime import date, datetime
from pathlib import Path

import pytest
import swisseph as swe

from jyotish.chart import compute
from jyotish.cohort import ACTIVE_SHARE, active_windows, chart_features, slow_spans
from jyotish.models import TimingQuery
from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
from jyotish.timing import answer_v2, slices, slow_spans_of, window_pieces
from jyotish.transits import transit_timeline

BIRTHS = json.loads((Path(__file__).parent / "fixtures" / "births.json").read_text())["births"]
A, B = swe.julday(2026, 1, 1, 0.0), swe.julday(2036, 1, 1, 0.0)
UNTIL = date(2026, 10, 22)


def _birth(b: dict) -> dict:
    utc = datetime.fromisoformat(b["utc"])
    return {"date": utc.date().isoformat(), "time": utc.strftime("%H:%M:%S"), "tz": "UTC", "lat": b["lat"],
            "lon": b["lon"], "node": "mean"}


@pytest.fixture(scope="module")
def chart():
    return compute(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False, dasha_levels=2)


@pytest.fixture(scope="module")
def spans(chart):
    return slow_spans_of(transit_timeline(chart, A, B, taras=False).rows)


def test_the_pieces_are_the_joins_windows(chart, spans):
    # Every window answer_v2 returns is a time-weighted mean of pieces: the pieces made from the
    # same spans give back each window's joint, q and t, the avoid window's too.
    pieces = window_pieces(chart, "career", A, B, spans)
    ans = answer_v2(chart, TimingQuery(area="career", start=date(2026, 1, 1), end=date(2036, 1, 1), top=50),
                    formula="v2.1")
    assert len(ans.windows) > 3
    for w in ans.windows + [ans.avoid]:
        inside = [p for p in pieces if p["a"] >= w.start_jd - 1e-6 and p["b"] <= w.end_jd + 1e-6]
        span = sum(p["b"] - p["a"] for p in inside)
        assert span == pytest.approx(w.end_jd - w.start_jd, abs=1e-6)
        for k, v in (("joint", w.joint), ("q", w.dasha_quality), ("t", w.transit_activation)):
            assert sum(p[k] * (p["b"] - p["a"]) for p in inside) / span == pytest.approx(v, abs=1e-9)
    assert len(pieces) > 20 and all(0 <= p["q"] <= 1 and 0 <= p["t"] <= 1 for p in pieces)
    assert all(p["joint"] == pytest.approx(0.6 * p["q"] + 0.4 * p["t"]) for p in pieces)


def test_slices_cover_the_range_once_and_pieces_do_not_depend_on_the_cut(chart, spans):
    cut = slices(chart, A, B, spans)
    antars = [p for p in chart.dashas["vimshottari"] if len(p.lords) == 2 and p.end_jd > A and p.start_jd < B]
    assert sum(y - x for x, y, _, _ in cut) == pytest.approx(B - A, abs=1e-6)        # the antars tile the range
    assert all(set(signs) == {"Saturn", "Jupiter", "Rahu", "Ketu"} for _, _, _, signs in cut)
    assert {tuple(per.lords) for _, _, per, _ in cut} == {tuple(p.lords) for p in antars}
    assert all(x < y for x, y, _, _ in cut)
    assert window_pieces(chart, "career", A, B, spans, cut=cut) == window_pieces(chart, "career", A, B, spans)
    # v2's share and v2.1's credit are both in [0, 1]; the Rao credit is never higher than the share
    # for the same signs, because its targets are fewer.
    for p21, p2 in zip(window_pieces(chart, "career", A, B, spans, cut=cut),
                       window_pieces(chart, "career", A, B, spans, formula="v2", cut=cut)):
        assert (p21["a"], p21["b"], p21["lords"], p21["q"]) == (p2["a"], p2["b"], p2["lords"], p2["q"])
        assert 0 <= p21["t"] <= 1 and 0 <= p2["t"] <= 1 and p2["transit"] is None


def test_the_sweep_is_once_per_process_and_agrees_with_a_range_sweep(chart):
    sw = slow_spans("lahiri", False, A, B)
    assert sw is slow_spans("lahiri", False, A, B)
    assert sw[0][2] <= swe.julday(1850, 1, 2, 0.0) and sw[-1][3] >= swe.julday(2149, 12, 31, 0.0)
    inside = sorted((b, s, max(t0, A), min(t1, B)) for b, s, t0, t1 in sw if t1 > A and t0 < B)
    own = sorted(slow_spans_of(transit_timeline(chart, A, B, taras=False).rows))
    assert [(b, s) for b, s, _, _ in inside] == [(b, s) for b, s, _, _ in own]
    for (_, _, a1, z1), (_, _, a2, z2) in zip(inside, own):
        assert abs(a1 - a2) < 1.5 / 1440 and abs(z1 - z2) < 1.5 / 1440          # each ingress within a minute
    # A range outside the standard sweep gets a sweep of its own.
    far = slow_spans("lahiri", False, swe.julday(1800, 1, 1, 0.0), swe.julday(1801, 1, 1, 0.0))
    assert far is not sw and far[0][2] == swe.julday(1800, 1, 1, 0.0)


def test_active_windows_take_the_best_third():
    pieces = [{"a": 10.0 * i, "b": 10.0 * (i + 1), "joint": j} for i, j in enumerate([0.2, 0.9, 0.5, 0.8, 0.1, 0.7])]
    active, share = active_windows(pieces, 0.0, 60.0, 0.0)
    # 0.9 (10-20) and 0.8 (30-40) fill the third of 60 days; 0.7 would carry it past.
    assert active == [(10 / 365.25, 20 / 365.25), (30 / 365.25, 40 / 365.25)] and share == pytest.approx(ACTIVE_SHARE)
    # Adjacent pieces merge, and a first piece longer than the budget is still taken.
    act, sh = active_windows([{"a": 0.0, "b": 50.0, "joint": 1.0}, {"a": 50.0, "b": 60.0, "joint": 0.9}], 0.0, 60.0, 0.0)
    assert act == [(0.0, 50 / 365.25)] and sh == pytest.approx(50 / 60)
    merged, _ = active_windows([{"a": 0.0, "b": 10.0, "joint": 0.9}, {"a": 10.0, "b": 20.0, "joint": 0.8},
                                {"a": 40.0, "b": 50.0, "joint": 0.1}], 0.0, 60.0, 0.0)
    assert merged == [(0.0, 20 / 365.25)]
    assert active_windows([], 0.0, 60.0, 0.0) == ([], 0.0)


@pytest.mark.parametrize("b", BIRTHS, ids=[x["name"] for x in BIRTHS])
def test_a_third_of_the_life_is_active_and_inside_it(b):
    f = chart_features(_birth(b), until=UNTIL.isoformat())
    age = (UNTIL - datetime.fromisoformat(b["utc"]).date()).days / 365.25
    assert f["until"] == "2026-10-22" and f["rules"]
    scored = [a for a in f["areas"].values() if a["score"] is not None]
    assert scored
    for name, a in f["areas"].items():
        assert set(a["votes"]) >= {"house", "lord", "karaka"} or a["tier"] == "needs two charts"
        assert set(a["terms"]) >= {"house", "lord"} or a["tier"] == "needs two charts"
        if age <= 0:                                              # synthetic-3 is born in 2036
            assert a["active"] == [] and a["active_share"] == 0.0
            continue
        if a["score"] is None:
            continue
        assert 0.2 <= a["active_share"] <= 0.45, (name, a["active_share"])
        assert all(0 <= x < y <= age + 0.01 for x, y in a["active"])
        assert all(y1 < x2 for (_, y1), (x2, _) in zip(a["active"], a["active"][1:]))    # merged and sorted
        assert sum(y - x for x, y in a["active"]) == pytest.approx(a["active_share"] * age, abs=0.02)


def test_the_stability_gate_rides_with_the_features():
    b = _birth(BIRTHS[0])
    f = chart_features(dict(b, accuracy="exact"), until=UNTIL.isoformat(), stability_samples=12)
    scored = {k: a for k, a in f["areas"].items() if a["score"] is not None}
    assert f["stability_samples"] == 12 and scored
    assert all(0.0 <= a["stability_time"] <= 1.0 and isinstance(a["narrate"], bool) for a in scored.values())
    assert sum(a["narrate"] for a in scored.values()) >= len(scored) - 2             # +-2 minutes moves little
    g = chart_features(dict(b, accuracy="unknown"), until=UNTIL.isoformat(), stability_samples=12)
    assert any(a["narrate"] is False for a in g["areas"].values() if a["score"] is not None)   # a day's window
    plain = chart_features(b, until=UNTIL.isoformat())
    assert plain["stability_samples"] == 0
    assert all(a["narrate"] is None and a["stability_time"] is None for a in plain["areas"].values())


def test_the_reference_charts_career_activation(chart):
    f = chart_features(_birth(BIRTHS[0]), until=UNTIL.isoformat())
    career = f["areas"]["career"]
    # Jupiter-Venus, the join's best window of 2026-2036, has not begun by 2026-10-22; the active
    # years are a ranking over the life, so their joint is above the life's median piece.
    jd0 = chart.meta.jd
    spans = slow_spans("lahiri", False, jd0, swe.julday(2026, 10, 22, 0.0))
    pieces = window_pieces(chart, "career", jd0, swe.julday(2026, 10, 22, 0.0), spans)
    joints = sorted(p["joint"] for p in pieces)
    median = joints[len(joints) // 2]
    for x, y in career["active"]:
        mid = jd0 + 365.25 * (x + y) / 2
        p = next(p for p in pieces if p["a"] <= mid < p["b"])
        assert p["joint"] >= median
    assert career["active_share"] == pytest.approx(ACTIVE_SHARE, abs=0.05)
