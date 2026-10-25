"""The astrologer's technical sheet (jyotish.sheet) on the reference chart: every point's figures read
against the chart object itself, not against the payload the sheet is written from, so a wrong path or
a wrong rounding in either shows here."""

from datetime import date, timedelta

import pytest

from jyotish.constants import SEVEN, SIGN_LORD, SIGNS
from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
from jyotish.scoring import AREAS, THEME_AREAS, varga_dignity_word
from jyotish.sheet import ORD, TITLES, build, sheets
from jyotish.uncertainty import assess

AS_OF = date(2026, 10, 21)
AREA = "career"


@pytest.fixture(scope="module")
def chart():
    return assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)


@pytest.fixture(scope="module")
def sheet(chart):
    return sheets(chart, AS_OF, ["career", "marriage", "longevity"])[AREA]


def point(sheet, n):
    p = sheet["points"][n - 1]
    assert p["n"] == n and p["title"] == TITLES[n]
    return p


def texts(sheet, n):
    return [i["text"] for i in point(sheet, n)["items"]]


def fires(chart, area=AREA):
    return [f for f in chart.fired_rules if any(area in THEME_AREAS.get(th, []) for th in f.themes)]


def test_fifteen_points_each_item_citing_paths_that_resolve(chart, sheet):
    from jyotish.fullchart import cached_payload, resolve
    from jyotish.narrate import full_range
    data = cached_payload(chart, AS_OF, *full_range(AS_OF), ["career", "marriage", "longevity"])
    assert [p["n"] for p in sheet["points"]] == list(range(1, 16))
    for p in sheet["points"]:
        assert p["items"], p["title"]
        for it in p["items"]:
            for path in it["facts"]:
                resolve(data, path)                                  # KeyError if a path does not exist
    cited = [it for p in sheet["points"] if p["n"] != 13 for it in p["items"] if it["facts"]]
    assert len(cited) >= 0.9 * sum(len(p["items"]) for p in sheet["points"] if p["n"] != 13)


def test_1_houses_from_the_lagna_moon_and_sun_with_bhava_bala(chart, sheet):
    bb = chart.features.bhava_bala.whole_sign
    order = sorted(bb, key=lambda h: -bb[h].rupas)
    asc, moon = chart.lagnas.asc_sign, chart.bodies["Moon"].sign
    t = texts(sheet, 1)
    for i, h in enumerate(AREAS[AREA]["houses"]):
        sign = (asc + h - 1) % 12
        assert t[i].startswith(f"{ORD[h]} from the lagna: {SIGNS[sign]}, lord {SIGN_LORD[sign]}")
        assert f"{bb[h].rupas:.2f} rupas" in t[i] and f"rank {order.index(h) + 1} of 12" in t[i]
    assert "Bhava Bala (house strength)" in t[0] and "(house strength)" not in t[1]      # English on first use only
    from_moon = next(x for x in t if x.startswith("From the Moon"))
    assert f"10th {SIGNS[(moon + 9) % 12]} (lord {SIGN_LORD[(moon + 9) % 12]}" in from_moon
    assert any(x.startswith("From the Sun") for x in t)


def test_2_lords_with_sign_house_dignity_shadbala_avastha_and_flags(chart, sheet):
    sat = next(x for x in texts(sheet, 2) if x.startswith("Saturn"))
    b, sb = chart.bodies["Saturn"], chart.features.shadbala.planets["Saturn"]
    assert "lord of the 10th from the lagna" in sat and f"{b.sign_name}" in sat and f"in the {ORD[b.house]}" in sat
    assert b.dignity in sat and f"ratio {sb.ratio:.2f} ({sb.total / 60:.2f} of {sb.required / 60:.2f}" in sat
    assert b.avastha_baladi in sat
    assert ("marana karaka sthana" in sat) == bool(b.marana_karaka_sthana)
    lords = [x.split(" — ")[0] for x in texts(sheet, 2)]
    assert set(lords) == set(chart.scored.areas[AREA].lords)


