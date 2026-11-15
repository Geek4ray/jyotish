"""The astrologer's verdicts on the sentence bank's rows (SPEC Layer 8, "The layered answer", 2026-11-15):
`bank_reviews`.

Revision ID: 0007
Revises: 0006
Created: 2026-11-15"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0007'
down_revision = '0006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    doc = sa.JSON().with_variant(postgresql.JSONB(), "postgresql")
    op.create_table(
        'bank_reviews',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('signature', sa.String(length=200), nullable=False),
        sa.Column('kind', sa.String(length=8), nullable=True),
        sa.Column('variant', sa.Integer(), nullable=True),
        sa.Column('bank_version', sa.String(length=16), nullable=True),
        sa.Column('verdict', sa.String(length=8), nullable=False),
        sa.Column('words', sa.Text(), nullable=True),
        sa.Column('sentence', sa.Text(), nullable=False),
        sa.Column('slots', doc, nullable=True),
        sa.Column('turn_id', sa.String(length=32), nullable=True),
        sa.Column('reviewer_id', sa.String(length=64), nullable=False),
        sa.Column('applied_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['turn_id'], ['turns.id'], name='fk_bank_reviews_turn_id_turns'),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('bank_reviews', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_bank_reviews_signature'), ['signature'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('bank_reviews', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_bank_reviews_signature'))
    op.drop_table('bank_reviews')
