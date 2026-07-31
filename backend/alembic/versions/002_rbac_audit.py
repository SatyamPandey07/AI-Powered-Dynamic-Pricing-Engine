"""RBAC and Audit

Revision ID: 002
Revises: 001
Create Date: 2026-07-30 23:45:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade():
    # add is_active to organizations
    op.add_column('organizations', sa.Column('is_active', sa.Boolean(), server_default='true', nullable=True))
    
    # add is_active to users
    op.add_column('users', sa.Column('is_active', sa.Boolean(), server_default='true', nullable=True))
    
    # create password_history table
    op.create_table(
        'password_history',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('hashed_password', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('password_history')
    op.drop_column('users', 'is_active')
    op.drop_column('organizations', 'is_active')
