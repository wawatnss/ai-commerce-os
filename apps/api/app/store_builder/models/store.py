"""
Database Models for Store Builder

This module defines SQLAlchemy models for storing store blueprints.
"""

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional, Dict, Any

Base = declarative_base()


class StoreBlueprint(Base):
    """
    Database model for store blueprints.
    
    Stores complete store configuration generated from intelligence data.
    """
    __tablename__ = "store_blueprints"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Source Data
    user_id = Column(Integer, nullable=True, index=True, comment="Owner user ID")
    brand_profile_id = Column(String(255), nullable=False, index=True, comment="Brand profile ID")
    product_id = Column(String(255), nullable=False, index=True, comment="Product ID")
    supplier_id = Column(String(255), nullable=True, index=True, comment="Supplier ID")
    
    # Store Identity
    store_name = Column(String(255), nullable=False, index=True, comment="Store name")
    store_description = Column(Text, nullable=False, comment="Store description")
    tagline = Column(String(500), nullable=True, comment="Store tagline")
    
    # Complete Blueprint (JSON for flexibility)
    blueprint_json = Column(JSON, nullable=False, comment="Complete store blueprint")
    
    # Validation
    validation_score = Column(Float, nullable=False, default=0.0, comment="Overall validation score")
    validation_result = Column(JSON, nullable=True, comment="Validation results")
    
    # Metadata
    # Note: "metadata" is reserved by SQLAlchemy's Declarative API for
    # Base.metadata. The column stays named "metadata"; `.metadata` is
    # re-exposed via a property assigned after the class body (see below).
    extra_metadata = Column("metadata", JSON, nullable=True, comment="Additional metadata")
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_store_brand_product', 'brand_profile_id', 'product_id'),
        Index('idx_store_name', 'store_name'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "brand_profile_id": self.brand_profile_id,
            "product_id": self.product_id,
            "supplier_id": self.supplier_id,
            "store_name": self.store_name,
            "store_description": self.store_description,
            "tagline": self.tagline,
            "blueprint_json": self.blueprint_json or {},
            "validation_score": self.validation_score,
            "validation_result": self.validation_result or {},
            "metadata": self.metadata or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# Re-expose the "metadata" column as `.metadata` (see comment above).
StoreBlueprint.metadata = property(lambda self: self.extra_metadata, lambda self, value: setattr(self, "extra_metadata", value))
