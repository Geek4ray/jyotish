"""The service's tables as of 2026-10-23: charts, readings, reviews, exclusions, the outcome side
(consents, subjects, events, erasures) and the blind comparison's pairs.

A database made by `create_all` before this revision existed is adopted by jyotish.db.migrate
(stamped, not re-created).

Revision ID: 0001
Revises:
Created: 2026-10-23"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# The document columns: JSON, JSONB under Postgres (as jyotish.db.DOCUMENT).
DOCUMENT = sa.JSON().with_variant(postgresql.JSONB(), "postgresql")

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('charts',
    sa.Column('id', sa.String(length=64), nullable=False),
    sa.Column('birth_key', sa.String(length=64), nullable=True),
    sa.Column('birth', DOCUMENT, nullable=False),
    sa.Column('engine', sa.String(length=32), nullable=False),
    sa.Column('document', DOCUMENT, nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('consents',
    sa.Column('id', sa.String(length=64), nullable=False),
    sa.Column('subject_id', sa.String(length=64), nullable=False),
    sa.Column('form_version', sa.String(length=32), nullable=False),
    sa.Column('track', sa.String(length=16), nullable=False),
    sa.Column('given_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('withdrawn_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('recorded_by', sa.String(length=64), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('erasures',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('subject_id', sa.String(length=64), nullable=False),
    sa.Column('erased_by', sa.String(length=64), nullable=False),
    sa.Column('counts', DOCUMENT, nullable=False),
    sa.Column('erased_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('exclusions',
    sa.Column('chart_id', sa.String(length=64), nullable=False),
    sa.Column('birth_key', sa.String(length=64), nullable=True),
    sa.Column('reason', sa.String(length=64), nullable=False),
    sa.Column('reviewer_id', sa.String(length=64), nullable=False),
    sa.Column('reading_id', sa.String(length=32), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('chart_id')
    )
    op.create_table('subjects',
    sa.Column('id', sa.String(length=64), nullable=False),
    sa.Column('chart_id', sa.String(length=64), nullable=False),
    sa.Column('birth_key', sa.String(length=64), nullable=True),
    sa.Column('birth', DOCUMENT, nullable=False),
    sa.Column('accuracy', sa.String(length=16), nullable=False),
    sa.Column('sex', sa.String(length=16), nullable=False),
    sa.Column('region', sa.String(length=64), nullable=False),
    sa.Column('source', sa.String(length=16), nullable=False),
    sa.Column('rectified', sa.Boolean(), nullable=False),
    sa.Column('seen_by_astrologer', sa.Boolean(), nullable=False),
    sa.Column('household_key', sa.String(length=64), nullable=True),
    sa.Column('birthplace_cluster', sa.String(length=64), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('events',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('subject_id', sa.String(length=64), nullable=False),
    sa.Column('event_type', sa.String(length=32), nullable=False),
    sa.Column('age_at_event', sa.Float(), nullable=True),
    sa.Column('censor_age', sa.Float(), nullable=False),
    sa.Column('value', DOCUMENT, nullable=True),
    sa.Column('self_report', sa.Boolean(), nullable=False),
    sa.Column('entered_by', sa.String(length=64), nullable=False),
    sa.Column('entered_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('before_reading', sa.DateTime(timezone=True), nullable=True),
    sa.Column('after', sa.Boolean(), nullable=False),
    sa.Column('consent_id', sa.String(length=64), nullable=False),
    sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('readings',
    sa.Column('id', sa.String(length=32), nullable=False),
    sa.Column('chart_id', sa.String(length=64), nullable=True),
    sa.Column('birth_key', sa.String(length=64), nullable=True),
    sa.Column('question', sa.Text(), nullable=False),
    sa.Column('request', DOCUMENT, nullable=False),
    sa.Column('status', sa.String(length=16), nullable=False),
    sa.Column('progress', DOCUMENT, nullable=False),
    sa.Column('document', DOCUMENT, nullable=True),
    sa.Column('page', sa.Text(), nullable=True),
    sa.Column('error', DOCUMENT, nullable=True),
    sa.Column('review_status', sa.String(length=16), server_default='draft', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['chart_id'], ['charts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('comparisons',
    sa.Column('id', sa.String(length=80), nullable=False),
    sa.Column('reading_a', sa.String(length=32), nullable=False),
    sa.Column('reading_b', sa.String(length=32), nullable=False),
    sa.Column('created_by', sa.String(length=64), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['reading_a'], ['readings.id'], ),
    sa.ForeignKeyConstraint(['reading_b'], ['readings.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('reviews',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('reading_id', sa.String(length=32), nullable=False),
    sa.Column('chart_id', sa.String(length=64), nullable=True),
    sa.Column('reviewer_id', sa.String(length=64), nullable=False),
    sa.Column('action', sa.String(length=16), nullable=False),
    sa.Column('target', sa.String(length=200), nullable=True),
    sa.Column('before', sa.Text(), nullable=True),
    sa.Column('after', sa.Text(), nullable=True),
    sa.Column('accepted', sa.Boolean(), nullable=True),
    sa.Column('errors', DOCUMENT, nullable=True),
    sa.Column('area', sa.String(length=32), nullable=True),
    sa.Column('verdict', sa.String(length=16), nullable=True),
    sa.Column('reason', sa.String(length=32), nullable=True),
    sa.Column('step', sa.String(length=32), nullable=True),
    sa.Column('answer', DOCUMENT, nullable=True),
    sa.Column('mode', sa.String(length=16), nullable=True),
    sa.Column('comment', sa.Text(), nullable=True),
    sa.Column('facts', DOCUMENT, nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['reading_id'], ['readings.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('reviews')
    op.drop_table('comparisons')
    op.drop_table('readings')
    op.drop_table('events')
    op.drop_table('subjects')
    op.drop_table('exclusions')
    op.drop_table('erasures')
    op.drop_table('consents')
    op.drop_table('charts')
