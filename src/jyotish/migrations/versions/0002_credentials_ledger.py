"""Reviewers', clerks' and the owner's tokens (their hashes) and the per-reading cost ledger.

Revision ID: 0002
Revises: 0001
Created: 2026-10-23"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

DOCUMENT = sa.JSON().with_variant(postgresql.JSONB(), "postgresql")

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('credentials',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('kind', sa.String(length=16), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('token_hash', sa.String(length=64), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('token_hash')
    )
    op.create_table('ledger',
    sa.Column('reading_id', sa.String(length=32), nullable=False),
    sa.Column('day', sa.String(length=10), nullable=False),
    sa.Column('writer_model', sa.String(length=64), nullable=True),
    sa.Column('checker_model', sa.String(length=64), nullable=True),
    sa.Column('depth', sa.String(length=16), nullable=True),
    sa.Column('writer_tokens', DOCUMENT, nullable=False),
    sa.Column('checker_tokens', DOCUMENT, nullable=False),
    sa.Column('writer_calls', sa.Integer(), nullable=False),
    sa.Column('checker_calls', sa.Integer(), nullable=False),
    sa.Column('cost_usd', sa.Float(), nullable=True),
    sa.Column('seconds', sa.Float(), nullable=True),
    sa.Column('replayed', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['reading_id'], ['readings.id'], ),
    sa.PrimaryKeyConstraint('reading_id')
    )
    with op.batch_alter_table('ledger', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_ledger_day'), ['day'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('ledger', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_ledger_day'))

    op.drop_table('ledger')
    op.drop_table('credentials')
