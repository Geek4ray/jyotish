"""The conversation (SPEC Layer 8, 2026-11-01): sessions and their turns, and the ledger keyed by a reading's or a
turn's id (its foreign key to readings dropped, a `kind` column added).

Revision ID: 0004
Revises: 0003
Created: 2026-11-01"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

DOCUMENT = sa.JSON().with_variant(postgresql.JSONB(), "postgresql")

revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None

# SQLite names no foreign key; batch mode recreates the table, and this convention names the one it drops.
NAMING = {"fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s"}


def upgrade() -> None:
    op.create_table('sessions',
    sa.Column('id', sa.String(length=32), nullable=False),
    sa.Column('chart_id', sa.String(length=64), nullable=True),
    sa.Column('birth_key', sa.String(length=64), nullable=True),
    sa.Column('birth', DOCUMENT, nullable=False),
    sa.Column('as_of', sa.String(length=10), nullable=False),
    sa.Column('check', DOCUMENT, nullable=True),
    sa.Column('minor', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['chart_id'], ['charts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('turns',
    sa.Column('id', sa.String(length=32), nullable=False),
    sa.Column('session_id', sa.String(length=32), nullable=False),
    sa.Column('n', sa.Integer(), nullable=False),
    sa.Column('birth_key', sa.String(length=64), nullable=True),
    sa.Column('question', sa.Text(), nullable=False),
    sa.Column('status', sa.String(length=16), nullable=False),
    sa.Column('route', DOCUMENT, nullable=True),
    sa.Column('document', DOCUMENT, nullable=True),
    sa.Column('error', DOCUMENT, nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('session_id', 'n')
    )
    if op.get_bind().dialect.name == "sqlite":
        with op.batch_alter_table('ledger', naming_convention=NAMING) as batch_op:
            batch_op.drop_constraint('fk_ledger_reading_id_readings', type_='foreignkey')
            batch_op.add_column(sa.Column('kind', sa.String(length=8), server_default='reading', nullable=False))
    else:
        op.drop_constraint('ledger_reading_id_fkey', 'ledger', type_='foreignkey')
        op.add_column('ledger', sa.Column('kind', sa.String(length=8), server_default='reading', nullable=False))


def downgrade() -> None:
    with op.batch_alter_table('ledger', schema=None) as batch_op:
        batch_op.drop_column('kind')
        batch_op.create_foreign_key('ledger_reading_id_fkey', 'readings', ['reading_id'], ['id'])
    op.drop_table('turns')
    op.drop_table('sessions')
