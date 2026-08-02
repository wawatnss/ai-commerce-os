"""
Store Renderer API Endpoint

This module provides the endpoint for triggering store rendering.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from ..repositories.store_repository import StoreRepository

router = APIRouter(prefix="/api/v1/store-renderer", tags=["store-renderer"])


@router.post("/render-store/{store_id}")
async def render_store(
    store_id: int,
    db: Session = Depends(get_db)
):
    """
    Trigger store rendering.
    
    This endpoint signals that a store should be rendered.
    The actual rendering is handled by the Next.js renderer.
    """
    repository = StoreRepository(db)
    store = repository.get_store_by_id(store_id)
    
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    # The Next.js renderer will fetch the store data directly
    # This endpoint is for triggering hot reload or signaling updates
    return {
        "message": "Store ready for rendering",
        "store_id": store_id,
        "preview_url": f"http://localhost:3000/store-preview/{store_id}"
    }
