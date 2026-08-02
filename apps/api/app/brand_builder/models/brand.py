"""
Database Models for Brand Builder

This module defines SQLAlchemy models for storing brand profiles.
"""

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, Index, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional, Dict, Any, List

Base = declarative_base()


class BrandProfile(Base):
    """
    Database model for brand profiles.
    
    Stores complete brand identity generated from product and supplier intelligence.
    """
    __tablename__ = "brand_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String(255), nullable=False, index=True, comment="Associated product ID")
    supplier_id = Column(String(255), nullable=True, index=True, comment="Associated supplier ID")
    
    # Brand Identity
    brand_name = Column(String(255), nullable=False, index=True, comment="Brand name")
    slogan = Column(String(500), nullable=True, comment="Brand slogan")
    mission = Column(Text, nullable=True, comment="Brand mission")
    vision = Column(Text, nullable=True, comment="Brand vision")
    
    # Audience
    target_audience = Column(String(255), nullable=True, comment="Target audience segment")
    customer_persona = Column(JSON, nullable=True, comment="Detailed customer persona")
    
    # Voice and Style
    tone_of_voice = Column(String(255), nullable=True, comment="Primary tone of voice")
    writing_style = Column(JSON, nullable=True, comment="Writing style guidelines")
    
    # Visual Identity
    color_palette = Column(JSON, nullable=True, comment="Color palette with hex codes")
    typography = Column(JSON, nullable=True, comment="Typography recommendations")
    
    # AI Prompts for Design
    logo_prompt = Column(Text, nullable=True, comment="Logo design prompt")
    packaging_prompt = Column(Text, nullable=True, comment="Packaging design prompt")
    product_photography_prompt = Column(Text, nullable=True, comment="Product photography prompt")
    hero_banner_prompt = Column(Text, nullable=True, comment="Hero banner prompt")
    
    # Communication Style
    social_media_style = Column(Text, nullable=True, comment="Social media style guidelines")
    seo_style = Column(Text, nullable=True, comment="SEO writing style")
    email_style = Column(Text, nullable=True, comment="Email writing style")
    
    # Positioning
    trust_elements = Column(JSON, nullable=True, comment="Trust-building elements")
    unique_value_proposition = Column(JSON, nullable=True, comment="Unique value proposition")
    differentiators = Column(JSON, nullable=True, comment="Competitive differentiators")
    domain_name_suggestions = Column(JSON, nullable=True, comment="Domain name suggestions")
    
    # Validation
    confidence_score = Column(Float, nullable=False, default=0.0, comment="Overall confidence score")
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
        Index('idx_brand_product_supplier', 'product_id', 'supplier_id'),
        Index('idx_brand_name', 'brand_name'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "product_id": self.product_id,
            "supplier_id": self.supplier_id,
            "brand_name": self.brand_name,
            "slogan": self.slogan,
            "mission": self.mission,
            "vision": self.vision,
            "target_audience": self.target_audience,
            "customer_persona": self.customer_persona or {},
            "tone_of_voice": self.tone_of_voice,
            "writing_style": self.writing_style or {},
            "color_palette": self.color_palette or {},
            "typography": self.typography or {},
            "logo_prompt": self.logo_prompt,
            "packaging_prompt": self.packaging_prompt,
            "product_photography_prompt": self.product_photography_prompt,
            "hero_banner_prompt": self.hero_banner_prompt,
            "social_media_style": self.social_media_style,
            "seo_style": self.seo_style,
            "email_style": self.email_style,
            "trust_elements": self.trust_elements or [],
            "unique_value_proposition": self.unique_value_proposition or {},
            "differentiators": self.differentiators or [],
            "domain_name_suggestions": self.domain_name_suggestions or [],
            "confidence_score": self.confidence_score,
            "validation_result": self.validation_result or {},
            "metadata": self.metadata or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# Re-expose the "metadata" column as `.metadata` (see comment above).
BrandProfile.metadata = property(lambda self: self.extra_metadata, lambda self, value: setattr(self, "extra_metadata", value))
