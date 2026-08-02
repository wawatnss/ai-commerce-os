"""
Database Models for Supplier Intelligence

This module defines SQLAlchemy models for storing supplier and offer data.
"""

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, Index, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional, Dict, Any, List

Base = declarative_base()


class Supplier(Base):
    """
    Database model for supplier information.
    
    Stores supplier details independent of any specific platform.
    """
    __tablename__ = "suppliers"
    
    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(String(255), nullable=False, unique=True, index=True, comment="External supplier ID")
    name = Column(String(255), nullable=False, index=True, comment="Supplier name")
    source = Column(String(100), nullable=False, comment="Data source (api, import, etc.)")
    country = Column(String(100), nullable=True, comment="Supplier country")
    currency = Column(String(10), nullable=True, comment="Preferred currency")
    contact = Column(JSON, nullable=True, comment="Contact information")
    # Note: "metadata" is reserved by SQLAlchemy's Declarative API for
    # Base.metadata. The column stays named "metadata"; `.metadata` is
    # re-exposed via a property assigned after the class body (see below).
    extra_metadata = Column("metadata", JSON, nullable=True, comment="Additional metadata")
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_supplier_source', 'source'),
        Index('idx_supplier_country', 'country'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "supplier_id": self.supplier_id,
            "name": self.name,
            "source": self.source,
            "country": self.country,
            "currency": self.currency,
            "contact": self.contact or {},
            "metadata": self.metadata or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# Re-expose the "metadata" column as `.metadata` (see comment above).
Supplier.metadata = property(lambda self: self.extra_metadata, lambda self, value: setattr(self, "extra_metadata", value))


class SupplierOffer(Base):
    """
    Database model for supplier offers.
    
    Stores offer details for specific products from suppliers.
    """
    __tablename__ = "supplier_offers"
    
    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(String(255), nullable=False, index=True, comment="Supplier ID")
    product_id = Column(String(255), nullable=False, index=True, comment="Product ID")
    
    # Offer details
    unit_cost = Column(Float, nullable=False, comment="Unit cost")
    minimum_order_quantity = Column(Integer, nullable=False, comment="Minimum order quantity")
    estimated_processing_time = Column(Integer, nullable=False, comment="Processing time in days")
    estimated_shipping_time = Column(Integer, nullable=False, comment="Shipping time in days")
    available_quantity = Column(Integer, nullable=True, comment="Available quantity")
    currency = Column(String(10), nullable=True, comment="Currency for unit_cost")
    
    # Metadata
    # Note: "metadata" is reserved by SQLAlchemy's Declarative API for
    # Base.metadata. The column stays named "metadata"; `.metadata` is
    # re-exposed via a property assigned after the class body (see below).
    extra_metadata = Column("metadata", JSON, nullable=True, comment="Additional metadata")
    
    # Timestamps
    last_updated = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_offer_supplier_product', 'supplier_id', 'product_id'),
        Index('idx_offer_product', 'product_id'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "supplier_id": self.supplier_id,
            "product_id": self.product_id,
            "unit_cost": self.unit_cost,
            "minimum_order_quantity": self.minimum_order_quantity,
            "estimated_processing_time": self.estimated_processing_time,
            "estimated_shipping_time": self.estimated_shipping_time,
            "available_quantity": self.available_quantity,
            "currency": self.currency,
            "metadata": self.metadata or {},
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# Re-expose the "metadata" column as `.metadata` (see comment above).
SupplierOffer.metadata = property(lambda self: self.extra_metadata, lambda self, value: setattr(self, "extra_metadata", value))


class SupplierEvaluation(Base):
    """
    Database model for supplier evaluations.
    
    Stores evaluation results for supplier offers.
    """
    __tablename__ = "supplier_evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(String(255), nullable=False, index=True, comment="Supplier ID")
    product_id = Column(String(255), nullable=False, index=True, comment="Product ID")
    
    # Individual rule scores
    cost_score = Column(Float, nullable=False, default=0.0)
    delivery_score = Column(Float, nullable=False, default=0.0)
    moq_score = Column(Float, nullable=False, default=0.0)
    availability_score = Column(Float, nullable=False, default=0.0)
    reliability_score = Column(Float, nullable=False, default=0.0)
    flexibility_score = Column(Float, nullable=False, default=0.0)
    data_quality_score = Column(Float, nullable=False, default=0.0)
    
    # Overall assessment
    overall_score = Column(Float, nullable=False, default=0.0, index=True, comment="Overall score (0-100)")
    confidence_score = Column(Float, nullable=False, default=0.0, comment="Confidence in evaluation (0-100)")
    recommendation = Column(String(50), nullable=False, index=True, comment="Recommendation level")
    reasoning = Column(Text, nullable=False, comment="Detailed reasoning")
    
    # Detailed analysis
    strengths = Column(JSON, nullable=False, default=list, comment="List of strengths")
    weaknesses = Column(JSON, nullable=False, default=list, comment="List of weaknesses")
    rule_results = Column(JSON, nullable=True, comment="Detailed rule results")
    
    # Metadata
    rule_config = Column(JSON, nullable=True, comment="Rule configuration used")
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_evaluation_supplier_product', 'supplier_id', 'product_id'),
        Index('idx_evaluation_recommendation', 'recommendation'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "supplier_id": self.supplier_id,
            "product_id": self.product_id,
            "cost_score": self.cost_score,
            "delivery_score": self.delivery_score,
            "moq_score": self.moq_score,
            "availability_score": self.availability_score,
            "reliability_score": self.reliability_score,
            "flexibility_score": self.flexibility_score,
            "data_quality_score": self.data_quality_score,
            "overall_score": self.overall_score,
            "confidence_score": self.confidence_score,
            "recommendation": self.recommendation,
            "reasoning": self.reasoning,
            "strengths": self.strengths or [],
            "weaknesses": self.weaknesses or [],
            "rule_results": self.rule_results or {},
            "rule_config": self.rule_config or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
