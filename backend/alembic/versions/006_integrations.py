"""Integrations & Sync Logs

Revision ID: 006
Revises: 005
Create Date: 2026-07-31 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'integrations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('org_id', sa.String(), nullable=True),
        sa.Column('platform', sa.String(), nullable=True),   # shopify | woocommerce | custom
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True, default='pending_auth'),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.Column('credentials', sa.Text(), nullable=True),  # Fernet-encrypted JSON
        sa.Column('config', sa.JSON(), nullable=True),       # sync freq, field mappings
        sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_sync_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'integration_credentials_history',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('integration_id', sa.String(), nullable=True),
        sa.Column('old_credentials_hash', sa.String(), nullable=True),
        sa.Column('new_credentials_hash', sa.String(), nullable=True),
        sa.Column('changed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['integration_id'], ['integrations.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'sync_logs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('integration_id', sa.String(), nullable=True),
        sa.Column('sync_type', sa.String(), nullable=True),  # inventory | sales | prices
        sa.Column('status', sa.String(), nullable=True),     # running | completed | failed
        sa.Column('items_processed', sa.Integer(), nullable=True, default=0),
        sa.Column('error_count', sa.Integer(), nullable=True, default=0),
        sa.Column('errors', sa.JSON(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['integration_id'], ['integrations.id']),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('sync_logs')
    op.drop_table('integration_credentials_history')
    op.drop_table('integrations')
