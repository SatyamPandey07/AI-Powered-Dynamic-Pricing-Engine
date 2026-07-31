"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2026-07-30 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Organizations
    op.create_table(
        'organizations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('subscription_tier', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Users
    op.create_table(
        'users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('org_id', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('hashed_password', sa.String(), nullable=True),
        sa.Column('role', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    
    # API Keys
    op.create_table(
        'api_keys',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('org_id', sa.String(), nullable=True),
        sa.Column('key_hash', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Skus
    op.create_table(
        'skus',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('org_id', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('cost', sa.Float(), nullable=True),
        sa.Column('min_price', sa.Float(), nullable=True),
        sa.Column('max_price', sa.Float(), nullable=True),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Suppliers
    op.create_table(
        'suppliers',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('org_id', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('api_endpoint', sa.String(), nullable=True),
        sa.Column('auth_type', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Competitors
    op.create_table(
        'competitors',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('org_id', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('website_url', sa.String(), nullable=True),
        sa.Column('api_type', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Competitor Sku Mappings
    op.create_table(
        'competitor_sku_mappings',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('competitor_id', sa.String(), nullable=True),
        sa.Column('sku_id', sa.String(), nullable=True),
        sa.Column('competitor_sku_id', sa.String(), nullable=True),
        sa.Column('last_price', sa.Float(), nullable=True),
        sa.Column('last_checked_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['competitor_id'], ['competitors.id'], ),
        sa.ForeignKeyConstraint(['sku_id'], ['skus.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Audit Logs
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('org_id', sa.String(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('action', sa.String(), nullable=True),
        sa.Column('resource_type', sa.String(), nullable=True),
        sa.Column('resource_id', sa.String(), nullable=True),
        sa.Column('changes_before', postgresql.JSONB(), nullable=True),
        sa.Column('changes_after', postgresql.JSONB(), nullable=True),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('user_agent', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # TimescaleDB Hypertables
    op.execute('''
        CREATE TABLE IF NOT EXISTS price_history (
            time TIMESTAMP WITH TIME ZONE NOT NULL,
            org_id VARCHAR REFERENCES organizations(id),
            sku_id VARCHAR REFERENCES skus(id),
            price DOUBLE PRECISION,
            source VARCHAR,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            PRIMARY KEY (time, org_id, sku_id)
        );
        SELECT create_hypertable('price_history', 'time', if_not_exists => TRUE);
    ''')
    
    op.execute('''
        CREATE TABLE IF NOT EXISTS sales_history (
            time TIMESTAMP WITH TIME ZONE NOT NULL,
            org_id VARCHAR REFERENCES organizations(id),
            sku_id VARCHAR REFERENCES skus(id),
            units_sold INTEGER,
            revenue DOUBLE PRECISION,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            PRIMARY KEY (time, org_id, sku_id)
        );
        SELECT create_hypertable('sales_history', 'time', if_not_exists => TRUE);
    ''')
    
    op.execute('''
        CREATE TABLE IF NOT EXISTS forecast_history (
            time TIMESTAMP WITH TIME ZONE NOT NULL,
            org_id VARCHAR REFERENCES organizations(id),
            sku_id VARCHAR REFERENCES skus(id),
            forecast_date TIMESTAMP WITH TIME ZONE,
            forecasted_units DOUBLE PRECISION,
            confidence_lower DOUBLE PRECISION,
            confidence_upper DOUBLE PRECISION,
            model_version VARCHAR,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            PRIMARY KEY (time, org_id, sku_id)
        );
        SELECT create_hypertable('forecast_history', 'time', if_not_exists => TRUE);
    ''')

def downgrade():
    op.drop_table('audit_logs')
    op.drop_table('competitor_sku_mappings')
    op.drop_table('competitors')
    op.drop_table('suppliers')
    op.drop_table('skus')
    op.drop_table('api_keys')
    op.drop_table('users')
    op.drop_table('organizations')
    op.execute("DROP TABLE price_history CASCADE;")
    op.execute("DROP TABLE sales_history CASCADE;")
    op.execute("DROP TABLE forecast_history CASCADE;")
