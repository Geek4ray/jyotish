"""Tagged timeline and TimingQuery on the reference chart: "career, 2026-2036"."""

import pytest
import swisseph as swe
from pydantic import ValidationError

from jyotish.models import TimingQuery
from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
from jyotish.timing import answer, dasha_rows, tagged_timeline
from jyotish.transits import transit_timeline
from jyotish.uncertainty import assess

A, B = swe.julday(2026, 1, 1, 0.0), swe.julday(2036, 1, 1, 0.0)
CAREER = dict(area="career", start="2026-01-01", end="2036-01-01", question="When does career rise?")


@pytest.fixture(scope="module")
def chart():
    return assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)


@pytest.fixture(scope="module")
def ans(chart):
    return answer(chart, TimingQuery(**CAREER))


def test_query_is_validated():
    with pytest.raises(ValidationError, match="unknown area"):
        TimingQuery(**dict(CAREER, area="love"))
    with pytest.raises(ValidationError, match="end must be after start"):
        TimingQuery(**dict(CAREER, start="2036-01-01", end="2026-01-01"))
    with pytest.raises(ValidationError):
        TimingQuery(**dict(CAREER, systems=["kalachakra"]))
    with pytest.raises(ValidationError):
        TimingQuery(**dict(CAREER, systems=[]))


def test_tagged_timeline_merges_dashas_and_transits(chart):
    tl = tagged_timeline(chart, A, B)
    kinds = {r.kind for r in tl.rows}
    assert kinds == {"dasha", "transit"}
    assert [r.start_jd for r in tl.rows] == sorted(r.start_jd for r in tl.rows)
    dashas = [r for r in tl.rows if r.kind == "dasha"]
    assert {(r.system, r.level) for r in dashas} == {(s, l) for s in ("vimshottari", "yogini", "chara") for l in (1, 2)}
    assert all(-1.0 <= r.quality <= 1.0 and r.tara for r in dashas)
    assert len([r for r in tl.rows if r.kind == "transit"]) == len(transit_timeline(chart, A, B).rows)
    jup = next(r for r in dashas if r.system == "vimshottari" and r.lords == ["Jupiter"])
    # Nadi activation: planets in Jupiter's nakshatras (PurvaBhadra: the Sun; ...), and
    # Jupiter's own nakshatra lord (Rohini: the Moon).
    assert "Moon" in jup.activation and "Sun" in jup.activation


def test_career_windows(ans, chart):
    assert ans.area_tier == chart.scored.areas["career"].tier and ans.area_stability is not None
    ws = ans.windows
    assert 1 <= len(ws) <= 5 and [w.joint for w in ws] == sorted((w.joint for w in ws), reverse=True)
    for w in ws:
        assert A <= w.start_jd < w.end_jd <= B
        assert set(w.periods) == {"vimshottari", "yogini", "chara"}
        d = w.derivation
        assert w.joint == pytest.approx(d["S_norm"] * w.dasha_quality + w.transit_activation)
        parts = [s["quality"] * s["relevant"] for s in d["systems"].values()]
        assert w.dasha_quality == pytest.approx(sum(parts) / len(parts), abs=1e-4)
        assert 0.0 <= w.transit_activation <= 1.0
        assert w.stability is not None and w.stability["time_range_days"] >= 0
    top = ws[0]
    # 2030: Jupiter-Venus in Vimshottari with the double transit on the 10th or its lord.
    assert top.periods["vimshottari"] == ["Jupiter", "Venus"]
    assert top.transit_activation == pytest.approx(1.0)
    assert swe.julday(2030, 1, 1, 0) < top.start_jd < swe.julday(2031, 1, 1, 0)


def test_sandhi_tags(chart):
    # The Yogini maha boundary (Siddha -> Sankata, 2028-08-02) and the Chara one
    # (Pisces -> Aquarius, 2028-03-11) fall in the range: windows near them are tagged.
    full = answer(chart, TimingQuery(**dict(CAREER, top=50)))
    tagged = [w for w in full.windows if "dasha_sandhi" in w.tags]
    assert tagged
    marks = (swe.julday(2028, 3, 11, 0), swe.julday(2028, 8, 2, 0))
    assert any(abs(w.start_jd - m) < 31 or abs(w.end_jd - m) < 31 for w in tagged for m in marks)


def test_systems_subset_and_no_uncertainty():
    from jyotish.chart import analyse
    from jyotish.reference import REFERENCE_ASC, REFERENCE_POSITIONS, REFERENCE_SPEEDS, reference_time_inputs
    c = analyse(REFERENCE_POSITIONS, REFERENCE_ASC, speeds=REFERENCE_SPEEDS, **reference_time_inputs())
    a = answer(c, TimingQuery(**dict(CAREER, systems=["vimshottari"])))
    assert all(set(w.periods) == {"vimshottari"} and w.stability is None for w in a.windows)
    assert a.area_stability is None


def test_dasha_rows_cover_the_range(chart):
    rows = [r for r in dasha_rows(chart, A, B) if r.system == "vimshottari" and r.level == 2]
    assert rows[0].start_jd <= A and rows[-1].end_jd >= B
    assert all(x.end_jd == pytest.approx(y.start_jd) for x, y in zip(rows, rows[1:]))
