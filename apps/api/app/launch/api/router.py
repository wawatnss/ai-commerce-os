"""
REST API Router for the Launch module.

Powers the admin dashboard's "Create a new brand" wizard: a single endpoint
runs the whole pipeline (Trend -> Product -> Supplier -> Brand -> Store ->
Optimize) from the name/category/objective/budget the user provided.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.billing.service import BillingService
from database import get_db
from ..services.launch_service import LaunchService
from ..schemas.launch import LaunchRequest, LaunchResponse

router = APIRouter(prefix="/api/v1/launch", tags=["launch"])


def get_launch_service(db: Session = Depends(get_db)) -> LaunchService:
    """Dependency to get launch service instance."""
    return LaunchService(db)


@router.post("/generate", response_model=LaunchResponse)
async def generate_launch(
    request: LaunchRequest,
    current_user: User = Depends(get_current_user),
    service: LaunchService = Depends(get_launch_service)
):
    """
    Create a new brand end-to-end from the wizard's name/category/objective/
    budget, and return the ordered list of pipeline steps plus the resulting
    `store_id`.
    """
    billing = BillingService(service.db)
    if not billing.can_create_store(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Store limit reached for your plan. Please upgrade."
        )
    return await service.generate(request, current_user.id)
