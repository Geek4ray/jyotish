"""`jyotish read` end to end, offline: birth data and a question -> reading JSON and the
Markdown page, with the model replayed from a recording (--model-fixture)."""

import json
from pathlib import Path

import pytest

from jyotish.cli import _birth_utc, main
from jyotish.narrate import TAG, Reading
from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON

FIXTURES = Path(__file__).parent / "fixtures"
QUESTION = "How will my career go, and when is the best time for a job change?"
BIRTH = ["--date", "2001-03-12", "--time", "10:10:25", "--tz", "Asia/Kolkata", "--lat", str(REFERENCE_LAT),
         "--lon", str(REFERENCE_LON), "--node", "mean", "--question", QUESTION, "--as-of", "2026-10-21",
         "--depth", "astrologer"]          # the fixtures are astrologer drafts; curious is tested on its own


def run(args):
    with pytest.raises(SystemExit) as e:
        main(["read", *BIRTH, *args])
    return e.value.code


@pytest.fixture(scope="module")
def page(tmp_path_factory):
    out = tmp_path_factory.mktemp("read") / "reading"
    # The hand-edited copy of the frozen recording: the frozen draft itself no longer passes
    # the validator (see test_frozen_recording_fails_cleanly).
    assert run(["--out", str(out), "--model-fixture", str(FIXTURES / "narration_career_edited.json")]) == 0
    return Reading(**json.loads(out.with_suffix(".json").read_text())), out.with_suffix(".md").read_text()


def test_birth_time_from_iana_name_or_offset():
    assert _birth_utc("2001-03-12", "10:10:25", "Asia/Kolkata") == (REFERENCE_BIRTH_UTC, "Asia/Kolkata")
    assert _birth_utc("2001-03-12", "10:10:25", "+05:30") == (REFERENCE_BIRTH_UTC, None)


def test_reading_json_is_the_output_schema(page):
    reading, _ = page
    assert [a.name for a in reading.areas] == ["career", "marriage", "longevity"]   # asked, then the top three
    assert reading.narration_source.endswith("narration_career_edited.json")
    assert reading.summary.current_period == "Jupiter-Mercury" and reading.summary.time_window_min == 2
    assert all(a.probability is None and not a.calibrated for a in reading.areas)
    assert sorted(reading.disclaimers) == ["longevity", "third_party"]
    # The edited fixture has no checker calls: every sentence on the page is unchecked, and says so.
    assert reading.unchecked_sentences == 2 + 8


def test_page_sections_in_order(page):
    _, md = page
    heads = ["## Summary", "## Career", "## Marriage", "## Longevity", "## Depends on exact birth time",
             "## Learner: what each claim rests on", "## Disclaimers"]
    pos = [md.index(h) for h in heads]
    assert pos == sorted(pos)
    assert "10 sentence(s) on this page have no recorded checker verdict" in md
    for field in ("- Driver: Venus", "- Current period (Vimshottari): Jupiter-Mercury", "- Top areas: career, marriage, longevity",
                  "- Birth-time window: ±2 min", "- Fired rules stable / unstable under that window: 5 / 0",
                  "- Abstained areas: children, father, gains, synastry"):
        assert field in md
    career = md[md.index("## Career"):md.index("## Marriage")]
    assert "- Stability: time 1.00 · ayanamsa 1.00 · house 1.00 (stable)" in career
    assert "- Polarity: intensity (house H10, lord Saturn, karaka Sun)" in career
    assert "School conflict" not in career                    # KP v2 abstains on career
    assert "the Jaimini family (arudha) is against" in md[md.index("## Marriage"):md.index("## Longevity")]
    assert "| avoid | 2028-11-17 | 2029-08-08 |" in career and "strongest piece" in career
    # Windows only for the area the question routes to: none for marriage or longevity.
    others = md[md.index("## Marriage"):md.index("## Depends on exact birth time")]
    assert "Windows" not in others and "| avoid |" not in others


def test_windows_only_for_the_routed_area(page):
    reading, _ = page
    assert [bool(a.windows) for a in reading.areas] == [True, False, False]
    assert [a.avoid_window is not None for a in reading.areas] == [True, False, False]


