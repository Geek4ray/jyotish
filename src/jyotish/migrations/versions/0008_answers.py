"""Stored composed answers (SPEC Layer 8, "The layered answer", 2026-11-15): `answers`, keyed by the chart, the routed
question and the bank version, with the birth key an erasure removes them by.

Revision ID: 0008
Revises: 0007
Created: 2026-11-15"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0008'
down_revision = '0007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    doc = sa.JSON().with_variant(postgresql.JSONB(), "postgresql")
    op.create_table(
        'answers',
        sa.Column('key', sa.String(length=64), nullable=False),
        sa.Column('birth_key', sa.String(length=64), nullable=True),
        sa.Column('bank_version', sa.String(length=16), nullable=False),
        sa.Column('document', doc, nullable=False),
        sa.Column('hits', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('key'),
    )
    with op.batch_alter_table('answers', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_answers_birth_key'), ['birth_key'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('answers', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_answers_birth_key'))
    op.drop_table('answers')
