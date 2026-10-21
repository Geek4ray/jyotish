"""Suite-wide: the chart cache (jyotish.cache) writes to a temporary directory, never to the
user's ~/.cache."""

import pytest


@pytest.fixture(autouse=True, scope="session")
def _chart_cache_dir(tmp_path_factory):
    mp = pytest.MonkeyPatch()
    mp.setenv("JYOTISH_CACHE_DIR", str(tmp_path_factory.mktemp("chart-cache")))
    yield
    mp.undo()
