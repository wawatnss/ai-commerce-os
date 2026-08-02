"""
REST API Router for the Demo module.

This module provides a single endpoint that runs the whole platform pipeline
end-to-end (Trend -> Product -> Supplier -> Brand -> Store -> Preview) using
only local, rule-based logic - no external AI provider or third-party data
source is ever called.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from ..services.demo_service import DemoService
from ..schemas.demo import DemoGenerateResponse

router = APIRouter(prefix="/api/v1/demo", tags=["demo"])


def get_demo_service(db: Session = Depends(get_db)) -> DemoService:
    """Dependency to get demo service instance."""
    return DemoService(db)


@router.post("/generate", response_model=DemoGenerateResponse)
async def generate_demo(service: DemoService = Depends(get_demo_service)):
    """
    Generate a complete demo store from scratch.

    Runs the full pipeline synchronously (it only takes a fraction of a
    second since nothing calls out to the network) and returns the ordered
    list of steps plus the resulting `store_id`, ready to be opened at
    `/store-preview/{store_id}` in apps/store-renderer.
    """
    return await service.generate()
