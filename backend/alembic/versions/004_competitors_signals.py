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
    op.create_table(
        'competitors',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('org_id', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('website_url', sa.String(), nullable=True),
        sa.Column('api_type', sa.String(), nullable=True),
        sa.Column('scrape_config', sa.JSON(), nullable=True),
        sa.Column('last_checked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.Column('update_frequency_hours', sa.Integer(), nullable=True, default=24),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'competitor_sku_mappings',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('competitor_id', sa.String(), nullable=True),
        sa.Column('sku_id', sa.String(), nullable=True),
        sa.Column('competitor_sku_id', sa.String(), nullable=True),
        sa.Column('competitor_product_url', sa.String(), nullable=True),
        sa.Column('last_price', sa.Float(), nullable=True),
        sa.Column('last_updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['competitor_id'], ['competitors.id'], ),
        sa.ForeignKeyConstraint(['sku_id'], ['skus.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
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
    # Add source column to price_history
    op.add_column('price_history', sa.Column('source', sa.String(), nullable=True))

def downgrade():
    op.drop_column('price_history', 'source')
    op.drop_table('event_signals')
    op.drop_table('weather_signals')
    op.drop_table('competitor_sku_mappings')
    op.drop_table('competitors')
