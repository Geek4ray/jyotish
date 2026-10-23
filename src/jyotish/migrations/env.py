"""Alembic's environment for the service's database (jyotish.db.migrate runs it). The connection is
the caller's when one is handed over (`config.attributes["connection"]`), else JYOTISH_DATABASE_URL.
SQLite alters tables in batch mode (it cannot drop or change a column in place)."""

from alembic import context

from jyotish.db import Base, engine_for

config = context.config
target_metadata = Base.metadata


def run(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata,
                      render_as_batch=connection.dialect.name == "sqlite", compare_type=True)
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    context.configure(url=config.get_main_option("sqlalchemy.url"), target_metadata=target_metadata,
                      literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
elif config.attributes.get("connection") is not None:
    run(config.attributes["connection"])
else:
    with engine_for().connect() as conn:
        run(conn)
        conn.commit()
