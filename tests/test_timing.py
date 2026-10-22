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


def with_formula(chart, formula):
    return chart.model_copy(update={"meta": chart.meta.model_copy(update={"timing_formula": formula})})


def v1(chart):
    return with_formula(chart, "v1")


@pytest.fixture(scope="module")
def ans(chart):
    return answer(v1(chart), TimingQuery(**CAREER))


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
    assert kinds == {"dasha", "transit", "tara"}                     # tara rows: tagged, not scored
    assert [r.start_jd for r in tl.rows] == sorted(r.start_jd for r in tl.rows)
    dashas = [r for r in tl.rows if r.kind == "dasha"]
    assert {(r.system, r.level) for r in dashas} == {(s, l) for s in ("vimshottari", "yogini", "chara") for l in (1, 2)}
    assert all(-1.0 <= r.quality <= 1.0 and r.tara for r in dashas)
    assert len([r for r in tl.rows if r.kind == "transit"]) == len(transit_timeline(chart, A, B).rows)
    assert len([r for r in tl.rows if r.kind == "tara"]) == len(transit_timeline(chart, A, B).tara_rows)
    jup = next(r for r in dashas if r.system == "vimshottari" and r.lords == ["Jupiter"])
    # Nadi activation: planets in Jupiter's nakshatras (PurvaBhadra: the Sun; ...), and
    # Jupiter's own nakshatra lord (Rohini: the Moon).
    assert "Moon" in jup.activation and "Sun" in jup.activation


def test_career_windows_v1(ans, chart):
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


def test_sandhi_tags_v1(chart):
    # The Yogini maha boundary (Siddha -> Sankata, 2028-08-02) and the Chara one
    # (Pisces -> Aquarius, 2028-03-11) fall in the range: windows near them are tagged.
    full = answer(v1(chart), TimingQuery(**dict(CAREER, top=50)))
    tagged = [w for w in full.windows if "dasha_sandhi" in w.tags]
    assert tagged
    marks = (swe.julday(2028, 3, 11, 0), swe.julday(2028, 8, 2, 0))
    assert any(abs(w.start_jd - m) < 31 or abs(w.end_jd - m) < 31 for w in tagged for m in marks)


def test_systems_subset_and_no_uncertainty():
    from jyotish.chart import analyse
    from jyotish.reference import REFERENCE_ASC, REFERENCE_POSITIONS, REFERENCE_SPEEDS, reference_time_inputs
    c = analyse(REFERENCE_POSITIONS, REFERENCE_ASC, speeds=REFERENCE_SPEEDS, **reference_time_inputs())
    a = answer(v1(c), TimingQuery(**dict(CAREER, systems=["vimshottari"])))
    assert all(set(w.periods) == {"vimshottari"} and w.stability is None for w in a.windows)
    assert a.area_stability is None


def test_dasha_rows_cover_the_range(chart):
    rows = [r for r in dasha_rows(chart, A, B) if r.system == "vimshottari" and r.level == 2]
    assert rows[0].start_jd <= A and rows[-1].end_jd >= B
    assert all(x.end_jd == pytest.approx(y.start_jd) for x, y in zip(rows, rows[1:]))


# --- v2 ------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def v2(chart):
    return answer(with_formula(chart, "v2"), TimingQuery(**CAREER))


def test_career_v2_windows(v2, chart):
    assert v2.formula == "v2" and len(v2.windows) == 3 and v2.avoid is not None
    assert v2.area_tier == chart.scored.areas["career"].tier          # narrated, not multiplied
    for w in v2.windows + [v2.avoid]:
        assert w.joint == pytest.approx(0.6 * w.dasha_quality + 0.4 * w.transit_activation)
        assert 0 <= w.dasha_quality <= 1 and 0 <= w.transit_activation <= 1
        assert w.end_jd - w.start_jd >= 30                               # short ones absorbed
        assert "vimshottari" in w.derivation["relevant_systems"] or w.derivation["q_terms"]["relevance"] == 0
        assert set(w.derivation["q_terms"]) <= {"dignity", "shadbala", "ishta", "tara", "relevance", "relation"}
    top = v2.windows[0]
    # Jupiter-Venus, Oct 2029 - Jun 2032: Venus exalted, Shadbala ratio above 1, high
    # Ishta, and relevant as Amatyakaraka (a career karaka); every system's lords relevant.
    assert top.periods["vimshottari"] == ["Jupiter", "Venus"]
    assert swe.julday(2029, 10, 1, 0) < top.start_jd < swe.julday(2029, 11, 1, 0)
    assert top.confidence == "strong" and top.derivation["pieces"] > 1    # merged across ingresses
    # Avoid: Jupiter-Ketu (Ketu 8th from Jupiter: relation 0; Ketu in Vadha tara: 0).
    assert v2.avoid.periods["vimshottari"] == ["Jupiter", "Ketu"]
    assert v2.avoid.derivation["q_terms"]["relation"] == 0.0


