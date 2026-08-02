"""
REST API Router for Brand Builder

This module provides FastAPI endpoints for brand generation operations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from ..services.brand_service import BrandService
from ..schemas.brand import BrandCreateRequest, BrandResponse, ValidationResponse

router = APIRouter(prefix="/api/v1/brands", tags=["brands"])


def get_brand_service(db: Session = Depends(get_db)) -> BrandService:
    """Dependency to get brand service instance."""
    return BrandService(db)


@router.post("/generate", response_model=BrandResponse)
async def generate_brand(
    request: BrandCreateRequest,
    service: BrandService = Depends(get_brand_service)
):
    """Generate a complete brand profile."""
    try:
        return await service.generate_brand(request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{brand_id}", response_model=BrandResponse)
async def get_brand(
    brand_id: int,
    service: BrandService = Depends(get_brand_service)
):
    """Get a specific brand profile."""
    brand = service.repository.get_brand_by_id(brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return BrandResponse.from_orm(brand)


@router.get("/", response_model=dict)
async def list_brands(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: BrandService = Depends(get_brand_service)
):
    """List all brand profiles."""
    skip = (page - 1) * page_size
    brands, total = service.repository.list_brands(skip, page_size)
    
    return {
        "items": [BrandResponse.from_orm(b) for b in brands],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.post("/{brand_id}/validate", response_model=ValidationResponse)
async def validate_brand(
    brand_id: int,
    service: BrandService = Depends(get_brand_service)
):
    """Validate a brand profile."""
    try:
        return service.validate_brand(brand_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{brand_id}/export")
async def export_brand(
    brand_id: int,
    service: BrandService = Depends(get_brand_service)
):
    """Export a complete brand profile as JSON."""
    try:
        return service.export_brand(brand_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
