"""The service's database (jyotish.db): Alembic brings a new database to the models' schema with no
drift, adopts a database made by create_all before the migrations existed, and does the same on
Postgres when JYOTISH_TEST_POSTGRES_URL names one (CI runs a Postgres service for it)."""

import os

import pytest
from sqlalchemy import inspect, text
from sqlalchemy.orm import sessionmaker

from jyotish.db import (Base, ComparisonRow, ReadingRow, current_revision, database_url, engine_for, head_revision,
                        migrate)

TABLES = {"charts", "readings", "reviews", "exclusions", "consents", "subjects", "events", "erasures", "comparisons",
          "credentials", "ledger"}


def _drift(engine) -> list:
    from alembic.autogenerate import compare_metadata
    from alembic.migration import MigrationContext
    with engine.connect() as conn:
        return compare_metadata(MigrationContext.configure(conn, opts={"compare_type": True}), Base.metadata)


def _check_fresh(url):
    engine = migrate(url)
    assert current_revision(engine) == head_revision()
    assert TABLES <= set(inspect(engine).get_table_names())
    assert _drift(engine) == []                              # the migrations make exactly the models' schema
    migrate(engine)                                          # a second run changes nothing
    assert current_revision(engine) == head_revision()
    return engine


def test_a_new_sqlite_database_is_migrated_to_the_head_with_no_drift(tmp_path):
    _check_fresh(f"sqlite:///{tmp_path / 'new.db'}")


def test_a_database_made_before_the_migrations_is_adopted(tmp_path):
    """create_all made the tables (no comparisons, no alembic_version); its pairs lived in
    readings.request.compared_with."""
    engine = engine_for(f"sqlite:///{tmp_path / 'old.db'}")
    old = [t for name, t in Base.metadata.tables.items() if name != "comparisons"]
    Base.metadata.create_all(engine, tables=old)
    with engine.begin() as conn:                             # a column added since: gone from the old table
        conn.execute(text("ALTER TABLE reviews DROP COLUMN facts"))
    with sessionmaker(engine).begin() as s:
        for rid, other in (("a" * 32, "b" * 32), ("b" * 32, "a" * 32)):
            s.add(ReadingRow(id=rid, question="q", request={"compared_with": [other]}, status="done", progress={}))
    migrate(engine)
    assert current_revision(engine) == head_revision()
    assert "facts" in {c["name"] for c in inspect(engine).get_columns("reviews")}
    with sessionmaker(engine)() as s:
        rows = s.query(ComparisonRow).all()
        assert [(r.reading_a, r.reading_b) for r in rows] == [("a" * 32, "b" * 32)]
    assert _drift(engine) == []


def test_a_hosts_postgres_url_gets_the_psycopg_driver(monkeypatch):
    assert database_url("postgres://u:p@h:5432/d") == "postgresql+psycopg://u:p@h:5432/d"
    assert database_url("postgresql://u:p@h/d") == "postgresql+psycopg://u:p@h/d"
    assert database_url("sqlite:///x.db") == "sqlite:///x.db"
    monkeypatch.setenv("JYOTISH_DATABASE_URL", "postgres://x/y")
    assert database_url() == "postgresql+psycopg://x/y"


@pytest.mark.skipif(not os.environ.get("JYOTISH_TEST_POSTGRES_URL"), reason="set JYOTISH_TEST_POSTGRES_URL to a scratch Postgres")
def test_postgres_is_migrated_to_the_head_with_no_drift():
    url = os.environ["JYOTISH_TEST_POSTGRES_URL"]
    engine = engine_for(url)
    with engine.begin() as conn:                             # a scratch database: start empty
        conn.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public"))
    engine = _check_fresh(url)
    cols = {c["name"]: c["type"] for c in inspect(engine).get_columns("readings")}
    assert type(cols["document"]).__name__ == "JSONB"