def test_3_karakas_the_same_way_main_first(chart, sheet):
    t = texts(sheet, 3)
    assert [x.split(" — ")[0] for x in t] == chart.scored.areas[AREA].karakas
    sun = chart.features.shadbala.planets["Sun"]
    assert t[0].startswith("Sun — main karaka") and f"ratio {sun.ratio:.2f}" in t[0]


def test_4_every_rule_and_placement_fired_with_source_status_scale_and_reductions(chart, sheet):
    t = texts(sheet, 4)
    fs = fires(chart)
    assert len(t) == len(fs)
    for f in fs:
        line = next(x for x in t if f"[{f.id}@{f.basis}]" in x)
        assert f"status {f.status}" in line and f"scale {f.scale:.2f}" in line
        assert all(a in line for a in f.applied) or (not f.applied and "no reduction" in line)
    ruchaka = [x for x in t if "[yoga.ruchaka@" in x]
    assert ruchaka and all("BPHS (Santhanam 1984) ch. 75, v. 1-2, checked" in x for x in ruchaka)
    assert any("ch. 24, not yet located, not checked" in x for x in t)          # a draft placement's honest source


def test_5_vargas_with_sign_and_dignity_vargottama_and_the_varga_lagnas_stability(chart, sheet):
    t = texts(sheet, 5)
    d10 = chart.vargas["D10"]
    for p in SEVEN:
        assert f"{p} {SIGNS[d10[p]]} {varga_dignity_word(p, d10[p])}" in t[0]
    assert t[0].startswith("D10 (dasamsa): ")
    st = chart.uncertainty.varga_stability["D10"]
    assert t[1].startswith(f"D10 lagna {SIGNS[d10['Asc']]}") and f"holds in {round(st * 200)} of 200" in t[1]
    vg = [p for p in chart.bodies if chart.bodies[p].vargottama and p != "Asc"]
    assert t[-1].endswith(f": {', '.join(vg) or 'none'}.")


def test_6_nakshatra_tara_chains_and_activation_of_the_lord_and_the_karaka(chart, sheet):
    from jyotish.display import dispositor_panel
    from jyotish.timing import activation_set
    t = texts(sheet, 6)
    b = chart.bodies["Saturn"]
    assert t[0] == (f"Saturn (10th lord): nakshatra (lunar mansion) {b.nak_name} pada {b.pada}, lord {b.nak_lord}; "
                    f"tara (star counted from the Moon's) {b.tara.name} (cycle {b.tara.cycle}).")
    panel = dispositor_panel(chart)
    chain = next(r["chain"] for r in panel["sign"]["rows"] if r["planet"] == "Saturn")
    assert f"sign {' → '.join(chain)}" in t[1]
    assert f"the Jupiter major period activates {', '.join(activation_set(chart, 'Jupiter'))}" in t[2]
    assert any(x.startswith("Sun (main karaka)") for x in t)


def test_7_kp_cusp_star_sub_lord_significations_and_verdict(chart, sheet):
    t = texts(sheet, 7)
    kp = chart.lagnas.cusp_lords_kp[10]
    assert t[0].startswith(f"KP (Krishnamurti Paddhati) cusp 10: star lord {kp['star']}, sub-lord (lord of the cusp's "
                           f"sub) {kp['sub']}")
    word = {1: "for", -1: "against", 0: "abstains", None: "not applied"}[chart.scored.areas[AREA].votes.get("kp")]
    assert t[-1] == f"KP verdict: {word}."


