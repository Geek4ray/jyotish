"""A conversation has a secret (SPEC Layer 8, decided after the review of chat v1, H7): `sessions.secret_hash`, the
hash of the secret the client's browser holds in an HttpOnly cookie.

Revision ID: 0006
Revises: 0005
Created: 2026-11-01"""

from alembic import op
import sqlalchemy as sa

revision = '0006'
down_revision = '0005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('sessions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('secret_hash', sa.String(length=64), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('sessions', schema=None) as batch_op:
        batch_op.drop_column('secret_hash')
