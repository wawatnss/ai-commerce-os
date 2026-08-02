"""
REST API Router for Supplier Intelligence

This module provides FastAPI endpoints for supplier intelligence operations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from database import get_db
from ..services.supplier_service import SupplierService
from ..engines import ScoreWeights
from ..schemas.supplier import (
    SupplierCreate,
    SupplierResponse,
    SupplierEvaluationResponse,
    EvaluationRequest,
    ComparisonRequest,
    ComparisonResponse,
    BestOffersResponse
)

router = APIRouter(prefix="/api/v1/suppliers", tags=["suppliers"])


def get_supplier_service(db: Session = Depends(get_db)) -> SupplierService:
    """Dependency to get supplier service instance."""
    return SupplierService(db)


# Supplier Management

@router.post("/", response_model=SupplierResponse)
async def create_supplier(
    supplier_data: SupplierCreate,
    service: SupplierService = Depends(get_supplier_service)
):
    """Create a new supplier."""
    return service.create_supplier(supplier_data.dict())


# Offer Management

@router.post("/offers/import")
async def import_offers(
    product_id: str = Query(...),
    supplier_ids: Optional[List[str]] = Query(None),
    service: SupplierService = Depends(get_supplier_service)
):
    """Import offers from data providers."""
    return service.import_offers(product_id, supplier_ids)


# Evaluation Endpoints

@router.post("/evaluate", response_model=SupplierEvaluationResponse)
async def evaluate_supplier(
    request: EvaluationRequest,
    service: SupplierService = Depends(get_supplier_service)
):
    """Evaluate a supplier for a product."""
    try:
        return service.evaluate_supplier(request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/compare", response_model=ComparisonResponse)
async def compare_suppliers(
    request: ComparisonRequest,
    service: SupplierService = Depends(get_supplier_service)
):
    """Compare multiple suppliers for a product."""
    return service.compare_suppliers(request)


# Best Offers

@router.get("/best", response_model=BestOffersResponse)
async def get_best_offers(
    product_id: str = Query(...),
    limit: int = Query(10, ge=1, le=100),
    service: SupplierService = Depends(get_supplier_service)
):
    """Get best offers for a product."""
    return service.get_best_offers(product_id, limit)


# Configuration

@router.post("/weights")
async def update_weights(
    weights: ScoreWeights,
    service: SupplierService = Depends(get_supplier_service)
):
    """Update scoring weights."""
    success = service.score_engine.update_weights(weights)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid weights")
    return {"success": True, "message": "Weights updated successfully"}
