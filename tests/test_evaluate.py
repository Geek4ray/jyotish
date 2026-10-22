"""The evaluation harness's gate (scripts/evaluate.py): what counts as worse, and the CI workflow."""

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _ev():
    spec = importlib.util.spec_from_file_location("evaluate", ROOT / "scripts" / "evaluate.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["evaluate"] = mod
    spec.loader.exec_module(mod)
    return mod


def card(**numbers):
    return {"numbers": {k: {"value": v, "better": b, "unit": ""} for k, (v, b) in numbers.items()}}


def test_worse_is_by_direction_and_skips_are_not_worse():
    ev = _ev()
    old = card(a=(1.0, "higher"), b=(0.0, "lower"), c=(5, None), d=(0.0001336, "lower"))
    assert ev.compare(card(a=(1.0, "higher"), b=(0.0, "lower"), c=(9, None), d=(0.0001336, "lower")), old) == []
    assert ev.compare(card(a=(0.99, "higher"), b=(0.0, "lower"), c=(5, None), d=(0.0001336, "lower")), old) == \
        ["a: 1.0 -> 0.99 (higher is better)"]
    assert ev.compare(card(a=(1.0, "higher"), b=(1, "lower"), c=(5, None), d=(0.0002, "lower")), old)[0].startswith("b:")
    assert ev.compare(card(b=(0.0, "lower")), old) == []                    # the others not measured: skipped
    assert ev.compare(card(d=(0.0001336 + 1e-12, "lower")), old) == []      # float noise is not a change


def test_the_committed_scorecard_has_every_number_with_a_direction():
    data = json.loads((ROOT / "docs" / "scorecard.json").read_text())
    nums = data["numbers"]
    assert data["commit"] and data["date"]
    for prefix in ("reference.", "metamorphic.", "checker.validator.", "placements."):
        assert any(k.startswith(prefix) for k in nums), prefix
    assert all(v["better"] in ("higher", "lower", None) for v in nums.values())
    assert nums["reference.failed"]["value"] == 0 and nums["placements.files_differing_from_table"]["value"] == 0
    md = (ROOT / "docs" / "scorecard.md").read_text()
    assert "## Skips and what is blocked" in md and "## Every number" in md


def test_ci_runs_the_suite_then_the_gate_with_the_crosscheck_install_apart():
    import yaml
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text()
    steps = yaml.safe_load(ci)["jobs"]["test"]["steps"]                        # valid YAML, and its steps
    apart = [s for s in steps if "[crosscheck]" in s.get("run", "")]
    assert len(apart) == 1 and apart[0]["continue-on-error"] is True
    assert "on: push" in ci and ".venv/bin/pytest -q" in ci
    assert "scripts/evaluate.py" in ci and "--compare docs/scorecard.json" in ci
    i = ci.index('pip install -e ".[crosscheck]"')
    assert "continue-on-error: true" in ci[ci.rfind("- name:", 0, i):i]         # its own step, allowed to fail
    assert ci.index("run: .venv/bin/pytest -q") < ci.index("run: .venv/bin/python scripts/evaluate.py")
