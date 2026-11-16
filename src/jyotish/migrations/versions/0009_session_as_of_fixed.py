"""A conversation's date fixed by a reviewer, or the server's today for every turn (SPEC Layer 8 rev 136, built
2026-11-16): `sessions.as_of_fixed`. A conversation begun before it is a client's, read at the day of each turn.

Revision ID: 0009
Revises: 0008
Created: 2026-11-16"""

from alembic import op
import sqlalchemy as sa

revision = '0009'
down_revision = '0008'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('sessions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('as_of_fixed', sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    with op.batch_alter_table('sessions', schema=None) as batch_op:
        batch_op.drop_column('as_of_fixed')
