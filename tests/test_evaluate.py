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
    return {"numbers": {k: {"value": x[0], "better": x[1], "unit": "", **({"gate": x[2]} if len(x) > 2 else {})}
                        for k, x in numbers.items()}}


def test_worse_is_by_direction_and_skips_are_not_worse():
    ev = _ev()
    old = card(a=(1.0, "higher"), b=(0.0, "lower"), c=(5, None), d=(0.0001336, "lower"))
    # A sampled statistic the committed scorecard marks ungated is never worse, whatever its direction.
    noisy = card(e=(0.9, "higher", False))
    assert ev.compare(card(e=(0.1, "higher", False)), noisy) == [] and ev.compare(card(e=(0.1, "higher")), noisy) == []
    assert ev.compare(card(e=(0.1, "higher")), card(e=(0.9, "higher", True))) == ["e: 0.9 -> 0.1 (higher is better)"]
    c = ev.Card()
    c.num("x", 1, "higher"); c.num("y", 1, None); c.num("z", 1, "lower", gate=False)
    assert [v["gate"] for v in c.numbers.values()] == [True, False, False]
    assert ev.compare(card(a=(1.0, "higher"), b=(0.0, "lower"), c=(9, None), d=(0.0001336, "lower")), old) == []
    assert ev.compare(card(a=(0.99, "higher"), b=(0.0, "lower"), c=(5, None), d=(0.0001336, "lower")), old) == \
        ["a: 1.0 -> 0.99 (higher is better)"]
    assert ev.compare(card(a=(1.0, "higher"), b=(1, "lower"), c=(5, None), d=(0.0002, "lower")), old)[0].startswith("b:")
    assert ev.compare(card(b=(0.0, "lower")), old) == []                    # the others not measured: skipped
    assert ev.compare(card(d=(0.0001336 + 1e-12, "lower")), old) == []      # float noise is not a change


def test_the_committed_scorecard_has_every_number_with_a_direction_and_gates_only_verdicts():
    data = json.loads((ROOT / "docs" / "scorecard.json").read_text())
    nums = data["numbers"]
    assert data["commit"] and data["date"]
    for prefix in ("reference.", "metamorphic.", "checker.validator.", "placements.", "synthetic."):
        assert any(k.startswith(prefix) for k in nums), prefix
    assert all(v["better"] in ("higher", "lower", None) and isinstance(v["gate"], bool) for v in nums.values())
    assert nums["reference.failed"]["value"] == 0 and nums["placements.files_differing_from_table"]["value"] == 0
    # Sampled statistics are not gated; the verdicts and the 20,000-run checks are.
    sampled = [k for k in nums if k.startswith("metamorphic.seed_agreement.")
               or k in ("checker.validator.precision", "checker.validator.recall", "checker.validator.f1")
               or (k.startswith("synthetic.") and not k.endswith(("pipeline_recovers", "pipeline_quiet")))]
    assert sampled and all(nums[k]["gate"] is False for k in sampled)
    for k in ("reference.failed", "reference.passed", "metamorphic.failed", "checker.validator.false_rejects",
              "checker.validator.wording_caught_share", "placements.files_differing_from_table",
              "synthetic.planted.20000.pipeline_recovers", "synthetic.null.20000.pipeline_quiet"):
        assert nums[k]["gate"] is True, k
    assert nums["synthetic.planted.20000.pipeline_recovers"]["value"] == 1 and nums["synthetic.null.20000.pipeline_quiet"]["value"] == 1
    assert all(v["gate"] is False for k, v in nums.items() if v["better"] is None)
    assert "checker.live.recall" in nums and nums["checker.live.recall"]["better"] is None   # the last live run, reported
    md = (ROOT / "docs" / "scorecard.md").read_text()
    assert "## Skips and what is blocked" in md and "## Every number" in md and "gates CI" in md
    assert "no Anthropic credentials here" not in md and "live run on record" in md


def test_ci_runs_the_suite_and_the_gate_as_two_jobs_with_the_crosscheck_install_apart():
    # Two jobs since 2026-11-10: pytest (44 to 54 minutes on the runners) and the harness (about 20) outgrew one
    # job's 75 minutes, and the harness runs its own tests, so neither waits on the other.
    import yaml
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text()
    jobs = yaml.safe_load(ci)["jobs"]                                            # valid YAML, and its jobs
    assert "on: push" in ci
    test, evaluate = jobs["test"], jobs["evaluate"]
    assert [s["run"] for s in test["steps"] if s.get("name") == "pytest"] == [".venv/bin/pytest -q"]
    gate = [s["run"] for s in evaluate["steps"] if "scripts/evaluate.py" in s.get("run", "")]
    assert len(gate) == 1 and "--compare docs/scorecard.json" in gate[0]
    assert not [s for s in test["steps"] if "scripts/evaluate.py" in s.get("run", "")]
    assert "needs" not in evaluate                                               # side by side, not in turn
    for job in (test, evaluate):
        steps = job["steps"]
        apart = [s for s in steps if "[crosscheck]" in s.get("run", "")]
        assert len(apart) == 1 and apart[0]["continue-on-error"] is True          # its own step, allowed to fail
        assert 30 <= job["timeout-minutes"] <= 120                               # a cap on a hang
        assert job["runs-on"] != "ubuntu-latest" and job["runs-on"].startswith("ubuntu-")   # pinned: a stable cache key
        setup = next(s for s in steps if "setup-python" in s.get("uses", ""))
        assert setup["with"]["cache"] == "pip" and setup["with"]["cache-dependency-path"] == "pyproject.toml"
    assert test["timeout-minutes"] >= 60 and "postgres" in test["services"]
    browser = next(s for s in test["steps"] if "actions/cache" in s.get("uses", ""))
    assert "ms-playwright" in browser["with"]["path"] and "pyproject.toml" in browser["with"]["key"]
    kept = next(s for s in evaluate["steps"] if "upload-artifact" in s.get("uses", ""))
    assert kept["if"] == "always()" and "scorecard" in kept["with"]["path"]


def test_the_paragraph_policy_is_counted_from_the_latest_curious_comparison():
    # Review Q11 (DoD 4): the paragraph held sentence by sentence has its own numbers, reported and never gated.
    ev = _ev()
    card = ev.Card()
    ev.paragraph_policy(card)
    nums = card.numbers
    ends = [nums[f"paragraph.{k}"]["value"] for k in ("complete", "partial", "none")]
    assert sum(ends) >= 6 and not any(nums[k]["gate"] for k in nums if k.startswith("paragraph."))
    assert "paragraph.ended_early" in nums and "paragraph.writer_rounds_mean" in nums
    assert any(k.startswith("paragraph.sentences_held_attempt_") for k in nums)
