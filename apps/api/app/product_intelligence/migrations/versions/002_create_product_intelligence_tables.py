"""
Create product intelligence tables

Revision ID: 002
Revises: 001
Create Date: 2026-08-01
"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    """Create product intelligence tables."""
    
    # Create product_intelligence_reports table
    op.create_table(
        'product_intelligence_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('trend_id', sa.String(255), nullable=False),
        sa.Column('product_name', sa.String(255), nullable=False),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('estimated_margin_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('demand_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('competition_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('shipping_complexity_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('supplier_availability_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('seasonality_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('impulse_buy_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('content_potential_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('seo_potential_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('return_risk_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('legal_risk_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('overall_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('confidence_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('recommendation', sa.String(50), nullable=False, server_default='hold'),
        sa.Column('reasoning', sa.Text(), nullable=False),
        sa.Column('strengths', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('weaknesses', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('rule_results', sa.JSON(), nullable=True),
        sa.Column('trend_data', sa.JSON(), nullable=True),
        sa.Column('analyzed_at', sa.DateTime(), nullable=False, server_default=datetime.utcnow),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_product_intelligence_reports_id', 'product_intelligence_reports', ['id'])
    op.create_index('ix_product_intelligence_reports_trend_id', 'product_intelligence_reports', ['trend_id'])
    op.create_index('ix_product_intelligence_reports_product_name', 'product_intelligence_reports', ['product_name'])
    op.create_index('ix_product_intelligence_reports_category', 'product_intelligence_reports', ['category'])
    op.create_index('ix_product_intelligence_reports_overall_score', 'product_intelligence_reports', ['overall_score'])
    op.create_index('ix_product_intelligence_reports_recommendation', 'product_intelligence_reports', ['recommendation'])
    op.create_index('ix_product_intelligence_reports_created_at', 'product_intelligence_reports', ['created_at'])
    op.create_index('idx_product_category_score', 'product_intelligence_reports', ['category', 'overall_score'])


def downgrade():
    """Drop product intelligence tables."""
    op.drop_table('product_intelligence_reports')
