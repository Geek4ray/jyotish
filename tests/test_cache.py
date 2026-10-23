"""jyotish.cache: assess results cached by birth data, conventions, seed and engine."""

import json
import time

import pytest

from jyotish import cache
from jyotish.models import Chart
from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON

KW = dict(time_accuracy="exact", tz="Asia/Kolkata", true_node=False, seed=0)


@pytest.fixture
def disk(tmp_path, monkeypatch):
    monkeypatch.setenv("JYOTISH_CACHE_DIR", str(tmp_path))
    monkeypatch.delenv("JYOTISH_CACHE", raising=False)
    cache.clear_memory()
    yield tmp_path
    cache.clear_memory()


def test_second_run_skips_the_assess(disk):
    t = time.perf_counter()
    first, src1 = cache.cached_assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, **KW)
    cold = time.perf_counter() - t
    t = time.perf_counter()
    again, src2 = cache.cached_assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, **KW)
    warm = time.perf_counter() - t
    assert (src1, src2) == ("computed", "memory") and warm < cold / 5
    assert again.model_dump() == first.model_dump() and again is not first
    # A new process finds it on disk, identical to the computed chart.
    cache.clear_memory()
    disk_copy, src3 = cache.cached_assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, **KW)
    assert src3 == "disk" and disk_copy.model_dump() == first.model_dump()
    assert len(list(disk.glob("*.json"))) == 1


def test_key_covers_birth_data_conventions_seed_and_engine(disk, monkeypatch):
    k = cache.chart_key(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, **KW)
    assert k != cache.chart_key(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, **dict(KW, seed=1))
    assert k != cache.chart_key(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, **dict(KW, true_node=True))
    assert k != cache.chart_key(REFERENCE_BIRTH_UTC, REFERENCE_LAT + 1e-4, REFERENCE_LON, **KW)
    assert k != cache.chart_key(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, **dict(KW, time_accuracy="within_15"))
    monkeypatch.setattr(cache, "engine_hash", lambda: "another engine")
    assert k != cache.chart_key(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, **KW)


def test_caller_cannot_change_the_cache_and_off_switch(disk, monkeypatch):
    a, _ = cache.cached_assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, **KW)
    a.scored.areas["career"].tier = "changed"
    b, _ = cache.cached_assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, **KW)
    assert b.scored.areas["career"].tier == "moderate"
    monkeypatch.setenv("JYOTISH_CACHE", "off")
    cache.clear_memory()
    for f in disk.glob("*.json"):
        f.unlink()
    _, src = cache.cached_assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, **KW)
    assert src == "computed" and not list(disk.glob("*.json"))


def test_two_jobs_computing_one_chart_at_once_both_succeed(tmp_path, monkeypatch):
    """Two workers computing the same uncached chart (a comparison posts two readings of one chart)
    each write their own temporary file: neither finds the other's moved away."""
    import threading
    monkeypatch.setenv("JYOTISH_CACHE_DIR", str(tmp_path))
    cache.clear_memory()
    errors = []

    def job():
        try:
            cache.cached_assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)
        except Exception as e:          # the failure this guards against: FileNotFoundError on replace
            errors.append(repr(e))
    threads = [threading.Thread(target=job) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert errors == [] and [p.suffix for p in tmp_path.iterdir()] == [".json"]
    cache.clear_memory()
