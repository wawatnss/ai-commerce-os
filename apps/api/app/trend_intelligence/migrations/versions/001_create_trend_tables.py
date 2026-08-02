"""
Create trend intelligence tables

Revision ID: 001
Revises: 
Create Date: 2026-08-01
"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Create trend intelligence tables."""
    
    # Create trends table
    op.create_table(
        'trends',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('trend_id', sa.String(255), nullable=False),
        sa.Column('source', sa.String(100), nullable=False),
        sa.Column('product_name', sa.String(255), nullable=False),
        sa.Column('brand', sa.String(255), nullable=True),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('tags', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('popularity_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('growth_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('competition_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('opportunity_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('confidence_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('overall_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('component_scores', sa.JSON(), nullable=True),
        sa.Column('weighted_scores', sa.JSON(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True, server_default='{}'),
        sa.Column('detected_at', sa.DateTime(), nullable=False),
        sa.Column('collected_at', sa.DateTime(), nullable=False, server_default=datetime.utcnow),
        sa.Column('scored_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_processed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for trends
    op.create_index('ix_trends_id', 'trends', ['id'])
    op.create_index('ix_trends_trend_id', 'trends', ['trend_id'], unique=True)
    op.create_index('ix_trends_source', 'trends', ['source'])
    op.create_index('ix_trends_product_name', 'trends', ['product_name'])
    op.create_index('ix_trends_brand', 'trends', ['brand'])
    op.create_index('ix_trends_category', 'trends', ['category'])
    op.create_index('ix_trends_overall_score', 'trends', ['overall_score'])
    op.create_index('ix_trends_detected_at', 'trends', ['detected_at'])
    op.create_index('ix_trends_is_active', 'trends', ['is_active'])
    op.create_index('ix_trends_created_at', 'trends', ['created_at'])
    op.create_index('idx_source_category', 'trends', ['source', 'category'])
    op.create_index('idx_overall_score_desc', 'trends', [sa.text('overall_score DESC')])
    op.create_index('idx_detected_at_desc', 'trends', [sa.text('detected_at DESC')])
    op.create_index('idx_product_name_category', 'trends', ['product_name', 'category'])
    
    # Create trend_collections table
    op.create_table(
        'trend_collections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('collection_id', sa.String(255), nullable=False),
        sa.Column('provider', sa.String(100), nullable=False),
        sa.Column('parameters', sa.JSON(), nullable=True, server_default='{}'),
        sa.Column('items_collected', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('items_processed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('items_failed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('duration_seconds', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for trend_collections
    op.create_index('ix_trend_collections_id', 'trend_collections', ['id'])
    op.create_index('ix_trend_collections_collection_id', 'trend_collections', ['collection_id'], unique=True)
    op.create_index('ix_trend_collections_provider', 'trend_collections', ['provider'])
    op.create_index('ix_trend_collections_status', 'trend_collections', ['status'])
    op.create_index('ix_trend_collections_created_at', 'trend_collections', ['created_at'])
    
    # Create trend_score_history table
    op.create_table(
        'trend_score_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('trend_id', sa.String(255), nullable=False),
        sa.Column('popularity_score', sa.Float(), nullable=False),
        sa.Column('growth_score', sa.Float(), nullable=False),
        sa.Column('competition_score', sa.Float(), nullable=False),
        sa.Column('opportunity_score', sa.Float(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('overall_score', sa.Float(), nullable=False),
        sa.Column('component_scores', sa.JSON(), nullable=True),
        sa.Column('weighted_scores', sa.JSON(), nullable=True),
        sa.Column('score_weights', sa.JSON(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(), nullable=False, server_default=datetime.utcnow),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=datetime.utcnow),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for trend_score_history
    op.create_index('ix_trend_score_history_id', 'trend_score_history', ['id'])
    op.create_index('ix_trend_score_history_trend_id', 'trend_score_history', ['trend_id'])
    op.create_index('ix_trend_score_history_overall_score', 'trend_score_history', ['overall_score'])
    op.create_index('ix_trend_score_history_recorded_at', 'trend_score_history', ['recorded_at'])


def downgrade():
    """Drop trend intelligence tables."""
    
    # Drop tables
    op.drop_table('trend_score_history')
    op.drop_table('trend_collections')
    op.drop_table('trends')
