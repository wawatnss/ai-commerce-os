"""
REST API Router for Trend Intelligence

This module provides FastAPI endpoints for trend intelligence operations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any

from database import get_db
from ..services.trend_service import TrendService
from ..schemas.trend import (
    TrendItemCreate,
    TrendItemUpdate,
    TrendItemResponse,
    TrendListResponse,
    CollectionRequest,
    CollectionResponse,
    ScoreRecalculateRequest,
    ScoreRecalculateResponse,
    TrendFilterParams,
    TrendAnalyticsResponse,
    ProviderListResponse
)

router = APIRouter(prefix="/api/v1/trends", tags=["trends"])


def get_trend_service(db: Session = Depends(get_db)) -> TrendService:
    """
    Dependency to get trend service instance.
    
    Args:
        db: Database session
        
    Returns:
        TrendService instance
    """
    return TrendService(db)


# Trend CRUD Endpoints

@router.get("/", response_model=TrendListResponse)
async def get_trends(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    source: Optional[str] = Query(None, description="Filter by source"),
    category: Optional[str] = Query(None, description="Filter by category"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    min_overall_score: Optional[float] = Query(None, ge=0, le=100, description="Minimum overall score"),
    max_overall_score: Optional[float] = Query(None, ge=0, le=100, description="Maximum overall score"),
    min_growth_score: Optional[float] = Query(None, ge=0, le=100, description="Minimum growth score"),
    min_opportunity_score: Optional[float] = Query(None, ge=0, le=100, description="Minimum opportunity score"),
    max_competition_score: Optional[float] = Query(None, ge=0, le=100, description="Maximum competition score"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_processed: Optional[bool] = Query(None, description="Filter by processed status"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    sort_by: str = Query("overall_score", description="Field to sort by"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    service: TrendService = Depends(get_trend_service)
):
    """
    Get trends with pagination and filtering.
    
    Returns a paginated list of trends with optional filtering by various criteria.
    """
    filters = TrendFilterParams(
        source=source,
        category=category,
        brand=brand,
        min_overall_score=min_overall_score,
        max_overall_score=max_overall_score,
        min_growth_score=min_growth_score,
        min_opportunity_score=min_opportunity_score,
        max_competition_score=max_competition_score,
        is_active=is_active,
        is_processed=is_processed,
        tags=tags
    )
    
    return service.get_trends(
        page=page,
        page_size=page_size,
        filters=filters,
        sort_by=sort_by,
        sort_order=sort_order
    )


@router.get("/{trend_id}", response_model=TrendItemResponse)
async def get_trend(
    trend_id: int,
    service: TrendService = Depends(get_trend_service)
):
    """
    Get a specific trend by ID.
    
    Returns detailed information about a specific trend.
    """
    trend = service.get_trend(trend_id)
    if not trend:
        raise HTTPException(status_code=404, detail="Trend not found")
    return trend


@router.post("/", response_model=TrendItemResponse, status_code=201)
async def create_trend(
    trend_data: TrendItemCreate,
    service: TrendService = Depends(get_trend_service)
):
    """
    Create a new trend.
    
    Creates a new trend with automatic score calculation.
    """
    return service.create_trend(trend_data)


@router.put("/{trend_id}", response_model=TrendItemResponse)
async def update_trend(
    trend_id: int,
    update_data: TrendItemUpdate,
    service: TrendService = Depends(get_trend_service)
):
    """
    Update a trend.
    
    Updates an existing trend. Scores are recalculated if score-related fields change.
    """
    trend = service.update_trend(trend_id, update_data)
    if not trend:
        raise HTTPException(status_code=404, detail="Trend not found")
    return trend


@router.delete("/{trend_id}", status_code=204)
async def delete_trend(
    trend_id: int,
    service: TrendService = Depends(get_trend_service)
):
    """
    Delete a trend.
    
    Permanently deletes a trend from the database.
    """
    success = service.delete_trend(trend_id)
    if not success:
        raise HTTPException(status_code=404, detail="Trend not found")


# Collection Endpoints

@router.post("/collect", response_model=CollectionResponse, status_code=202)
async def start_collection(
    request: CollectionRequest,
    background_tasks: BackgroundTasks,
    service: TrendService = Depends(get_trend_service)
):
    """
    Start a trend collection task.
    
    Initiates an asynchronous trend collection from the specified provider.
    The task runs in the background and can be monitored using the collection ID.
    """
    try:
        return await service.start_collection(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/collections/{collection_id}", response_model=CollectionResponse)
async def get_collection(
    collection_id: str,
    service: TrendService = Depends(get_trend_service)
):
    """
    Get collection status.
    
    Returns the current status and results of a collection task.
    """
    collection = service.get_collection(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    return collection


@router.get("/collections/recent", response_model=List[CollectionResponse])
async def get_recent_collections(
    provider: Optional[str] = Query(None, description="Filter by provider"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number to return"),
    service: TrendService = Depends(get_trend_service)
):
    """
    Get recent collection jobs.
    
    Returns a list of the most recent collection jobs.
    """
    return service.get_recent_collections(provider=provider, limit=limit)


# Scoring Endpoints

@router.post("/scores/recalculate", response_model=ScoreRecalculateResponse)
async def recalculate_scores(
    request: ScoreRecalculateRequest,
    service: TrendService = Depends(get_trend_service)
):
    """
    Recalculate trend scores.
    
    Triggers a recalculation of scores for trends based on current scoring weights.
    Can be filtered by specific trends, category, or minimum score.
    """
    return await service.recalculate_scores(request)


# Analytics Endpoints

@router.get("/analytics/summary", response_model=TrendAnalyticsResponse)
async def get_analytics(
    service: TrendService = Depends(get_trend_service)
):
    """
    Get trend analytics.
    
    Returns analytics data including total trends, average scores, top categories, etc.
    """
    return service.get_analytics()


# Provider Endpoints

@router.get("/providers", response_model=ProviderListResponse)
async def get_providers(
    service: TrendService = Depends(get_trend_service)
):
    """
    Get available trend data providers.
    
    Returns a list of registered providers with their status and statistics.
    """
    return service.get_providers()


# Utility Endpoints

@router.post("/cleanup", response_model=Dict[str, int])
async def cleanup_old_trends(
    days: int = Query(30, ge=1, description="Number of days to keep"),
    service: TrendService = Depends(get_trend_service)
):
    """
    Clean up old inactive trends.
    
    Deletes inactive trends older than the specified number of days.
    """
    deleted = service.cleanup_old_trends(days=days)
    return {"deleted": deleted}


@router.get("/cache/stats", response_model=Dict[str, Any])
async def get_cache_stats(
    service: TrendService = Depends(get_trend_service)
):
    """
    Get cache statistics.
    
    Returns Redis cache statistics including memory usage, hit rate, etc.
    """
    return service.get_cache_stats()


@router.post("/cache/clear", status_code=204)
async def clear_cache(
    service: TrendService = Depends(get_trend_service)
):
    """
    Clear all trend-related cache.
    
    Clears all cached trend data. Use with caution in production.
    """
    service.cache.invalidate_all_trends()
