"""
Create brand builder tables

Revision ID: 004
Revises: 003
Create Date: 2026-08-01
"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    """Create brand builder tables."""
    
    # Create brand_profiles table
    op.create_table(
        'brand_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.String(255), nullable=False),
        sa.Column('supplier_id', sa.String(255), nullable=True),
        sa.Column('brand_name', sa.String(255), nullable=False),
        sa.Column('slogan', sa.String(500), nullable=True),
        sa.Column('mission', sa.Text(), nullable=True),
        sa.Column('vision', sa.Text(), nullable=True),
        sa.Column('target_audience', sa.String(255), nullable=True),
        sa.Column('customer_persona', sa.JSON(), nullable=True),
        sa.Column('tone_of_voice', sa.String(255), nullable=True),
        sa.Column('writing_style', sa.JSON(), nullable=True),
        sa.Column('color_palette', sa.JSON(), nullable=True),
        sa.Column('typography', sa.JSON(), nullable=True),
        sa.Column('logo_prompt', sa.Text(), nullable=True),
        sa.Column('packaging_prompt', sa.Text(), nullable=True),
        sa.Column('product_photography_prompt', sa.Text(), nullable=True),
        sa.Column('hero_banner_prompt', sa.Text(), nullable=True),
        sa.Column('social_media_style', sa.Text(), nullable=True),
        sa.Column('seo_style', sa.Text(), nullable=True),
        sa.Column('email_style', sa.Text(), nullable=True),
        sa.Column('trust_elements', sa.JSON(), nullable=True),
        sa.Column('unique_value_proposition', sa.JSON(), nullable=True),
        sa.Column('differentiators', sa.JSON(), nullable=True),
        sa.Column('domain_name_suggestions', sa.JSON(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('validation_result', sa.JSON(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_brand_profiles_id', 'brand_profiles', ['id'])
    op.create_index('ix_brand_profiles_product_id', 'brand_profiles', ['product_id'])
    op.create_index('ix_brand_profiles_supplier_id', 'brand_profiles', ['supplier_id'])
    op.create_index('ix_brand_profiles_brand_name', 'brand_profiles', ['brand_name'])
    op.create_index('ix_brand_profiles_created_at', 'brand_profiles', ['created_at'])
    op.create_index('idx_brand_product_supplier', 'brand_profiles', ['product_id', 'supplier_id'])


def downgrade():
    """Drop brand builder tables."""
    op.drop_table('brand_profiles')