def test_chart_header_reproduces_the_page(page, tmp_path):
    import shlex
    reading, md = page
    c = reading.chart["conventions"]
    assert (c["ayanamsa"], c["node"], c["house_system"], c["dasha_year"], c["karaka_scheme"]) == \
        ("lahiri", "mean", "whole_sign", 365.25, 8)
    line = next(x for x in md.splitlines() if x.startswith("**Chart:**"))
    for part in ("born 2001-03-12 10:10:25 (Asia/Kolkata) = 2001-03-12T04:40:25+00:00 UTC", "accuracy exact",
                 "ayanamsa lahiri", "node mean", "houses whole_sign (KP placidus)", "dasha year 365.25 days",
                 "karaka scheme 8"):
        assert part in line, part
    assert "chara_variant kn_rao" in md and "Stability sampler: 200 birth times, uniform ±2 min, seed 0" in md
    # Re-running the header's own command gives the same page.
    command = next(x for x in md.splitlines() if x.startswith("Reproduce: "))[len("Reproduce: `"):-1]
    argv = shlex.split(command)[1:]
    out = tmp_path / "again"
    with pytest.raises(SystemExit) as e:
        main([*argv, "--out", str(out)])
    assert e.value.code == 0 and out.with_suffix(".md").read_text() == md


def test_sensitive_claims_are_marked_inline(page):
    # Every career claim holds in all samples under v2 (no mark); a claim under 0.8 carries
    # its number after its tags, in the claim list and in its learner entry.
    from jyotish.page import render
    from jyotish.uncertainty import assess
    reading, md = page
    assert "*(time-stability" not in md
    career = reading.areas[0]
    claims = [c.model_copy(update={"stability": 0.605, "stability_label": "sensitive"}) if c.finding_id == "vote:career.varga" else c
              for c in career.claims]
    shaky = reading.model_copy(update={"areas": [career.model_copy(update={"claims": claims})] + reading.areas[1:]})
    chart = assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)
    body = render(shaky, chart).split("\n---\n")[0]
    varga = next(x for x in body.splitlines() if x.startswith("8. The varga vote"))
    assert varga.endswith("]. *(time-stability 0.605, sensitive)*")
    assert body.count("*(time-stability") == 2                  # the claim list and its learner entry


def test_claims_in_engine_order_with_tags_as_footnotes(page):
    reading, md = page
    body, notes = md.split("\n---\n")
    assert not TAG.search(body)                                 # every tag became a footnote
    career = reading.areas[0]
    assert [c.finding_id for c in career.claims][:3] == ["yoga.kendra_trikona_raja@lagna", "yoga.budhaditya@lagna",
                                                          "yoga.ruchaka@lagna+sun"]
    assert career.claims[-1].finding_id == "vote:career.varga"
    first = md.index("1. The Sun and Mercury conjoined in the 10th join")
    assert first < md.index("8. The varga vote is for career")
    tags = {t for a in reading.areas for c in a.claims for t in c.cites} | set(reading.summary.cites)
    assert {line.split("`")[1] for line in notes.strip().splitlines()} == tags


def test_learner_tables_come_from_the_engine(page):
    _, md = page
    learner = md[md.index("## Learner"):]
    ruchaka = learner[learner.index("`yoga.ruchaka@lagna+sun`"):learner.index("`vote:career.house`")]
    assert "| marana_karaka_sthana | ×0.6 | applied | applied |" in ruchaka
    assert "| shadbala_ratio < 1.0 | ×0.5 | not applied | not applied |" in ruchaka
    assert "| lagna | Mars, H7 | 0.408 | 1 | rule and text | no |" in ruchaka
    assert "| sun | Mars, H10 | 0.408 | 1 | rule | yes |" in ruchaka
    assert "Sudarshana: the fire from the Sun" in ruchaka
    assert "| sun | 10 | Scorpio | 7.37 | -0.04 | – |" in learner           # house vote, basis on the row
    assert "| Jupiter | D10 | enemy | Aries | 0.5 | 0.25 | no | no | 0.25 |" in learner   # varga v2 row
    assert "Sudarshana" not in learner[:learner.index("`yoga.ruchaka@lagna+sun`")]


