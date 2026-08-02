"""
Repository for Brand Builder Database Operations

This module handles all database operations for brand profiles.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from ..models.brand import BrandProfile
from ..schemas.brand import BrandCreateRequest


class BrandRepository:
    """Repository for brand profile database operations."""
    
    def __init__(self, db: Session):
        """Initialize the repository."""
        self.db = db
    
    def create_brand(self, brand_data: Dict[str, Any]) -> BrandProfile:
        """Create a new brand profile."""
        db_brand = BrandProfile(
            product_id=brand_data["product_id"],
            supplier_id=brand_data.get("supplier_id"),
            brand_name=brand_data["brand_name"],
            slogan=brand_data.get("slogan"),
            mission=brand_data.get("mission"),
            vision=brand_data.get("vision"),
            target_audience=brand_data.get("target_audience"),
            customer_persona=brand_data.get("customer_persona"),
            tone_of_voice=brand_data.get("tone_of_voice"),
            writing_style=brand_data.get("writing_style"),
            color_palette=brand_data.get("color_palette"),
            typography=brand_data.get("typography"),
            logo_prompt=brand_data.get("logo_prompt"),
            packaging_prompt=brand_data.get("packaging_prompt"),
            product_photography_prompt=brand_data.get("product_photography_prompt"),
            hero_banner_prompt=brand_data.get("hero_banner_prompt"),
            social_media_style=brand_data.get("social_media_style"),
            seo_style=brand_data.get("seo_style"),
            email_style=brand_data.get("email_style"),
            trust_elements=brand_data.get("trust_elements"),
            unique_value_proposition=brand_data.get("unique_value_proposition"),
            differentiators=brand_data.get("differentiators"),
            domain_name_suggestions=brand_data.get("domain_name_suggestions"),
            confidence_score=brand_data.get("confidence_score", 0),
            validation_result=brand_data.get("validation_result"),
            metadata=brand_data.get("metadata", {})
        )
        
        self.db.add(db_brand)
        self.db.commit()
        self.db.refresh(db_brand)
        
        return db_brand
    
    def get_brand_by_product(self, product_id: str) -> Optional[BrandProfile]:
        """Get a brand by product ID."""
        return self.db.query(BrandProfile).filter(
            BrandProfile.product_id == product_id
        ).first()
    
    def get_brand_by_id(self, brand_id: int) -> Optional[BrandProfile]:
        """Get a brand by database ID."""
        return self.db.query(BrandProfile).filter(
            BrandProfile.id == brand_id
        ).first()
    
    def update_brand(self, brand_id: int, update_data: Dict[str, Any]) -> Optional[BrandProfile]:
        """Update a brand profile."""
        db_brand = self.get_brand_by_id(brand_id)
        if not db_brand:
            return None
        
        for field, value in update_data.items():
            if hasattr(db_brand, field):
                setattr(db_brand, field, value)
        
        db_brand.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_brand)
        
        return db_brand
    
    def delete_brand(self, brand_id: int) -> bool:
        """Delete a brand profile."""
        db_brand = self.get_brand_by_id(brand_id)
        if not db_brand:
            return False
        
        self.db.delete(db_brand)
        self.db.commit()
        
        return True
    
    def list_brands(self, skip: int = 0, limit: int = 20) -> tuple[List[BrandProfile], int]:
        """List all brands with pagination."""
        total = self.db.query(BrandProfile).count()
        brands = self.db.query(BrandProfile).order_by(
            desc(BrandProfile.created_at)
        ).offset(skip).limit(limit).all()
        
        return brands, total