def test_v2_transit_term_saturates_for_career(v2):
    # With four career houses and their lords, Saturn and Jupiter touch at least one of
    # them nearly all the time, so t is 1 (the double transit) across the decade. Reported
    # as a property of the v2 definition, not tuned.
    assert all(w.transit_activation == pytest.approx(1.0) for w in v2.windows + [v2.avoid])


def test_v2_sandhi_caps_confidence(chart):
    full = answer(with_formula(chart, "v2"), TimingQuery(**dict(CAREER, top=50)))
    allw = full.windows + [full.avoid]
    sandhi = [w for w in allw if "dasha_sandhi" in w.tags]
    assert sandhi and all(w.confidence in ("moderate", "weak") for w in sandhi)
    # Jupiter-Mercury (Aug 2026 - Nov 2028) spans the Chara (2028-03-11) and Yogini
    # (2028-08-02) maha changes.
    jm = next(w for w in allw if w.periods["vimshottari"] == ["Jupiter", "Mercury"])
    assert "dasha_sandhi" in jm.tags and jm.confidence == "moderate"


# --- v2.1 (default): K.N. Rao's double-transit targets ------------------------------

def _d(jd):
    y, m, d, _ = swe.revjul(jd, swe.GREG_CAL)
    return f"{y:04d}-{m:02d}"


def test_v21_is_the_default(chart):
    assert chart.meta.timing_formula == "v2.1"


def test_career_v21_decade(chart):
    # The numbers SPEC's prototype gave for 2026-2036 (rev 76), reproduced by the engine.
    a = answer(chart, TimingQuery(**CAREER))
    assert a.formula == "v2.1"
    rows = [(w.periods["vimshottari"], _d(w.start_jd), _d(w.end_jd), round(w.joint, 2), round(w.transit_activation, 2))
            for w in a.windows]
    assert rows == [(["Jupiter", "Venus"], "2029-10", "2032-06", 0.84, 0.88),
                    (["Jupiter", "Mercury"], "2027-10", "2028-02", 0.84, 1.0),
                    (["Jupiter", "Saturn"], "2026-01", "2026-08", 0.83, 0.95)]
    av = a.avoid
    assert (av.periods["vimshottari"], _d(av.start_jd), _d(av.end_jd), round(av.joint, 2),
            round(av.transit_activation, 2)) == (["Jupiter", "Ketu"], "2028-11", "2029-08", 0.47, 0.67)
    top = a.windows[0].derivation
    assert top["targets"] == {"full": ["Aquarius", "Taurus"], "secondary": ["Gemini", "Libra", "Pisces"]}
    sp = top["strongest_piece"]
    assert sp["t"] == 1.0 and sp["end_jd"] - sp["start_jd"] >= 30 and _d(sp["start_jd"]).startswith("2030")
    assert "truncated" in a.windows[2].tags                    # Jupiter-Saturn began before 2026
    assert "dasha_sandhi" in a.windows[1].tags and a.windows[1].confidence == "moderate"
    for w in a.windows + [a.avoid]:
        d = w.derivation
        assert w.joint == pytest.approx(0.6 * w.dasha_quality + 0.4 * w.transit_activation)
        assert d["t"] == w.transit_activation and set(d["q_terms"]) and "relevant_systems" in d


def test_v21_t_no_longer_saturates(chart):
    a = answer(chart, TimingQuery(**dict(CAREER, top=50)))
    ts = [w.transit_activation for w in a.windows + [a.avoid]]
    assert min(ts) < 0.7 and max(ts) == pytest.approx(1.0)


def test_career_v21_from_today(chart):
    a = answer(chart, TimingQuery(area="career", start="2026-10-21", end="2036-10-21"))
    assert [w.periods["vimshottari"] for w in a.windows] == [["Jupiter", "Venus"], ["Jupiter", "Mercury"],
                                                            ["Jupiter", "Mercury"]]
    third = a.windows[2]
    assert "truncated" in third.tags and _d(third.start_jd) == "2026-10"
    assert a.avoid.periods["vimshottari"] == ["Jupiter", "Ketu"]


def test_absorbed_piece_keeps_host_label(chart):
    a = answer(chart, TimingQuery(**dict(CAREER, top=50)))
    hosts = [w for w in a.windows + [a.avoid] if w.derivation["absorbed"]]
    assert hosts                      # 2029-10-05 - 10-23, absorbed by Jupiter-Ketu Aug - Oct 2029
    for w in hosts:
        for piece in w.derivation["absorbed"]:
            assert piece["end_jd"] - piece["start_jd"] < 30
            assert w.start_jd <= piece["start_jd"] and piece["end_jd"] <= w.end_jd
