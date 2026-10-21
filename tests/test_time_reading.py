"""scripts/time_reading.py, offline: the model calls are replayed, and a failed narration still
prints every attempt's errors and writes the full recording."""

import importlib.util
import json
from pathlib import Path

import pytest

import jyotish.narrate as narrate_mod

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"


@pytest.fixture
def script(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location("time_reading", ROOT / "scripts" / "time_reading.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    monkeypatch.setattr(mod, "LAST", tmp_path / "last_recording.json")
    monkeypatch.setattr(mod, "OUT", tmp_path / "timings.jsonl")
    return mod


def replay(monkeypatch, fixture, *, reject=None, raise_on_writer=None):
    rec = json.loads((FIXTURES / fixture).read_text())

    class Drafter(narrate_mod.FixtureDrafter):
        def __init__(self, cfg):
            super().__init__(rec)

        def __call__(self, system, user, errors):
            if raise_on_writer and self.calls + 1 == raise_on_writer:
                raise RuntimeError("API error: overloaded")
            return super().__call__(system, user, errors)

    class Checker(narrate_mod.FixtureChecker):
        def __init__(self, cfg):
            super().__init__(rec)

        def __call__(self, sentence, derivation):
            if reject and reject in sentence:
                return narrate_mod.CheckResult(propositions=[narrate_mod.Proposition(
                    text="a word the data does not state", supported=False, evidence="not in the derivation")])
            return super().__call__(sentence, derivation)
    monkeypatch.setattr(narrate_mod, "AnthropicDrafter", Drafter)
    monkeypatch.setattr(narrate_mod, "AnthropicChecker", Checker)


def test_failed_run_prints_every_error_and_keeps_the_recording(script, monkeypatch, capsys):
    replay(monkeypatch, "narration_career_opus55_r1.json")          # fails the validator three times
    out = script.live(sequential=True)
    text = capsys.readouterr().out
    assert out["accepted"] is False and out["error"] == "NarrationError" and out["attempts"] == 3
    for n in (1, 2, 3):
        assert f"attempt {n}: writer" in text
    assert "validator: unknown finding id 'yoga.ruchaka@lagna'" in text
    assert "narration failed: NarrationError" in text and "written to" in text
    saved = json.loads(script.LAST.read_text())
    assert saved["accepted"] is False and len(saved["drafts"]) == 3 and saved["question"] == script.QUESTION
    assert saved["error"]["type"] == "NarrationError" and saved["error"]["errors"]
    assert [c["kind"] for c in saved["calls"]] == ["writer"] * 3     # the validator failed: no checks ran


def test_checker_rejections_are_printed_per_attempt(script, monkeypatch, capsys):
    replay(monkeypatch, "narration_career_edited.json", reject="The varga vote")
    out = script.live(sequential=True)
    text = capsys.readouterr().out
    assert out["accepted"] is False
    assert "checker rejected vote:career.varga (attempt 1): The varga vote" in text
    assert "unsupported: a word the data does not state" in text and "evidence: not in the derivation" in text
    assert "attempt 3: " in text and " rejected" in text
    saved = json.loads(script.LAST.read_text())
    assert sum(c["kind"] == "checker" for c in saved["calls"]) == 3 * (2 + 8)   # every claim, every attempt


def test_accepted_run_and_api_error_both_write_the_recording(script, monkeypatch, capsys):
    replay(monkeypatch, "narration_career_edited.json")
    assert script.live(sequential=False)["accepted"] is True
    assert json.loads(script.LAST.read_text())["accepted"] is True
    replay(monkeypatch, "narration_career_opus55_r1.json", raise_on_writer=2)
    out = script.live(sequential=True)
    assert out["error"] == "RuntimeError" and "overloaded" in capsys.readouterr().out
    saved = json.loads(script.LAST.read_text())
    assert saved["error"]["type"] == "RuntimeError" and len(saved["drafts"]) == 1


def test_payload_is_the_same_in_every_process():
    """The writer's and checker's input does not depend on the interpreter's hash seed (the
    varga rows used to follow a set's iteration order)."""
    import subprocess
    import sys
    code = ("from jyotish.chart import compute; from jyotish.narrate import payload, findings, _check_payload;"
            "from jyotish.reference import *; import hashlib;"
            "c = compute(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False);"
            "areas = ['career', 'marriage', 'longevity'];"
            "u, _ = payload(c, 'q', areas);"
            "d = ''.join(_check_payload(f) for a in areas for f in findings(c, a)[0]);"
            "print(hashlib.sha256((u + d).encode()).hexdigest())")
    seen = {subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True,
                           env={"PYTHONHASHSEED": str(h), "PATH": "", "JYOTISH_CACHE": "off"}).stdout
            for h in (1, 2, 3)}
    assert len(seen) == 1
