"""A review row may be on a conversation's turn (SPEC Layer 8, 2026-11-01): `turn_id`, and `reading_id` nullable.

Revision ID: 0005
Revises: 0004
Created: 2026-11-01"""

from alembic import op
import sqlalchemy as sa

revision = '0005'
down_revision = '0004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('reviews', schema=None) as batch_op:
        batch_op.add_column(sa.Column('turn_id', sa.String(length=32), nullable=True))
        batch_op.alter_column('reading_id', existing_type=sa.String(length=32), nullable=True)
        batch_op.create_foreign_key('fk_reviews_turn_id_turns', 'turns', ['turn_id'], ['id'])


def downgrade() -> None:
    with op.batch_alter_table('reviews', schema=None) as batch_op:
        batch_op.drop_constraint('fk_reviews_turn_id_turns', type_='foreignkey')
        batch_op.alter_column('reading_id', existing_type=sa.String(length=32), nullable=False)
        batch_op.drop_column('turn_id')
