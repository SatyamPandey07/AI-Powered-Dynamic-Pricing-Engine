"""Demand Forecasting

Revision ID: 003
Revises: 002
Create Date: 2026-07-31 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'model_versions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('org_id', sa.String(), nullable=True),
        sa.Column('sku_id', sa.String(), nullable=True),
        sa.Column('model_type', sa.String(), nullable=True),
        sa.Column('accuracy_mape', sa.Float(), nullable=True),
        sa.Column('accuracy_mae', sa.Float(), nullable=True),
        sa.Column('trained_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('activated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('model_artifact', sa.String(), nullable=True),
        sa.Column('parameters', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['sku_id'], ['skus.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('model_versions')
