"""
REST API Router for Store Builder

This module provides FastAPI endpoints for store generation operations.
All endpoints support an optional authenticated user. If a token is provided,
only the user's own stores are returned (or all stores for a superuser).
Without a token, the endpoints fall back to the legacy admin behaviour and
expose all stores.
"""

import json
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import Optional

from app.auth.dependencies import get_current_user_optional
from app.auth.models import User
from app.billing.service import BillingService
from database import get_db
from ..services.store_service import StoreService
from ..services.readiness import ReadinessEngine
from ..services.shopify_readiness import ShopifyReadinessEngine
from ..services.shopify_autofix import ShopifyAutoFixEngine
from ..services.shopify_export import ShopifyExportEngine
from ..schemas.store import StoreCreateRequest, StoreResponse, StoreValidationResponse
from ..schemas.readiness import ReadinessReport
from ..schemas.shopify_readiness import ShopifyReadinessReport
from .renderer import router as renderer_router
from agents.conversion_engine import ConversionEngine

router = APIRouter(prefix="/api/v1/stores", tags=["stores"])

# Include renderer routes
router.include_router(renderer_router)


def get_store_service(db: Session = Depends(get_db)) -> StoreService:
    """Dependency to get store service instance."""
    return StoreService(db)


def _can_access(store, user: Optional[User]) -> bool:
    if user is None or user.is_superuser:
        return True
    return store.user_id == user.id


