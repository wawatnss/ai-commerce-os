"""
Pydantic Schemas for Brand Builder

This module defines the request/response schemas for the Brand Builder API.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class BrandCreateRequest(BaseModel):
    """Schema for creating a brand."""
    product_id: str = Field(..., description="Product ID from Product Intelligence")
    supplier_id: Optional[str] = Field(None, description="Supplier ID from Supplier Intelligence")
    force_regenerate: bool = Field(default=False, description="Force regeneration even if brand exists")
    use_ai: bool = Field(default=True, description="Use AI provider for generation")


class BrandResponse(BaseModel):
    """Schema for brand response."""
    id: int
    product_id: str
    supplier_id: Optional[str]
    brand_name: str
    slogan: Optional[str]
    mission: Optional[str]
    vision: Optional[str]
    target_audience: Optional[str]
    customer_persona: Optional[Dict[str, Any]]
    tone_of_voice: Optional[str]
    writing_style: Optional[Dict[str, Any]]
    color_palette: Optional[Dict[str, Any]]
    typography: Optional[Dict[str, Any]]
    logo_prompt: Optional[str]
    packaging_prompt: Optional[str]
    product_photography_prompt: Optional[str]
    hero_banner_prompt: Optional[str]
    social_media_style: Optional[str]
    seo_style: Optional[str]
    email_style: Optional[str]
    trust_elements: Optional[List[str]]
    unique_value_proposition: Optional[Dict[str, Any]]
    differentiators: Optional[List[str]]
    domain_name_suggestions: Optional[List[str]]
    confidence_score: float
    validation_result: Optional[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BrandExport(BaseModel):
    """Schema for complete brand export."""
    brand_profile: BrandResponse
    source_data: Dict[str, Any] = Field(default_factory=dict, description="Source product and supplier data")
    export_timestamp: datetime = Field(default_factory=datetime.utcnow)


class ValidationResponse(BaseModel):
    """Schema for validation response."""
    overall_score: float
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    coherence_score: float
    readability_score: float
    uniqueness_score: float
    marketing_coherence_score: float
    seo_coherence_score: float
