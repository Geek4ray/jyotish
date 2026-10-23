"""Suite-wide: the chart cache (jyotish.cache) and the candidate rules (service.record_candidates)
write to temporary files, never to the user's ~/.cache or the repository's data/."""

import pytest


@pytest.fixture(autouse=True, scope="session")
def _chart_cache_dir(tmp_path_factory):
    mp = pytest.MonkeyPatch()
    mp.setenv("JYOTISH_CACHE_DIR", str(tmp_path_factory.mktemp("chart-cache")))
    # Candidate rules (the [tradition:] sentences of a live reading) go to a temporary file too.
    mp.setenv("JYOTISH_CANDIDATE_RULES", str(tmp_path_factory.mktemp("candidates") / "candidate_rules.jsonl"))
    yield
    mp.undo()
