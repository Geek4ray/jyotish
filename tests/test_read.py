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
         "--lon", str(REFERENCE_LON), "--node", "mean", "--question", QUESTION, "--as-of", "2026-10-21"]


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
    assert [a.name for a in reading.areas] == ["career", "health", "marriage"]   # asked, then the top three
    assert reading.narration_source.endswith("narration_career_edited.json")
    assert reading.summary.current_period == "Jupiter-Mercury" and reading.summary.time_window_min == 2
    assert all(a.probability is None and not a.calibrated for a in reading.areas)
    assert sorted(reading.disclaimers) == ["health", "third_party"]
    # The edited fixture has no checker calls: every sentence on the page is unchecked, and says so.
    assert reading.unchecked_sentences == 3 + 9


def test_page_sections_in_order(page):
    _, md = page
    heads = ["## Summary", "## Career", "## Health", "## Marriage", "## Depends on exact birth time",
             "## Learner: what each claim rests on", "## Disclaimers"]
    pos = [md.index(h) for h in heads]
    assert pos == sorted(pos)
    assert "12 sentence(s) on this page have no recorded checker verdict" in md
    for field in ("- Driver: Venus", "- Current period (Vimshottari): Jupiter-Mercury", "- Top areas: health, career, marriage",
                  "- Birth-time window: ±2 min", "- Fired rules stable / unstable under that window: 5 / 0",
                  "- Abstained areas: children, father, gains, synastry"):
        assert field in md
    career = md[md.index("## Career"):md.index("## Health")]
    assert "- Stability: time 0.60 · ayanamsa 0.67 · house 0.50 (sensitive)" in career
    assert "- Polarity: intensity (house H10, lord Saturn, karaka Sun)" in career
    assert "the KP family (kp) is against" in career
    assert "| avoid | 2028-11-17 | 2029-08-08 |" in career and "strongest piece" in career


def test_claims_in_engine_order_with_tags_as_footnotes(page):
    reading, md = page
    body, notes = md.split("\n---\n")
    assert not TAG.search(body)                                 # every tag became a footnote
    career = reading.areas[0]
    assert [c.finding_id for c in career.claims][:3] == ["yoga.kendra_trikona_raja@lagna", "yoga.budhaditya@lagna",
                                                          "yoga.ruchaka@lagna+sun"]
    assert career.claims[-1].finding_id == "vote:career.kp"
    first = md.index("1. The Sun and Mercury conjoined in the 10th join")
    assert first < md.index("9. The KP vote is against career")
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
    assert "| 10 | lagna | Moon | Ketu | 8 | – | 10, 6, 2, 11 |" in learner  # KP vote
    assert "Sudarshana" not in learner[:learner.index("`yoga.ruchaka@lagna+sun`")]


def test_frozen_recording_fails_cleanly(tmp_path, capsys):
    # The frozen first recording predates items 8 and 11: its summary names votes it does not
    # cite and mentions timing, and its Ruchaka claims carry the two pre-merge ids. Replayed,
    # it fails the validator on every attempt; nothing is written.
    out = tmp_path / "r1"
    assert run(["--out", str(out), "--model-fixture", str(FIXTURES / "narration_career_opus55_r1.json")]) == 2
    err = capsys.readouterr().err
    assert "unknown finding id 'yoga.ruchaka@lagna'" in err and "timing language" in err
    assert not out.with_suffix(".json").exists() and not out.with_suffix(".md").exists()
