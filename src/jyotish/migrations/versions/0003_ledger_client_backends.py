"""The ledger keeps the client's layer apart and the three roles' backends (2026-10-25): each role may
run on its own backend and model, and each is priced by its own.

Revision ID: 0003
Revises: 0002
Created: 2026-10-25"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

DOCUMENT = sa.JSON().with_variant(postgresql.JSONB(), "postgresql")

revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('ledger', schema=None) as batch_op:
        batch_op.add_column(sa.Column('client_model', sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column('client_tokens', DOCUMENT, nullable=True))
        batch_op.add_column(sa.Column('client_calls', sa.Integer(), server_default='0', nullable=False))
        batch_op.add_column(sa.Column('backends', DOCUMENT, nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('ledger', schema=None) as batch_op:
        batch_op.drop_column('backends')
        batch_op.drop_column('client_calls')
        batch_op.drop_column('client_tokens')
        batch_op.drop_column('client_model')
