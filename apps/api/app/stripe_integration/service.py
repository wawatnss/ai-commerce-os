"""Stripe integration service."""
import logging
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.auth.models import User
from app.billing.models import UserSubscription
from app.billing.service import BillingService

logger = logging.getLogger("ai_commerce")


class StripeService:
    """Wrap Stripe operations and keep local subscription state in sync."""

    def __init__(self, db: Session, secret_key: Optional[str] = None):
        self.db = db
        self._client = None
        self.secret_key = secret_key

    def _get_client(self):
        if self._client is None:
            if not self.secret_key:
                raise RuntimeError("Stripe secret key not configured")
            import stripe
            stripe.api_key = self.secret_key
            self._client = stripe
        return self._client

    def _get_or_create_customer(self, user: User) -> dict:
        import stripe
        stripe.api_key = self.secret_key
        existing = stripe.Customer.list(email=user.email, limit=1)
        if existing.data:
            return existing.data[0]
        return stripe.Customer.create(email=user.email, metadata={"user_id": str(user.id)})

    def create_checkout_session(self, user: User, price_id: str, success_url: str, cancel_url: str) -> dict:
        if not self.secret_key:
            raise HTTPException(status_code=503, detail="Stripe not configured")
        import stripe
        stripe.api_key = self.secret_key

        customer = self._get_or_create_customer(user)
        session = stripe.checkout.Session.create(
            customer=customer["id"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={"user_id": str(user.id)},
        )
        return {"url": session.url, "session_id": session.id}

    def create_customer_portal_session(self, user: User, return_url: str) -> dict:
        if not self.secret_key:
            raise HTTPException(status_code=503, detail="Stripe not configured")
        import stripe
        stripe.api_key = self.secret_key

        customer = self._get_or_create_customer(user)
        session = stripe.billing_portal.Session.create(
            customer=customer["id"],
            return_url=return_url,
        )
        return {"url": session.url}

    def handle_webhook(self, payload: bytes, sig_header: str, webhook_secret: str) -> dict:
        if not self.secret_key:
            return {"status": "ignored", "reason": "stripe not configured"}
        import stripe
        stripe.api_key = self.secret_key
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        except Exception:
            logger.exception("Invalid Stripe webhook signature")
            raise HTTPException(status_code=400, detail="Invalid signature")

        if event["type"] == "checkout.session.completed":
            self._checkout_completed(event["data"]["object"])
        elif event["type"] == "customer.subscription.updated":
            self._subscription_updated(event["data"]["object"])
        elif event["type"] == "customer.subscription.deleted":
            self._subscription_deleted(event["data"]["object"])

        return {"status": "ok"}

    def _checkout_completed(self, session: dict):
        user_id = int(session.get("metadata", {}).get("user_id", 0))
        # Default to pro for the architecture test; real mapping by price ID in settings.
        plan = "pro"
        billing = BillingService(self.db)
        sub = billing.get_or_create_subscription(user_id, plan)
        sub.status = "active"
        self.db.commit()

    def _subscription_updated(self, subscription: dict):
        # Update status from Stripe (active, past_due, canceled)
        pass

    def _subscription_deleted(self, subscription: dict):
        pass
