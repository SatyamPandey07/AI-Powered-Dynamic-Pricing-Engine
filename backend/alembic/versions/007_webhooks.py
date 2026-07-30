"""Webhooks

Revision ID: 007
Revises: 006
Create Date: 2026-07-31 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'webhooks',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('org_id', sa.String(), nullable=True),
        sa.Column('endpoint_type', sa.String(), nullable=True),
        sa.Column('target_url', sa.String(), nullable=True),
        sa.Column('events_subscribed', sa.JSON(), nullable=True),
        sa.Column('signing_secret', sa.String(), nullable=True),
        sa.Column('active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'webhook_deliveries',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('webhook_id', sa.String(), nullable=True),
        sa.Column('event_type', sa.String(), nullable=True),
        sa.Column('payload', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(), default='pending'),
        sa.Column('attempt_number', sa.Integer(), default=0),
        sa.Column('next_retry_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('response_code', sa.Integer(), nullable=True),
        sa.Column('response_body', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['webhook_id'], ['webhooks.id']),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('webhook_deliveries')
    op.drop_table('webhooks')
