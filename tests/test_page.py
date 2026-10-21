"""The page renderer over every derivation shape the engine produces, and `jyotish page`
(re-render a reading's Markdown from its JSON, no model call)."""

import json
from datetime import date

import pytest

from jyotish.cli import main
from jyotish.narrate import Reading, ReadingClaim, ReadingDraft, findings, narrate
from jyotish.page import derivation_table, render
from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
from jyotish.scoring import AREAS
from jyotish.uncertainty import assess

FAMILIES = ("house", "lord", "karaka", "varga", "arudha", "kp", "panchanga")


@pytest.fixture(scope="module")
def chart():
    return assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)


def test_every_derivation_of_every_family_renders(chart):
    """All 18 areas x all seven families, voting or abstaining: no derivation shape untested."""
    shapes = set()
    for area in AREAS:
        details = chart.scored.areas[area].vote_details
        assert set(details) == set(FAMILIES), area
        for family, d in details.items():
            lines = derivation_table(d)
            assert lines and not any("Traceback" in x for x in lines)
            if isinstance(d, list):
                shapes.add("rows")
                if d:
                    assert lines[0].startswith("| ") and len(lines) == len(d) + 2, (area, family)
            else:
                shapes.add("named rows:" + ",".join(d))
                for key, rows in d.items():
                    assert f"{key.replace('_', ' ')}:" in lines, (area, family, key)
                    if rows:
                        cols = "| " + " | ".join(k.replace("_", " ") for k in dict.fromkeys(
                            k for r in rows for k in r)) + " |"
                        assert cols in lines, (area, family, key)
    assert shapes == {"rows", "named rows:padas", "named rows:marana_karaka_sthana"}
    padas = derivation_table(chart.scored.areas["marriage"].vote_details["arudha"])
    assert "| pada | basis | house | sign | occupants | benefics |" in padas
    assert "| UL | lagna | 2 | Gemini | Rahu | – |" in padas


def test_full_page_with_a_claim_for_every_finding_in_every_area(chart):
    """The whole renderer, learner section included, over every finding the engine offers in
    all 18 areas (claims stand in for the model's sentences; the page renders their tags)."""
    blank = ReadingDraft(summary="Overview.", areas=[])
    reading = narrate(chart, "Tell me about my chart", drafter=lambda *_: blank, checker=lambda *_: None,
                      as_of=date(2026, 10, 21), areas=list(AREAS))
    areas = []
    for a in reading.areas:
        ok, shaky = findings(chart, a.name)
        claims = [ReadingClaim(finding_id=f["finding_id"], text=f"Finding {f['finding_id']} [{f['allowed_tags'][0]}].",
                               cites=[f["allowed_tags"][0]], kind=f["kind"], school=f["school"], basis=f["basis"],
                               stability=f["stability"], confidence=f["confidence"]) for f in ok + shaky]
        areas.append(a.model_copy(update={"claims": claims}))
    n = sum(len(a.claims) for a in areas)
    assert n > 18 * 5
    md = render(reading.model_copy(update={"areas": areas}), chart)
    assert md.count("\n### ") == n
    assert md.count("pada | basis | house | sign | occupants | benefics") >= 1
    assert "marana karaka sthana:" in md                       # longevity's arudha shape


BIRTH = ["--date", "2001-03-12", "--time", "10:10:25", "--tz", "Asia/Kolkata", "--lat", str(REFERENCE_LAT),
         "--lon", str(REFERENCE_LON), "--node", "mean", "--place", "Rewari, Haryana"]


def _cli(args):
    with pytest.raises(SystemExit) as e:
        main(args)
    return e.value.code


def test_page_command_rerenders_without_the_model(tmp_path, capsys):
    from pathlib import Path
    out = tmp_path / "reading"
    fixture = Path(__file__).parent / "fixtures" / "narration_career_edited.json"
    assert _cli(["read", *BIRTH, "--depth", "astrologer",
                 "--question", "How will my career go, and when is the best time for a job change?",
                 "--as-of", "2026-10-21", "--out", str(out), "--model-fixture", str(fixture)]) == 0
    first = out.with_suffix(".md").read_text()
    again = tmp_path / "again.md"
    assert _cli(["page", "--from", str(out.with_suffix(".json")), *BIRTH, "--out", str(again)]) == 0
    assert again.read_text() == first                         # the same page, from the JSON alone
    # Flags that do not reproduce the reading's chart are refused, naming what differs.
    capsys.readouterr()
    wrong = [x if x != "mean" else "true" for x in BIRTH]
    assert _cli(["page", "--from", str(out.with_suffix(".json")), *wrong, "--out", str(tmp_path / "x.md")]) == 2
    assert "conventions" in capsys.readouterr().err and not (tmp_path / "x.md").exists()
