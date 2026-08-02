"""
REST API Router for Product Intelligence

This module provides FastAPI endpoints for product intelligence operations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from database import get_db
from ..services.product_service import ProductService
from ..engines import ScoreWeights
from ..schemas.product import (
    ProductAnalysisRequest,
    BatchAnalysisRequest,
    ProductIntelligenceReportResponse,
    ProductListResponse,
    ProductFilterParams,
    ProductAnalyticsResponse,
    TopProductsResponse
)

router = APIRouter(prefix="/api/v1/products", tags=["products"])


def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    """Dependency to get product service instance."""
    return ProductService(db)


# Analysis Endpoints

@router.post("/analyze", response_model=ProductIntelligenceReportResponse)
async def analyze_product(
    request: ProductAnalysisRequest,
    service: ProductService = Depends(get_product_service)
):
    """Analyze a product based on trend data."""
    try:
        return service.analyze_product(request.trend_id, request.force_reanalyze)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/analyze/batch")
async def batch_analyze(
    request: BatchAnalysisRequest,
    service: ProductService = Depends(get_product_service)
):
    """Analyze multiple products."""
    return service.batch_analyze(request)


# Report Endpoints

@router.get("/", response_model=ProductListResponse)
async def get_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    min_overall_score: Optional[float] = Query(None, ge=0, le=100),
    max_overall_score: Optional[float] = Query(None, ge=0, le=100),
    recommendation: Optional[str] = Query(None),
    min_confidence_score: Optional[float] = Query(None, ge=0, le=100),
    sort_by: str = Query("overall_score"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    service: ProductService = Depends(get_product_service)
):
    """Get product intelligence reports with pagination and filtering."""
    filters = ProductFilterParams(
        category=category,
        min_overall_score=min_overall_score,
        max_overall_score=max_overall_score,
        recommendation=recommendation,
        min_confidence_score=min_confidence_score
    )
    
    return service.get_reports(
        page=page,
        page_size=page_size,
        filters=filters,
        sort_by=sort_by,
        sort_order=sort_order
    )


@router.get("/{report_id}", response_model=ProductIntelligenceReportResponse)
async def get_report(
    report_id: int,
    service: ProductService = Depends(get_product_service)
):
    """Get a specific product intelligence report."""
    report = service.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


# Dashboard Endpoints

@router.get("/top", response_model=TopProductsResponse)
async def get_top_products(
    limit: int = Query(100, ge=1, le=1000),
    min_score: float = Query(60, ge=0, le=100),
    service: ProductService = Depends(get_product_service)
):
    """Get top products by overall score."""
    return service.get_top_products(limit=limit, min_score=min_score)


@router.get("/analytics", response_model=ProductAnalyticsResponse)
async def get_analytics(
    service: ProductService = Depends(get_product_service)
):
    """Get product intelligence analytics."""
    return service.get_analytics()


# Configuration Endpoints

@router.post("/weights")
async def update_weights(
    weights: ScoreWeights,
    service: ProductService = Depends(get_product_service)
):
    """Update scoring weights."""
    success = service.update_weights(weights)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid weights")
    return {"success": True, "message": "Weights updated successfully"}