def test_frozen_recording_gives_a_reading_with_gaps(tmp_path, capsys):
    # The frozen first recording predates items 8 and 11: its summary names votes it does not
    # cite and mentions timing, and its Ruchaka claims carry the two pre-merge ids. Replayed,
    # it fails the validator on every attempt, and the reading still comes back: the claims
    # that pass are kept, the summary is the engine's, the rest are listed as gaps.
    out = tmp_path / "r1"
    assert run(["--out", str(out), "--model-fixture", str(FIXTURES / "narration_career_opus55_r1.json")]) == 0
    err = capsys.readouterr().err
    assert "narration incomplete" in err and "the summary is the engine's own" in err
    reading = Reading(**json.loads(out.with_suffix(".json").read_text()))
    assert reading.summary.source == "engine" and reading.summary.text.startswith("Career: tier moderate")
    career = reading.areas[0]
    assert "yoga.ruchaka@lagna+sun" in {g["finding_id"] for g in career.narration_gaps}
    assert {c.finding_id for c in career.claims} >= {"yoga.budhaditya@lagna", "vote:career.house"}
    md = out.with_suffix(".md").read_text()
    assert "> Narration incomplete:" in md and "*Written by the engine from its fields" in md
    assert "Not narrated within the checks:" in md and "`yoga.ruchaka@lagna+sun` (rule)" in md


TIMING_LINE = ("Best window for career by the engine's timing score: 2029-10-23 to 2032-06-23 "
               "(Vimshottari Jupiter–Venus, score 0.84), strongest from 2030-05-01 to 2030-09-22 (score 0.89). "
               "Window to avoid: 2028-11-17 to 2029-08-08 (Vimshottari Jupiter–Ketu, score 0.47).")


def test_when_question_gets_the_engine_timing_line(page):
    # SPEC Phase 4 item 2: the engine answers "when" in words, since the model may not.
    reading, md = page
    assert reading.summary.timing_line == TIMING_LINE
    summary = md[md.index("## Summary"):md.index("## Career")]
    assert f"**When (engine):** {TIMING_LINE}" in summary
    assert summary.index("**When (engine):**") < summary.index("- Driver:")
    assert not TAG.search(reading.summary.timing_line)          # engine text: no model tags


def test_timing_line_marks_sandhi_and_truncation_and_is_absent_without_when():
    from jyotish.narrate import ReadingWindow, timing_line
    w = ReadingWindow(start="2026-10-21", end="2027-01-24", score=0.834, q=0.734, q_terms={}, t=0.982,
                      relevant_systems=["vimshottari"], strongest_piece=None, confidence=None, stability=None,
                      sandhi=True, truncated=True, tags=["dasha_sandhi", "truncated"],
                      why=[{"kind": "dasha", "system": "vimshottari", "lords": ["Jupiter", "Mercury"]}])
    line = timing_line("career", [w], None)
    assert line == ("Best window for career by the engine's timing score: 2026-10-21 to 2027-01-24 "
                    "(Vimshottari Jupiter–Mercury, score 0.83; dasha sandhi: confidence capped at moderate; "
                    "cut by the start or end of the range asked about).")
    assert timing_line("career", [], None) is None


def test_no_timing_line_for_a_question_without_when(tmp_path):
    out = tmp_path / "plain"
    args = [x if x != QUESTION else "How will my career go?" for x in BIRTH]
    with pytest.raises(SystemExit) as e:
        main(["read", *args, "--out", str(out), "--model-fixture", str(FIXTURES / "narration_career_edited.json")])
    assert e.value.code == 0
    reading = Reading(**json.loads(out.with_suffix(".json").read_text()))
    assert reading.summary.timing_line is None and "When (engine)" not in out.with_suffix(".md").read_text()


