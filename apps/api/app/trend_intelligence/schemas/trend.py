"""
Pydantic Schemas for Trend Intelligence API

This module defines Pydantic models for request validation and response serialization.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class CollectionStatus(str, Enum):
    """Enumeration of collection statuses."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TrendItemCreate(BaseModel):
    """Schema for creating a trend item."""
    trend_id: str = Field(..., description="Unique trend identifier")
    source: str = Field(..., description="Data source provider")
    product_name: str = Field(..., min_length=1, max_length=255, description="Product name")
    brand: Optional[str] = Field(None, max_length=255, description="Brand name")
    category: str = Field(..., min_length=1, max_length=100, description="Product category")
    tags: List[str] = Field(default_factory=list, description="Associated tags")
    popularity_score: float = Field(..., ge=0, le=100, description="Popularity score")
    growth_score: float = Field(..., ge=0, le=100, description="Growth score")
    competition_score: float = Field(..., ge=0, le=100, description="Competition score")
    opportunity_score: float = Field(..., ge=0, le=100, description="Opportunity score")
    confidence_score: float = Field(..., ge=0, le=100, description="Confidence score")
    detected_at: datetime = Field(default_factory=datetime.utcnow, description="Detection timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @validator('tags')
    def validate_tags(cls, v):
        """Validate tags are not empty strings."""
        return [tag for tag in v if tag.strip()]


class TrendItemUpdate(BaseModel):
    """Schema for updating a trend item."""
    product_name: Optional[str] = Field(None, max_length=255)
    brand: Optional[str] = Field(None, max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    popularity_score: Optional[float] = Field(None, ge=0, le=100)
    growth_score: Optional[float] = Field(None, ge=0, le=100)
    competition_score: Optional[float] = Field(None, ge=0, le=100)
    opportunity_score: Optional[float] = Field(None, ge=0, le=100)
    confidence_score: Optional[float] = Field(None, ge=0, le=100)
    overall_score: Optional[float] = Field(None, ge=0, le=100)
    component_scores: Optional[Dict[str, float]] = None
    weighted_scores: Optional[Dict[str, float]] = None
    metadata: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    is_processed: Optional[bool] = None


class TrendItemResponse(BaseModel):
    """Schema for trend item response."""
    id: int
    trend_id: str
    source: str
    product_name: str
    brand: Optional[str]
    category: str
    tags: List[str]
    popularity_score: float
    growth_score: float
    competition_score: float
    opportunity_score: float
    confidence_score: float
    overall_score: float
    component_scores: Optional[Dict[str, float]]
    weighted_scores: Optional[Dict[str, float]]
    metadata: Dict[str, Any]
    detected_at: datetime
    collected_at: datetime
    scored_at: Optional[datetime]
    is_active: bool
    is_processed: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TrendListResponse(BaseModel):
    """Schema for paginated trend list response."""
    items: List[TrendItemResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class CollectionRequest(BaseModel):
    """Schema for requesting a trend collection."""
    provider: str = Field(..., description="Provider name (e.g., 'mock', 'google_trends')")
    category: Optional[str] = Field(None, description="Filter by category")
    limit: int = Field(default=50, ge=1, le=1000, description="Maximum items to collect")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Additional provider parameters")
    
    @validator('provider')
    def validate_provider(cls, v):
        """Validate provider name."""
        if not v or not v.strip():
            raise ValueError("Provider name cannot be empty")
        return v.lower().strip()


class CollectionResponse(BaseModel):
    """Schema for collection response."""
    collection_id: str
    provider: str
    status: CollectionStatus
    items_collected: int
    items_processed: int
    items_failed: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: Optional[float]
    error_message: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ScoreRecalculateRequest(BaseModel):
    """Schema for requesting score recalculation."""
    trend_ids: Optional[List[str]] = Field(None, description="Specific trend IDs to recalculate")
    category: Optional[str] = Field(None, description="Recalculate all trends in category")
    min_overall_score: Optional[float] = Field(None, ge=0, le=100, description="Minimum overall score")
    recalculate_all: bool = Field(default=False, description="Recalculate all active trends")
    force: bool = Field(default=False, description="Force recalculation even if recently scored")


class ScoreRecalculateResponse(BaseModel):
    """Schema for score recalculation response."""
    job_id: str
    trends_queued: int
    status: str
    message: str


class TrendFilterParams(BaseModel):
    """Schema for trend filtering parameters."""
    source: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    min_overall_score: Optional[float] = Field(None, ge=0, le=100)
    max_overall_score: Optional[float] = Field(None, ge=0, le=100)
    min_growth_score: Optional[float] = Field(None, ge=0, le=100)
    min_opportunity_score: Optional[float] = Field(None, ge=0, le=100)
    max_competition_score: Optional[float] = Field(None, ge=0, le=100)
    is_active: Optional[bool] = None
    is_processed: Optional[bool] = None
    tags: Optional[List[str]] = None
    detected_after: Optional[datetime] = None
    detected_before: Optional[datetime] = None


class TrendAnalyticsResponse(BaseModel):
    """Schema for trend analytics response."""
    total_trends: int
    active_trends: int
    average_overall_score: float
    top_categories: List[Dict[str, Any]]
    top_sources: List[Dict[str, Any]]
    score_distribution: Dict[str, int]
    recent_trends: int
    growth_trends: int


class ProviderInfo(BaseModel):
    """Schema for provider information."""
    name: str
    description: str
    available: bool
    last_collection: Optional[datetime]
    total_collections: int
    average_items_per_collection: Optional[float]


class ProviderListResponse(BaseModel):
    """Schema for provider list response."""
    providers: List[ProviderInfo]
