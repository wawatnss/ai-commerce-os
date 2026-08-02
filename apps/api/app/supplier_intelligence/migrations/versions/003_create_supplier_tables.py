"""
Create supplier intelligence tables

Revision ID: 003
Revises: 002
Create Date: 2026-08-01
"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    """Create supplier intelligence tables."""
    
    # Create suppliers table
    op.create_table(
        'suppliers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('supplier_id', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('source', sa.String(100), nullable=False),
        sa.Column('country', sa.String(100), nullable=True),
        sa.Column('currency', sa.String(10), nullable=True),
        sa.Column('contact', sa.JSON(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('supplier_id')
    )
    
    # Create supplier_offers table
    op.create_table(
        'supplier_offers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('supplier_id', sa.String(255), nullable=False),
        sa.Column('product_id', sa.String(255), nullable=False),
        sa.Column('unit_cost', sa.Float(), nullable=False),
        sa.Column('minimum_order_quantity', sa.Integer(), nullable=False),
        sa.Column('estimated_processing_time', sa.Integer(), nullable=False),
        sa.Column('estimated_shipping_time', sa.Integer(), nullable=False),
        sa.Column('available_quantity', sa.Integer(), nullable=True),
        sa.Column('currency', sa.String(10), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('last_updated', sa.DateTime(), nullable=False, server_default=datetime.utcnow),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=datetime.utcnow),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create supplier_evaluations table
    op.create_table(
        'supplier_evaluations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('supplier_id', sa.String(255), nullable=False),
        sa.Column('product_id', sa.String(255), nullable=False),
        sa.Column('cost_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('delivery_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('moq_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('availability_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('reliability_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('flexibility_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('data_quality_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('overall_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('confidence_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('recommendation', sa.String(50), nullable=False, server_default='consider'),
        sa.Column('reasoning', sa.Text(), nullable=False),
        sa.Column('strengths', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('weaknesses', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('rule_results', sa.JSON(), nullable=True),
        sa.Column('rule_config', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=datetime.utcnow),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_suppliers_id', 'suppliers', ['id'])
    op.create_index('ix_suppliers_supplier_id', 'suppliers', ['supplier_id'])
    op.create_index('ix_suppliers_name', 'suppliers', ['name'])
    op.create_index('ix_suppliers_created_at', 'suppliers', ['created_at'])
    op.create_index('idx_supplier_source', 'suppliers', ['source'])
    op.create_index('idx_supplier_country', 'suppliers', ['country'])
    
    op.create_index('ix_supplier_offers_id', 'supplier_offers', ['id'])
    op.create_index('ix_supplier_offers_supplier_id', 'supplier_offers', ['supplier_id'])
    op.create_index('ix_supplier_offers_product_id', 'supplier_offers', ['product_id'])
    op.create_index('ix_supplier_offers_last_updated', 'supplier_offers', ['last_updated'])
    op.create_index('idx_offer_supplier_product', 'supplier_offers', ['supplier_id', 'product_id'])
    op.create_index('idx_offer_product', 'supplier_offers', ['product_id'])
    
    op.create_index('ix_supplier_evaluations_id', 'supplier_evaluations', ['id'])
    op.create_index('ix_supplier_evaluations_supplier_id', 'supplier_evaluations', ['supplier_id'])
    op.create_index('ix_supplier_evaluations_product_id', 'supplier_evaluations', ['product_id'])
    op.create_index('ix_supplier_evaluations_overall_score', 'supplier_evaluations', ['overall_score'])
    op.create_index('ix_supplier_evaluations_recommendation', 'supplier_evaluations', ['recommendation'])
    op.create_index('ix_supplier_evaluations_created_at', 'supplier_evaluations', ['created_at'])
    op.create_index('idx_evaluation_supplier_product', 'supplier_evaluations', ['supplier_id', 'product_id'])
    op.create_index('idx_evaluation_recommendation', 'supplier_evaluations', ['recommendation'])


def downgrade():
    """Drop supplier intelligence tables."""
    op.drop_table('supplier_evaluations')
    op.drop_table('supplier_offers')
    op.drop_table('suppliers')