def test_8_jaimini_arudha_occupants_benefics_and_verdict(chart, sheet):
    t = texts(sheet, 8)
    a10 = SIGNS[chart.features.jaimini.arudhas["A10"]]
    occ = [p for p in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu")
           if chart.bodies[p].sign == chart.features.jaimini.arudhas["A10"]]
    assert t[0].startswith(f"arudha (the image of a house) A10: {a10}") and f"occupants {', '.join(occ)}" in t[0]
    word = {1: "for", -1: "against", 0: "abstains"}[chart.scored.areas[AREA].votes["arudha"]]
    assert t[-1].startswith(f"Jaimini verdict: {word}")


def test_9_panchanga_lords_and_the_houses_they_rule(chart, sheet):
    t = texts(sheet, 9)
    pa, lordship = chart.panchanga, chart.features.lordship
    tithi = next(x for x in t if x.startswith("tithi"))
    assert f"lord {pa.tithi_lord}" in tithi and ", ".join(ORD[h] for h in lordship[pa.tithi_lord]) in tithi
    assert any(x.startswith(f"vara (weekday) lord {pa.vara_lord}") for x in t)
    assert any(x.startswith(f"nakshatra lord {pa.nakshatra_lord}") for x in t)


def test_10_the_family_votes_as_a_table(chart, sheet):
    from jyotish.fullchart import contributions
    p = point(sheet, 10)
    a = chart.scored.areas[AREA]
    rows = {r["family"]: r for r in p["table"]["rows"]}
    word = {1: "for", -1: "against", 0: "abstains", None: "not applied"}
    assert p["table"]["columns"] == ["family", "vote", "rests on", "percentile"]
    assert {f: r["vote"] for f, r in rows.items()} == {f: word[v] for f, v in a.votes.items()}
    pct = {r["family"]: r["percentile"] for r in contributions(a, AREA, chart)["ranked"]}
    assert all(rows[f]["percentile"] == pct.get(f) for f in rows)
    assert rows["house"]["rests on"].startswith(f"10th Aquarius, {chart.features.bhava_bala.whole_sign[10].rupas:.2f}")


def test_11_running_periods_with_lords_and_every_window_with_its_figures(chart, sheet):
    from jyotish.models import TimingQuery
    from jyotish.narrate import full_range
    from jyotish.timing import _jd, answer
    t = texts(sheet, 11)
    jd = _jd(AS_OF)
    maha = next(p for p in chart.dashas["vimshottari"] if len(p.lords) == 1 and p.start_jd <= jd < p.end_jd)
    antar = next(p for p in chart.dashas["vimshottari"] if len(p.lords) == 2 and p.start_jd <= jd < p.end_jd)
    assert f"major period {maha.lords[0]}" in t[0] and f"sub-period {antar.lords[1]}" in t[0]
    assert any(x.startswith(f"{maha.lords[0]}: {chart.bodies[maha.lords[0]].dignity}, tara "
                            f"{chart.bodies[maha.lords[0]].tara.name}") for x in t)
    ans = answer(chart, TimingQuery(area=AREA, start=full_range(AS_OF)[0], end=full_range(AS_OF)[1]))
    wins = [x for x in t if x.startswith("Window ")]
    assert len(wins) == len(ans.windows)
    for w, line in zip(ans.windows, wins):
        assert f"score {round(w.joint, 3):.3f}" in line and f"q {round(w.dasha_quality, 3):.3f}" in line
    assert any(x.startswith("Avoid ") for x in t) == (ans.avoid is not None)


def test_12_transit_spans_of_saturn_jupiter_and_the_nodes_and_the_tara_rows(chart, sheet):
    from jyotish.narrate import full_range
    from jyotish.timing import _jd
    from jyotish.transits import transit_timeline
    start, end = full_range(AS_OF)
    tl = transit_timeline(chart, _jd(start), _jd(end))
    t = texts(sheet, 12)
    slow = [r for r in tl.rows if r.body in ("Saturn", "Jupiter", "Rahu", "Ketu")]
    assert sum(1 for x in t if x.split(" in ")[0] in ("Saturn", "Jupiter", "Rahu", "Ketu") and " from the Moon, " in x) \
        == len(slow)
    first = slow[0]
    assert t[0].startswith(f"{first.body} in {first.sign_name}") and f"{ORD[first.houses['moon']]} from the Moon" in t[0]
    taras = [r for r in tl.tara_rows if r.body != "Moon"]
    assert sum(1 for x in t if "from the Moon's)" in x) == len(taras)


