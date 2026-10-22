"""The Phase 0 cross-check against PyJHora (scripts/crosscheck.py), on a seeded sample. Skips when
PyJHora (the dev-only "crosscheck" extra) is not installed. PyJHora is imported here and in the
script only, never by src/."""

import importlib.util
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.crosscheck
pytest.importorskip("jhora", reason="PyJHora is not installed: pip install -e '.[crosscheck]'")

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def xc():
    spec = importlib.util.spec_from_file_location("crosscheck", ROOT / "scripts" / "crosscheck.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["crosscheck"] = mod                     # dataclasses look their module up here
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def sample(xc):
    return xc.run(60, seed=11)


def test_the_engine_matches_pyjhora_within_the_gate(xc, sample):
    r, j, births = sample
    assert r.n == 60 and not r.failed, r.failed[:5]
    s = xc.summary(r)
    assert all(mx <= 1.0 for q, (mx, _) in s.items() if q.startswith("longitude")), s
    assert s["mahadasha start (days)"][0] <= 1.0
    assert {f"longitude {p}" for p in xc.BODIES} <= set(s)


def test_pyjhora_is_set_to_the_engines_conventions(sample):
    _, j, _ = sample
    import swisseph as swe
    assert j.const._RAHU == swe.MEAN_NODE and j.vimsottari.year_duration == 365.25
    assert not j.drik.PLANET_FLAGS & swe.FLG_TRUEPOS and not j.drik.PLANET_FLAGS & swe.FLG_NONUT
    assert j.defaults["ayanamsa"] and "dasha_year" in j.defaults               # its own defaults, for the report


def test_the_check_catches_a_convention_difference(xc, sample):
    # A negative control: PyJHora on the true node must fail the gate on Rahu and Ketu.
    _, j, births = sample
    ours = [xc.engine_side(b) for b in births[:10]]
    j.const.set_node_mode(True)
    try:
        theirs = [xc.pyjhora_side(j, b) for b in births[:10]]
    finally:
        j.const.set_node_mode(False)
    r = xc.compare(births[:10], ours, theirs)
    assert r.failed and all(("Rahu" in x or "Ketu" in x) for x in r.failed)


def test_edges_are_listed_not_failed(xc):
    assert xc.edge_distance(30.0 + 10 / 3, 9) < 1e-6                         # a navamsa edge
    assert xc.edge_distance(5.0, 30) < 1e-6 and xc.edge_distance(30 + 12.0, 30) < 1e-6   # odd and even trimsamsa
    assert xc.edge_distance(30 + 5.0 + 2 / 3600, 30) == pytest.approx(2.0)
    assert xc.edge_distance(10 / 3 + 0.5 / 3600, 108) == pytest.approx(0.5)


def test_src_never_imports_pyjhora():
    for path in (ROOT / "src").rglob("*.py"):
        text = path.read_text()
        assert "jhora" not in text, path
    assert "jhora" not in sys.modules or all("jyotish" not in m for m in sys.modules if m.startswith("jhora"))
