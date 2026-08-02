"""
Database Models for Product Intelligence

This module defines SQLAlchemy models for storing product intelligence reports.
"""

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, Index, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional, Dict, Any, List

Base = declarative_base()


class ProductIntelligenceReport(Base):
    """
    Database model for product intelligence reports.
    
    Stores comprehensive product analysis results from the scoring engine.
    """
    __tablename__ = "product_intelligence_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    trend_id = Column(String(255), nullable=False, index=True, comment="Associated trend ID")
    product_name = Column(String(255), nullable=False, index=True, comment="Product name")
    category = Column(String(100), nullable=False, index=True, comment="Product category")
    
    # Individual rule scores
    estimated_margin_score = Column(Float, nullable=False, default=0.0)
    demand_score = Column(Float, nullable=False, default=0.0)
    competition_score = Column(Float, nullable=False, default=0.0)
    shipping_complexity_score = Column(Float, nullable=False, default=0.0)
    supplier_availability_score = Column(Float, nullable=False, default=0.0)
    seasonality_score = Column(Float, nullable=False, default=0.0)
    impulse_buy_score = Column(Float, nullable=False, default=0.0)
    content_potential_score = Column(Float, nullable=False, default=0.0)
    seo_potential_score = Column(Float, nullable=False, default=0.0)
    return_risk_score = Column(Float, nullable=False, default=0.0)
    legal_risk_score = Column(Float, nullable=False, default=0.0)
    
    # Overall assessment
    overall_score = Column(Float, nullable=False, default=0.0, index=True, comment="Overall score (0-100)")
    confidence_score = Column(Float, nullable=False, default=0.0, comment="Confidence in analysis (0-100)")
    recommendation = Column(String(50), nullable=False, index=True, comment="Recommendation level")
    reasoning = Column(Text, nullable=False, comment="Detailed reasoning")
    
    # Detailed analysis
    strengths = Column(JSON, nullable=False, default=list, comment="List of strengths")
    weaknesses = Column(JSON, nullable=False, default=list, comment="List of weaknesses")
    rule_results = Column(JSON, nullable=True, comment="Detailed rule results")
    
    # Metadata
    trend_data = Column(JSON, nullable=True, comment="Original trend data")
    analyzed_at = Column(DateTime, nullable=False, default=datetime.utcnow, comment="When analysis was performed")
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_product_category_score', 'category', 'overall_score'),
        Index('idx_product_recommendation', 'recommendation'),
        Index('idx_product_trend_id', 'trend_id'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "trend_id": self.trend_id,
            "product_name": self.product_name,
            "category": self.category,
            "estimated_margin_score": self.estimated_margin_score,
            "demand_score": self.demand_score,
            "competition_score": self.competition_score,
            "shipping_complexity_score": self.shipping_complexity_score,
            "supplier_availability_score": self.supplier_availability_score,
            "seasonality_score": self.seasonality_score,
            "impulse_buy_score": self.impulse_buy_score,
            "content_potential_score": self.content_potential_score,
            "seo_potential_score": self.seo_potential_score,
            "return_risk_score": self.return_risk_score,
            "legal_risk_score": self.legal_risk_score,
            "overall_score": self.overall_score,
            "confidence_score": self.confidence_score,
            "recommendation": self.recommendation,
            "reasoning": self.reasoning,
            "strengths": self.strengths or [],
            "weaknesses": self.weaknesses or [],
            "rule_results": self.rule_results or {},
            "trend_data": self.trend_data or {},
            "analyzed_at": self.analyzed_at.isoformat() if self.analyzed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
