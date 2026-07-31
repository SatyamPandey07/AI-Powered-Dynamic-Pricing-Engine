"""Competitors and Signals

Revision ID: 004
Revises: 003
Create Date: 2026-07-31 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None

def upgrade():
    # competitors table was already created in 001
    # competitor_sku_mappings was also created in 001
    op.create_table(
        'weather_signals',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('org_id', sa.String(), nullable=True),
        sa.Column('time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('temperature', sa.Float(), nullable=True),
        sa.Column('humidity', sa.Float(), nullable=True),
        sa.Column('precipitation', sa.Float(), nullable=True),
        sa.Column('condition', sa.String(), nullable=True),
        sa.Column('forecast_next_7_days', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'event_signals',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('org_id', sa.String(), nullable=True),
        sa.Column('event_name', sa.String(), nullable=True),
        sa.Column('event_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('affected_skus', sa.JSON(), nullable=True),
        sa.Column('impact_percent', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('event_signals')
    op.drop_table('weather_signals')
