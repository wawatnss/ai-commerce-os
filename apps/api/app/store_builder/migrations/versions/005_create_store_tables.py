"""
Create store builder tables

Revision ID: 005
Revises: 004
Create Date: 2026-08-01
"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade():
    """Create store builder tables."""
    
    # Create store_blueprints table
    op.create_table(
        'store_blueprints',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('brand_profile_id', sa.String(255), nullable=False),
        sa.Column('product_id', sa.String(255), nullable=False),
        sa.Column('supplier_id', sa.String(255), nullable=True),
        sa.Column('store_name', sa.String(255), nullable=False),
        sa.Column('store_description', sa.Text(), nullable=False),
        sa.Column('tagline', sa.String(500), nullable=True),
        sa.Column('blueprint_json', sa.JSON(), nullable=False),
        sa.Column('validation_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('validation_result', sa.JSON(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_store_blueprints_id', 'store_blueprints', ['id'])
    op.create_index('ix_store_blueprints_brand_profile_id', 'store_blueprints', ['brand_profile_id'])
    op.create_index('ix_store_blueprints_product_id', 'store_blueprints', ['product_id'])
    op.create_index('ix_store_blueprints_supplier_id', 'store_blueprints', ['supplier_id'])
    op.create_index('ix_store_blueprints_store_name', 'store_blueprints', ['store_name'])
    op.create_index('ix_store_blueprints_created_at', 'store_blueprints', ['created_at'])
    op.create_index('idx_store_brand_product', 'store_blueprints', ['brand_profile_id', 'product_id'])


def downgrade():
    """Drop store builder tables."""
    op.drop_table('store_blueprints')
