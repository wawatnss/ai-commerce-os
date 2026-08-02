"""Stripe integration router."""
from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.stripe_integration.service import StripeService
from config import settings
from database import get_db

router = APIRouter(prefix="/api/v1/billing", tags=["billing"])


def _get_stripe_service(db: Session = Depends(get_db)) -> StripeService:
    return StripeService(db, secret_key=getattr(settings, "STRIPE_SECRET_KEY", None))


@router.post("/checkout")
def create_checkout(
    price_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success_url = f"{settings.PUBLIC_ADMIN_URL}/?checkout=success"
    cancel_url = f"{settings.PUBLIC_ADMIN_URL}/?checkout=cancel"
    return StripeService(db, getattr(settings, "STRIPE_SECRET_KEY", None)).create_checkout_session(user, price_id, success_url, cancel_url)


@router.post("/customer-portal")
def customer_portal(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return_url = f"{settings.PUBLIC_ADMIN_URL}/"
    return StripeService(db, getattr(settings, "STRIPE_SECRET_KEY", None)).create_customer_portal_session(user, return_url)


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None),
    db: Session = Depends(get_db)
):
    payload = await request.body()
    secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", None)
    return StripeService(db, getattr(settings, "STRIPE_SECRET_KEY", None)).handle_webhook(payload, stripe_signature, secret)
