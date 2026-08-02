"""
Database Models for Trend Intelligence

This module defines SQLAlchemy models for storing trend data in the database.
"""

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, Index, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional, Dict, Any, List

Base = declarative_base()


class Trend(Base):
    """
    Database model for trend items.
    
    Stores normalized trend data from various providers with all calculated scores.
    """
    __tablename__ = "trends"
    
    id = Column(Integer, primary_key=True, index=True)
    trend_id = Column(String(255), unique=True, nullable=False, index=True, comment="Unique trend identifier")
    source = Column(String(100), nullable=False, index=True, comment="Data source provider")
    product_name = Column(String(255), nullable=False, index=True, comment="Product or keyword name")
    brand = Column(String(255), nullable=True, index=True, comment="Associated brand")
    category = Column(String(100), nullable=False, index=True, comment="Product category")
    tags = Column(JSON, nullable=False, default=list, comment="Associated tags/keywords")
    
    # Scores
    popularity_score = Column(Float, nullable=False, default=0.0, comment="Popularity score (0-100)")
    growth_score = Column(Float, nullable=False, default=0.0, comment="Growth score (0-100)")
    competition_score = Column(Float, nullable=False, default=0.0, comment="Competition score (0-100)")
    opportunity_score = Column(Float, nullable=False, default=0.0, comment="Opportunity score (0-100)")
    confidence_score = Column(Float, nullable=False, default=0.0, comment="Confidence score (0-100)")
    overall_score = Column(Float, nullable=False, default=0.0, index=True, comment="Overall weighted score (0-100)")
    
    # Component scores (for detailed analysis)
    component_scores = Column(JSON, nullable=True, comment="Individual component scores breakdown")
    weighted_scores = Column(JSON, nullable=True, comment="Weighted component scores")
    
    # Metadata
    # Note: the SQLAlchemy Declarative API reserves the literal attribute name
    # "metadata" (it's used for Base.metadata). The physical column is still
    # named "metadata"; the Python-side attribute is exposed as `.metadata`
    # again via a property assigned right after the class body (see below).
    extra_metadata = Column("metadata", JSON, nullable=True, default=dict, comment="Additional provider-specific data")
    detected_at = Column(DateTime, nullable=False, index=True, comment="When the trend was detected")
    collected_at = Column(DateTime, nullable=False, default=datetime.utcnow, comment="When data was collected")
    scored_at = Column(DateTime, nullable=True, comment="When scores were calculated")
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True, index=True, comment="Whether trend is active")
    is_processed = Column(Boolean, nullable=False, default=False, comment="Whether trend has been processed")
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_source_category', 'source', 'category'),
        Index('idx_overall_score_desc', 'overall_score'),
        Index('idx_detected_at_desc', 'detected_at'),
        Index('idx_product_name_category', 'product_name', 'category'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "trend_id": self.trend_id,
            "source": self.source,
            "product_name": self.product_name,
            "brand": self.brand,
            "category": self.category,
            "tags": self.tags or [],
            "popularity_score": self.popularity_score,
            "growth_score": self.growth_score,
            "competition_score": self.competition_score,
            "opportunity_score": self.opportunity_score,
            "confidence_score": self.confidence_score,
            "overall_score": self.overall_score,
            "component_scores": self.component_scores,
            "weighted_scores": self.weighted_scores,
            "metadata": self.metadata or {},
            "detected_at": self.detected_at.isoformat() if self.detected_at else None,
            "collected_at": self.collected_at.isoformat() if self.collected_at else None,
            "scored_at": self.scored_at.isoformat() if self.scored_at else None,
            "is_active": self.is_active,
            "is_processed": self.is_processed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# Re-expose the "metadata" column as `.metadata` (see comment above). This is
# assigned after the class body so SQLAlchemy's declarative scanning never
# sees an attribute literally named "metadata".
Trend.metadata = property(lambda self: self.extra_metadata, lambda self, value: setattr(self, "extra_metadata", value))


class TrendCollection(Base):
    """
    Database model for trend collection jobs.
    
    Tracks batch collection operations from providers.
    """
    __tablename__ = "trend_collections"
    
    id = Column(Integer, primary_key=True, index=True)
    collection_id = Column(String(255), unique=True, nullable=False, index=True)
    provider = Column(String(100), nullable=False, index=True)
    
    # Collection parameters
    parameters = Column(JSON, nullable=True, default=dict, comment="Collection parameters used")
    
    # Results
    items_collected = Column(Integer, nullable=False, default=0, comment="Number of items collected")
    items_processed = Column(Integer, nullable=False, default=0, comment="Number of items successfully processed")
    items_failed = Column(Integer, nullable=False, default=0, comment="Number of items that failed")
    
    # Status
    status = Column(String(50), nullable=False, default="pending", index=True, comment="Collection status")
    error_message = Column(Text, nullable=True, comment="Error message if failed")
    
    # Timing
    started_at = Column(DateTime, nullable=True, comment="When collection started")
    completed_at = Column(DateTime, nullable=True, comment="When collection completed")
    duration_seconds = Column(Float, nullable=True, comment="Collection duration in seconds")
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "collection_id": self.collection_id,
            "provider": self.provider,
            "parameters": self.parameters or {},
            "items_collected": self.items_collected,
            "items_processed": self.items_processed,
            "items_failed": self.items_failed,
            "status": self.status,
            "error_message": self.error_message,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class TrendScoreHistory(Base):
    """
    Database model for tracking score history.
    
    Stores historical score data for trend analysis and optimization.
    """
    __tablename__ = "trend_score_history"
    
    id = Column(Integer, primary_key=True, index=True)
    trend_id = Column(String(255), nullable=False, index=True, comment="Reference to trend.trend_id")
    
    # Scores at this point in time
    popularity_score = Column(Float, nullable=False)
    growth_score = Column(Float, nullable=False)
    competition_score = Column(Float, nullable=False)
    opportunity_score = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)
    overall_score = Column(Float, nullable=False, index=True)
    
    # Score breakdown
    component_scores = Column(JSON, nullable=True)
    weighted_scores = Column(JSON, nullable=True)
    
    # Weights used
    score_weights = Column(JSON, nullable=True, comment="Weights used for calculation")
    
    # Timestamp
    recorded_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "trend_id": self.trend_id,
            "popularity_score": self.popularity_score,
            "growth_score": self.growth_score,
            "competition_score": self.competition_score,
            "opportunity_score": self.opportunity_score,
            "confidence_score": self.confidence_score,
            "overall_score": self.overall_score,
            "component_scores": self.component_scores,
            "weighted_scores": self.weighted_scores,
            "score_weights": self.score_weights,
            "recorded_at": self.recorded_at.isoformat() if self.recorded_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