def test_page_derives_the_timing_line_for_an_older_reading(page):
    # A reading JSON written before summary.timing_line existed renders the same line.
    from jyotish.page import render
    from jyotish.uncertainty import assess
    reading, md = page
    old = reading.model_copy(update={"summary": reading.summary.model_copy(update={"timing_line": None})})
    chart = assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)
    assert render(old, chart) == md


def test_learner_names_the_planet_of_a_pair_modifier(page):
    _, md = page
    budh = md[md.index("`yoga.budhaditya@lagna`", md.index("## Learner")):]
    assert "| avastha in [bala, mrita] (Mercury) | ×0.9 | applied |" in budh
    assert "| combust (Mercury) | ×0.5 | not applied |" in budh


def test_every_claim_carries_its_learner_block(page):
    # The website renders the learner panel from the reading JSON alone (SPEC Phase 4, item 5).
    reading, _ = page
    claims = [c for a in reading.areas for c in a.claims]
    assert claims and all(c.learner and c.learner["kind"] == c.kind for c in claims)
    ruchaka = next(c for c in claims if c.finding_id == "yoga.ruchaka@lagna+sun").learner
    assert ruchaka["sudarshana_bases"] == ["sun"] and [f["basis"] for f in ruchaka["fires"]] == ["lagna", "sun"]
    assert {"modifier": "marana_karaka_sthana", "scale": 0.6,
            "applied": {"lagna": "applied", "sun": "applied"}} in ruchaka["modifiers"]
    house = next(c for c in claims if c.finding_id == "vote:career.house").learner
    assert house["direction"] == "for" and house["derivation"][0]["basis"] == "lagna"


def test_upgrade_adds_only_engine_fields_to_an_old_reading(page):
    from jyotish.narrate import upgrade_reading
    from jyotish.uncertainty import assess
    reading, _ = page
    old = reading.model_copy(update={
        "summary": reading.summary.model_copy(update={"timing_line": None}),
        "areas": [a.model_copy(update={"claims": [c.model_copy(update={"learner": None}) for c in a.claims]})
                  for a in reading.areas]})
    chart = assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)
    assert upgrade_reading(old, chart) == reading


def test_example_reading_is_current():
    # examples/reference_reading.json (the live sixth reading) carries the learner blocks and
    # the timing line the website renders.
    ex = Reading(**json.loads((Path(__file__).parents[1] / "examples" / "reference_reading.json").read_text()))
    assert ex.summary.timing_line == TIMING_LINE
    assert all(c.learner for a in ex.areas for c in a.claims) and ex.unchecked_sentences == 0



def test_cli_refuses_null_island(tmp_path, capsys):
    args = [x for x in BIRTH]
    args[args.index("--lat") + 1] = "0"
    args[args.index("--lon") + 1] = "0"
    with pytest.raises(SystemExit) as e:
        main(["read", *args, "--out", str(tmp_path / "x"), "--model-fixture", str(FIXTURES / "narration_career_edited.json")])
    assert e.value.code == 2 and "Gulf of Guinea" in capsys.readouterr().err
    assert not (tmp_path / "x.json").exists()


def test_curious_page_puts_the_paragraph_first_and_the_claims_behind_a_toggle(tmp_path):
    out = tmp_path / "curious"
    args = [x for x in BIRTH]
    args[args.index("--depth") + 1] = "curious"
    with pytest.raises(SystemExit) as e:
        main(["read", *args, "--out", str(out), "--model-fixture", str(FIXTURES / "narration_curious_handwritten.json")])
    assert e.value.code == 0
    reading = Reading(**json.loads(out.with_suffix(".json").read_text()))
    assert reading.depth == "curious" and reading.chart["depth"] == "curious" and "--depth curious" in reading.chart["command"]
    md = out.with_suffix(".md").read_text()
    career = md[md.index("## Career"):md.index("## Marriage")]
    assert career.index("Two combinations sit in your house of work") < career.index("<details><summary>Show the astrologer's reading")
    assert career.index("<details>") < career.index("1. ") < career.index("</details>")
    assert "*These are periods the engine scores as favourable for career; it does not predict when you will act.*" in md
