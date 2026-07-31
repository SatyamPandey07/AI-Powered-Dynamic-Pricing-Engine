"""Price Optimization & Elasticity

Revision ID: 005
Revises: 004
Create Date: 2026-07-31 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'elasticity_measurements',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('org_id', sa.String(), nullable=True),
        sa.Column('sku_id', sa.String(), nullable=True),
        sa.Column('elasticity_value', sa.Float(), nullable=True),
        sa.Column('confidence_lower', sa.Float(), nullable=True),
        sa.Column('confidence_upper', sa.Float(), nullable=True),
        sa.Column('data_points', sa.Integer(), nullable=True),
        sa.Column('r_squared', sa.Float(), nullable=True),
        sa.Column('calculated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('model_type', sa.String(), nullable=True, default='regression'),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['sku_id'], ['skus.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'pricing_tests',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('org_id', sa.String(), nullable=True),
        sa.Column('sku_id', sa.String(), nullable=True),
        sa.Column('control_price', sa.Float(), nullable=True),
        sa.Column('treatment_price', sa.Float(), nullable=True),
        sa.Column('traffic_split', sa.Float(), nullable=True, default=0.5),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('control_conversions', sa.Integer(), nullable=True, default=0),
        sa.Column('treatment_conversions', sa.Integer(), nullable=True, default=0),
        sa.Column('control_revenue', sa.Float(), nullable=True, default=0.0),
        sa.Column('treatment_revenue', sa.Float(), nullable=True, default=0.0),
        sa.Column('p_value', sa.Float(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True, default=0.95),
        sa.Column('winner', sa.String(), nullable=True),
        sa.Column('winner_revenue_lift', sa.Float(), nullable=True),
        sa.Column('status', sa.String(), nullable=True, default='running'),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['sku_id'], ['skus.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'price_recommendations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('org_id', sa.String(), nullable=True),
        sa.Column('sku_id', sa.String(), nullable=True),
        sa.Column('recommended_price', sa.Float(), nullable=True),
        sa.Column('current_price', sa.Float(), nullable=True),
        sa.Column('objective', sa.String(), nullable=True),
        sa.Column('expected_revenue_impact', sa.Float(), nullable=True),
        sa.Column('expected_margin_impact', sa.Float(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('reasoning', sa.String(), nullable=True),
        sa.Column('factors', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('accepted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('actual_impact', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['sku_id'], ['skus.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'pricing_rules',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('org_id', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('condition', sa.JSON(), nullable=True),
        sa.Column('action', sa.JSON(), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=True, default=True),
        sa.Column('priority', sa.Integer(), nullable=True, default=0),
        sa.Column('last_applied_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id']),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('pricing_rules')
    op.drop_table('price_recommendations')
    op.drop_table('pricing_tests')
    op.drop_table('elasticity_measurements')
