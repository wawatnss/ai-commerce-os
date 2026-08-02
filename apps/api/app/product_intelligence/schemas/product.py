"""
Pydantic Schemas for Product Intelligence

This module defines the request/response schemas for the Product Intelligence API.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class Recommendation(str, Enum):
    """Recommendation levels."""
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    HOLD = "hold"
    AVOID = "avoid"


class ProductIntelligenceReportCreate(BaseModel):
    """Schema for creating a product intelligence report."""
    trend_id: str = Field(..., description="Associated trend ID")
    product_name: str = Field(..., min_length=1, max_length=255, description="Product name")
    category: str = Field(..., min_length=1, max_length=100, description="Product category")
    trend_data: Dict[str, Any] = Field(..., description="Original trend data")


class ProductIntelligenceReportUpdate(BaseModel):
    """Schema for updating a product intelligence report."""
    overall_score: Optional[float] = Field(None, ge=0, le=100)
    recommendation: Optional[Recommendation] = None
    reasoning: Optional[str] = None
    rule_results: Optional[Dict[str, Any]] = None


class ProductIntelligenceReportResponse(BaseModel):
    """Schema for product intelligence report response."""
    id: int
    trend_id: str
    product_name: str
    category: str
    
    # Individual scores
    estimated_margin_score: float
    demand_score: float
    competition_score: float
    shipping_complexity_score: float
    supplier_availability_score: float
    seasonality_score: float
    impulse_buy_score: float
    content_potential_score: float
    seo_potential_score: float
    return_risk_score: float
    legal_risk_score: float
    
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
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProductAnalysisRequest(BaseModel):
    """Schema for requesting product analysis."""
    trend_id: str = Field(..., description="Trend ID to analyze")
    force_reanalyze: bool = Field(default=False, description="Force reanalysis even if recent report exists")


class BatchAnalysisRequest(BaseModel):
    """Schema for batch analysis request."""
    trend_ids: Optional[List[str]] = Field(None, description="Specific trend IDs to analyze")
    category: Optional[str] = Field(None, description="Analyze all trends in category")
    min_overall_score: Optional[float] = Field(None, ge=0, le=100, description="Minimum trend score")
    analyze_all: bool = Field(default=False, description="Analyze all active trends")
    force_reanalyze: bool = Field(default=False, description="Force reanalysis")


class ProductFilterParams(BaseModel):
    """Schema for filtering product reports."""
    category: Optional[str] = None
    min_overall_score: Optional[float] = Field(None, ge=0, le=100)
    max_overall_score: Optional[float] = Field(None, ge=0, le=100)
    recommendation: Optional[Recommendation] = None
    min_confidence_score: Optional[float] = Field(None, ge=0, le=100)
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None


class ProductListResponse(BaseModel):
    """Schema for paginated product list response."""
    items: List[ProductIntelligenceReportResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ProductAnalyticsResponse(BaseModel):
    """Schema for product analytics response."""
    total_reports: int
    average_overall_score: float
    average_confidence_score: float
    recommendation_distribution: Dict[str, int]
    top_categories: List[Dict[str, Any]]
    score_distribution: Dict[str, int]
    recent_analyses: int
    high_opportunity_products: int


class TopProductsResponse(BaseModel):
    """Schema for top products response."""
    products: List[ProductIntelligenceReportResponse]
    count: int
    criteria: str


class ScoreEvolutionResponse(BaseModel):
    """Schema for score evolution response."""
    trend_id: str
    product_name: str
    scores: List[Dict[str, Any]]