def test_13_the_readings_weighing_verbatim_and_marked(chart):
    from jyotish.fullchart import cached_payload
    from jyotish.narrate import full_range
    data = cached_payload(chart, AS_OF, *full_range(AS_OF), ["career", "marriage", "longevity"])
    j = [{"section": "timing", "sentence": "I give more weight to the Jupiter–Venus window [fact:timing.career.windows.0]."}]
    s = build(data, AREA, j)
    assert texts(s, 13) == [f"The reading's weighing (timing): {j[0]['sentence']}"]
    assert texts(build(data, AREA), 13)[0].startswith("No weighing sentences")


def test_14_stability_the_three_numbers_and_every_finding_below_1(chart, sheet):
    t = texts(sheet, 14)
    st = chart.scored.areas[AREA].stability
    assert t[0].startswith(f"The area's tier: time {round(st.time, 3)}, ayanamsa {round(st.ayanamsa, 3)}, "
                           f"house {round(st.house, 3)}")
    weak = {f"{f.id}@{f.basis}" for f in fires(chart) if f.stability and (f.stability.ayanamsa < 1 or f.stability.house < 1)}
    listed = {x.split(":")[0] for x in t[1:] if "@" in x.split(":")[0]}
    assert listed == weak


def test_15_drafts_abstentions_and_not_computed(chart, sheet):
    from jyotish.fullchart import NOT_COMPUTED
    t = texts(sheet, 15)
    drafts = [f for f in fires(chart) if f.status == "draft"]
    assert t[0].startswith(f"{len(drafts)} draft placements")
    abst = [f for f, v in chart.scored.areas[AREA].votes.items() if v in (0, None)]
    assert all(f in t[1] for f in abst)
    assert sum(1 for x in t if x.startswith("Not computed — ")) == len(NOT_COMPUTED)


def test_every_offered_area_has_a_sheet_and_synastry_none(chart):
    s = sheets(chart, AS_OF, ["career", "marriage", "longevity", "synastry"])
    assert set(s) == {"career", "marriage", "longevity"}
    assert texts(s["marriage"], 1)[0].startswith("7th from the lagna")
    assert texts(s["longevity"], 5)[0].startswith("D30 (trimsamsa): ")


def test_the_rebuilt_r2_pages_are_the_current_renderers_and_show_both_views(tmp_path):
    """docs/comparison_2026-10-23_r2/{a,b}.page.md (scripts/rebuild_pages.py) are what the renderer makes
    from the readings' JSON today; each area has the technical sheet, B its analysis under the same toggle."""
    import shutil
    import sys
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    src = root / "docs" / "comparison_2026-10-23_r2"
    for side in ("a", "b"):
        shutil.copy(src / f"{side}.reading.json", tmp_path / f"{side}.reading.json")
    sys.path.insert(0, str(root / "scripts"))
    try:
        import rebuild_pages
        made = rebuild_pages.rebuild(tmp_path)
    finally:
        sys.path.remove(str(root / "scripts"))
    for side, path in made.items():
        committed = (src / f"{side}.page.md").read_text()
        assert path.read_text() == committed, f"{side}.page.md is stale: run scripts/rebuild_pages.py"
        assert committed.count("<summary>For the astrologer</summary>") == 3
        assert committed.count("### The technical sheet") == 3 and "15. **Drafts, abstentions" in committed
    b = (src / "b.page.md").read_text()
    assert b.count("### Assessment") == 3 and b.count("### What the chart does not say") == 3
    assert b.count("*Not written within the checks.*") == 2           # B's two gaps: career assessment, marriage timing
