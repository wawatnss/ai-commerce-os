"""
Pydantic Schemas for Supplier Intelligence

This module defines the request/response schemas for the Supplier Intelligence API.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class Recommendation(str, Enum):
    """Recommendation levels."""
    STRONG_RECOMMEND = "strong_recommend"
    RECOMMEND = "recommend"
    CONSIDER = "consider"
    AVOID = "avoid"


class SupplierCreate(BaseModel):
    """Schema for creating a supplier."""
    supplier_id: str = Field(..., description="External supplier ID")
    name: str = Field(..., min_length=1, max_length=255, description="Supplier name")
    source: str = Field(..., description="Data source")
    country: Optional[str] = Field(None, max_length=100, description="Supplier country")
    currency: Optional[str] = Field(None, max_length=10, description="Preferred currency")
    contact: Optional[Dict[str, str]] = Field(None, description="Contact information")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class SupplierOfferCreate(BaseModel):
    """Schema for creating a supplier offer."""
    supplier_id: str = Field(..., description="Supplier ID")
    product_id: str = Field(..., description="Product ID")
    unit_cost: float = Field(..., gt=0, description="Unit cost")
    minimum_order_quantity: int = Field(..., gt=0, description="Minimum order quantity")
    estimated_processing_time: int = Field(..., ge=0, description="Processing time in days")
    estimated_shipping_time: int = Field(..., ge=0, description="Shipping time in days")
    available_quantity: Optional[int] = Field(None, ge=0, description="Available quantity")
    currency: Optional[str] = Field(None, description="Currency")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class SupplierResponse(BaseModel):
    """Schema for supplier response."""
    id: int
    supplier_id: str
    name: str
    source: str
    country: Optional[str]
    currency: Optional[str]
    contact: Optional[Dict[str, str]]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SupplierOfferResponse(BaseModel):
    """Schema for supplier offer response."""
    id: int
    supplier_id: str
    product_id: str
    unit_cost: float
    minimum_order_quantity: int
    estimated_processing_time: int
    estimated_shipping_time: int
    available_quantity: Optional[int]
    currency: Optional[str]
    metadata: Optional[Dict[str, Any]]
    last_updated: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class SupplierEvaluationResponse(BaseModel):
    """Schema for supplier evaluation response."""
    id: int
    supplier_id: str
    product_id: str
    
    # Individual scores
    cost_score: float
    delivery_score: float
    moq_score: float
    availability_score: float
    reliability_score: float
    flexibility_score: float
    data_quality_score: float
    
    # Overall assessment
    overall_score: float
    confidence_score: float
    recommendation: Recommendation
    reasoning: str
    
    # Detailed analysis
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    rule_results: Dict[str, Any] = Field(default_factory=dict)
    
    # Metadata
    rule_config: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class EvaluationRequest(BaseModel):
    """Schema for requesting supplier evaluation."""
    supplier_id: str = Field(..., description="Supplier ID")
    product_id: str = Field(..., description="Product ID")
    force_reevaluate: bool = Field(default=False, description="Force reevaluation")


class ComparisonRequest(BaseModel):
    """Schema for comparing multiple suppliers."""
    product_id: str = Field(..., description="Product ID")
    supplier_ids: List[str] = Field(..., description="Supplier IDs to compare")
    force_reevaluate: bool = Field(default=False, description="Force reevaluation")


class ComparisonResponse(BaseModel):
    """Schema for comparison response."""
    product_id: str
    evaluations: List[SupplierEvaluationResponse]
    best_supplier: Optional[SupplierEvaluationResponse]
    comparison_summary: Dict[str, Any]


class SupplierFilterParams(BaseModel):
    """Schema for filtering suppliers."""
    source: Optional[str] = None
    country: Optional[str] = None
    created_after: Optional[datetime] = None


class EvaluationFilterParams(BaseModel):
    """Schema for filtering evaluations."""
    product_id: Optional[str] = None
    min_overall_score: Optional[float] = Field(None, ge=0, le=100)
    recommendation: Optional[Recommendation] = None
    created_after: Optional[datetime] = None


class BestOffersResponse(BaseModel):
    """Schema for best offers response."""
    product_id: str
    offers: List[SupplierEvaluationResponse]
    count: int