def _get_authorized_store(store_id: int, user: Optional[User], service: StoreService):
    store = service.repository.get_store_by_id(store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    if not _can_access(store, user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this store")
    return store


@router.post("/generate", response_model=StoreResponse)
async def generate_store(
    request: StoreCreateRequest,
    current_user: User = Depends(get_current_user_optional),
    service: StoreService = Depends(get_store_service)
):
    """Generate a complete store blueprint."""
    if current_user:
        request.user_id = current_user.id
        billing = BillingService(service.db)
        if not billing.can_create_store(current_user.id):
            raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="Store limit reached for your plan")
    try:
        return await service.generate_store(request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{store_id}", response_model=StoreResponse)
async def get_store(
    store_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    service: StoreService = Depends(get_store_service)
):
    """Get a specific store blueprint."""
    store = _get_authorized_store(store_id, current_user, service)
    return StoreResponse.from_orm(store)


@router.get("/", response_model=dict)
async def list_stores(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: Optional[User] = Depends(get_current_user_optional),
    service: StoreService = Depends(get_store_service)
):
    """List store blueprints. Authenticated users only see their own stores (or all if superuser)."""
    skip = (page - 1) * page_size
    if current_user and not current_user.is_superuser:
        stores, total = service.repository.list_stores_by_user(current_user.id, skip, page_size)
    else:
        stores, total = service.repository.list_stores(skip, page_size)

    items = []
    engine = ReadinessEngine()
    shopify_engine = ShopifyReadinessEngine()
    for s in stores:
        item = StoreResponse.from_orm(s)
        item = item.model_dump() if hasattr(item, "model_dump") else item.dict()
        item["readiness"] = engine.run(s.blueprint_json or {}).model_dump()
        item["shopify_readiness"] = shopify_engine.run(s.blueprint_json or {}).model_dump()
        items.append(item)

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.post("/{store_id}/validate", response_model=StoreValidationResponse)
async def validate_store(
    store_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    service: StoreService = Depends(get_store_service)
):
    """Validate a store blueprint."""
    _get_authorized_store(store_id, current_user, service)
    try:
        return service.validate_store(store_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{store_id}/export")
async def export_store(
    store_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    service: StoreService = Depends(get_store_service)
):
    """Export a complete store blueprint as platform-agnostic JSON."""
    _get_authorized_store(store_id, current_user, service)
    try:
        return service.export_store(store_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{store_id}")
async def delete_store(
    store_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    service: StoreService = Depends(get_store_service)
):
    """Delete a store blueprint."""
    _get_authorized_store(store_id, current_user, service)
    success = service.repository.delete_store(store_id)
    if not success:
        raise HTTPException(status_code=404, detail="Store not found")
    return {"message": "Store deleted successfully"}


def _is_demo_store(blueprint: dict) -> bool:
    """Heuristic: DemoService always prefixes its trend/product ids with 'demo-'."""
    return str(blueprint.get("product_id", "")).startswith("demo-")


@router.post("/{store_id}/optimize")
async def optimize_store(
    store_id: int,
    demo_mode: Optional[bool] = Query(
        None,
        description=(
            "Allow simulated review data (never real prices/reviews). "
            "Defaults to auto-detecting demo stores by their product_id."
        ),
    ),
    current_user: Optional[User] = Depends(get_current_user_optional),
    service: StoreService = Depends(get_store_service)
):
    """
    Run the Conversion Optimization Engine (Phase 8) over a store and
    persist the optimized blueprint.
    """
    store = _get_authorized_store(store_id, current_user, service)

    blueprint = store.blueprint_json or {}
    effective_demo_mode = demo_mode if demo_mode is not None else _is_demo_store(blueprint)

    engine = ConversionEngine()
    optimized_blueprint, report = engine.run(blueprint, demo_mode=effective_demo_mode)

    updated_store = service.repository.update_store(store_id, {"blueprint_json": optimized_blueprint})

    return {
        "store_id": store_id,
        "demo_mode": effective_demo_mode,
        "report": report.to_dict(),
        "store": StoreResponse.from_orm(updated_store),
    }


@router.get("/{store_id}/conversion-report")
async def get_conversion_report(
    store_id: int,
    recompute: bool = Query(
        False, description="Recompute instead of returning the cached report (does not persist changes)"
    ),
    current_user: Optional[User] = Depends(get_current_user_optional),
    service: StoreService = Depends(get_store_service)
):
    """Return the conversion report for a store (from cache, or recomputed on demand)."""
    store = _get_authorized_store(store_id, current_user, service)

    blueprint = store.blueprint_json or {}
    if not recompute and blueprint.get("conversion_report"):
        return {"store_id": store_id, "report": blueprint["conversion_report"], "cached": True}

    engine = ConversionEngine()
    _, report = engine.run(blueprint, demo_mode=_is_demo_store(blueprint))
    return {"store_id": store_id, "report": report.to_dict(), "cached": False}


@router.get("/{store_id}/readiness", response_model=ReadinessReport)
async def get_store_readiness(
    store_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    service: StoreService = Depends(get_store_service)
):
    """Return the publication readiness report for a store (computed on demand)."""
    store = _get_authorized_store(store_id, current_user, service)

    report = ReadinessEngine().run(store.blueprint_json or {})
    return report


@router.get("/{store_id}/shopify-readiness", response_model=ShopifyReadinessReport)
async def get_store_shopify_readiness(
    store_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    service: StoreService = Depends(get_store_service)
):
    """Return the Shopify import readiness report for a store (computed on demand)."""
    store = _get_authorized_store(store_id, current_user, service)

    report = ShopifyReadinessEngine().run(store.blueprint_json or {})
    return report


@router.post("/{store_id}/shopify-autofix")
async def shopify_autofix(
    store_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    service: StoreService = Depends(get_store_service)
):
    """Auto-fix the store blueprint to reach a high Shopify readiness score."""
    store = _get_authorized_store(store_id, current_user, service)

    fixed_blueprint = ShopifyAutoFixEngine().run(store.blueprint_json or {})
    updated = service.repository.update_store(store_id, {"blueprint_json": fixed_blueprint})

    report = ShopifyReadinessEngine().run(updated.blueprint_json or {})
    return {
        "store_id": store_id,
        "readiness": report,
    }


@router.get("/{store_id}/export/shopify")
async def export_shopify(
    store_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    service: StoreService = Depends(get_store_service)
):
    """Download a Shopify-compatible export file for a store."""
    store = _get_authorized_store(store_id, current_user, service)

    payload = ShopifyExportEngine().run(store.blueprint_json or {}, store_id)
    body = json.dumps(payload, indent=2, default=str, ensure_ascii=False)

    return Response(
        content=body,
        media_type="application/json",
        headers={
            "Content-Disposition": f'attachment; filename="shopify-export-{store_id}.json"',
        },
    )
