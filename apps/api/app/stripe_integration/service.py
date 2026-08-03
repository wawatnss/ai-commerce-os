"""Stripe integration service."""
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.auth.models import User
from app.billing.models import UserSubscription
from app.billing.service import BillingService
from config import settings

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
            # `price_id` is echoed back in checkout.session.completed's metadata
            # so the webhook handler can map it to a local plan without an
            # extra Stripe API call.
            metadata={"user_id": str(user.id), "price_id": price_id},
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

    def _map_price_id_to_plan(self, price_id: Optional[str]) -> Optional[str]:
        """Map a Stripe Price ID to an internal plan slug, or None if unknown."""
        if not price_id:
            return None
        mapping = {
            getattr(settings, "STRIPE_PRICE_ID_FREE", None): "free",
            getattr(settings, "STRIPE_PRICE_ID_PRO", None): "pro",
            getattr(settings, "STRIPE_PRICE_ID_BUSINESS", None): "business",
        }
        mapping.pop(None, None)  # ignore any tier whose price ID isn't configured
        return mapping.get(price_id)

    def _extract_price_id(self, subscription: dict) -> Optional[str]:
        items = (subscription.get("items") or {}).get("data") or []
        if items:
            price = items[0].get("price") or {}
            return price.get("id")
        return None

    def _find_local_subscription(self, subscription: dict) -> Optional[UserSubscription]:
        """Look up the local row for a Stripe subscription object.

        Matched by `stripe_subscription_id` first, falling back to
        `stripe_customer_id` (e.g. for a subscription we haven't seen the ID
        of yet). Returns None if neither matches - the caller must handle
        that case explicitly rather than assume a row always exists.
        """
        sub_id = subscription.get("id")
        customer_id = subscription.get("customer")
        query = self.db.query(UserSubscription)
        found = None
        if sub_id:
            found = query.filter(UserSubscription.stripe_subscription_id == sub_id).first()
        if not found and customer_id:
            found = query.filter(UserSubscription.stripe_customer_id == customer_id).first()
        return found

    def _checkout_completed(self, session: dict):
        user_id = int(session.get("metadata", {}).get("user_id", 0))
        price_id = session.get("metadata", {}).get("price_id")
        plan = self._map_price_id_to_plan(price_id)
        if not plan:
            logger.warning(
                "checkout.session.completed for user_id=%s references an unknown or missing "
                "price_id=%r; leaving subscription untouched.",
                user_id, price_id,
            )
            return

        billing = BillingService(self.db)
        sub = billing.get_or_create_subscription(user_id, plan)
        sub.plan = plan
        sub.status = "active"
        sub.stripe_customer_id = session.get("customer")
        sub.stripe_subscription_id = session.get("subscription")
        sub.stripe_price_id = price_id
        self.db.commit()

    def _subscription_updated(self, subscription: dict):
        """Sync plan, status, and expires_at from a customer.subscription.updated event."""
        sub = self._find_local_subscription(subscription)
        if not sub:
            logger.warning(
                "customer.subscription.updated for unknown Stripe subscription_id=%s "
                "customer=%s; ignoring.",
                subscription.get("id"), subscription.get("customer"),
            )
            return

        price_id = self._extract_price_id(subscription)
        plan = self._map_price_id_to_plan(price_id)
        if plan:
            sub.plan = plan
            sub.stripe_price_id = price_id
        else:
            logger.warning(
                "customer.subscription.updated for subscription_id=%s references an unknown "
                "price_id=%r; keeping existing plan=%r.",
                subscription.get("id"), price_id, sub.plan,
            )

        sub.status = subscription.get("status", sub.status)
        sub.stripe_subscription_id = subscription.get("id") or sub.stripe_subscription_id
        sub.stripe_customer_id = subscription.get("customer") or sub.stripe_customer_id

        current_period_end = subscription.get("current_period_end")
        if current_period_end:
            sub.expires_at = datetime.fromtimestamp(current_period_end, tz=timezone.utc)

        self.db.commit()

    def _subscription_deleted(self, subscription: dict):
        """Mark the local subscription cancelled. Never deletes the row - historical
        plan/usage data must be preserved."""
        sub = self._find_local_subscription(subscription)
        if not sub:
            logger.warning(
                "customer.subscription.deleted for unknown Stripe subscription_id=%s "
                "customer=%s; ignoring.",
                subscription.get("id"), subscription.get("customer"),
            )
            return

        sub.status = "canceled"
        ended_at = subscription.get("ended_at") or subscription.get("canceled_at")
        if ended_at:
            sub.expires_at = datetime.fromtimestamp(ended_at, tz=timezone.utc)
        self.db.commit()
