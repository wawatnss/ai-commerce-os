"""
Pydantic Schemas for Store Builder

This module defines the request/response schemas for the Store Builder API.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class StoreCreateRequest(BaseModel):
    """Schema for creating a store."""
    brand_profile_id: str = Field(..., description="Brand profile ID")
    product_id: str = Field(..., description="Product ID")
    supplier_id: Optional[str] = Field(None, description="Supplier ID")
    user_id: Optional[int] = Field(None, description="Owner user ID")
    force_regenerate: bool = Field(default=False, description="Force regeneration")
    use_ai: bool = Field(default=True, description="Use AI for generation")


class StoreResponse(BaseModel):
    """Schema for store response."""
    id: int
    user_id: Optional[int]
    brand_profile_id: str
    product_id: str
    supplier_id: Optional[str]
    store_name: str
    store_description: str
    tagline: Optional[str]
    blueprint_json: Dict[str, Any]
    validation_score: float
    validation_result: Optional[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class StoreValidationResponse(BaseModel):
    """Schema for validation response."""
    overall_score: float
    coherence_score: float
    seo_score: float
    ux_score: float
    accessibility_score: float
    responsive_score: float
    performance_score: float
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]


class StoreExportResponse(BaseModel):
    """Schema for store export."""
    store_blueprint: Dict[str, Any]
    export_format: str = Field(default="json")
    export_timestamp: datetime = Field(default_factory=datetime.utcnow)
