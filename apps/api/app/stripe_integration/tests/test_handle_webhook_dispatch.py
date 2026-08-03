"""Tests for StripeService.handle_webhook()'s event-type dispatch.

`stripe.Webhook.construct_event` is mocked in every test here: no real
signature cryptography and no network call is ever performed. This covers
the same dispatch code path `POST /api/v1/billing/webhook` uses.
"""
import stripe
import pytest
from fastapi import HTTPException

from app.billing.models import UserSubscription
from config import settings


@pytest.fixture(autouse=True)
def configured_price_ids(monkeypatch):
    monkeypatch.setattr(settings, "STRIPE_PRICE_ID_PRO", "price_pro_test")


def _mock_construct_event(monkeypatch, event: dict):
    monkeypatch.setattr(stripe.Webhook, "construct_event", staticmethod(lambda payload, sig_header, secret: event))


def test_handle_webhook_checkout_session_completed(stripe_service, db_session, user, monkeypatch):
    event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_1",
                "customer": "cus_1",
                "subscription": "sub_1",
                "metadata": {"user_id": str(user.id), "price_id": "price_pro_test"},
            }
        },
    }
    _mock_construct_event(monkeypatch, event)

    result = stripe_service.handle_webhook(b"{}", "t=1,v1=fake", "whsec_test")

    assert result == {"status": "ok"}
    sub = db_session.query(UserSubscription).filter(UserSubscription.user_id == user.id).one()
    assert sub.plan == "pro"
    assert sub.status == "active"


def test_handle_webhook_subscription_updated(stripe_service, db_session, user, monkeypatch):
    existing = UserSubscription(
        user_id=user.id, plan="pro", status="active",
        stripe_subscription_id="sub_1", stripe_customer_id="cus_1",
    )
    db_session.add(existing)
    db_session.commit()

    event = {
        "type": "customer.subscription.updated",
        "data": {
            "object": {
                "id": "sub_1",
                "customer": "cus_1",
                "status": "past_due",
                "items": {"data": [{"price": {"id": "price_pro_test"}}]},
            }
        },
    }
    _mock_construct_event(monkeypatch, event)

    result = stripe_service.handle_webhook(b"{}", "t=1,v1=fake", "whsec_test")

    assert result == {"status": "ok"}
    db_session.expire_all()
    updated = db_session.query(UserSubscription).filter(UserSubscription.user_id == user.id).one()
    assert updated.status == "past_due"


def test_handle_webhook_subscription_deleted(stripe_service, db_session, user, monkeypatch):
    existing = UserSubscription(
        user_id=user.id, plan="pro", status="active",
        stripe_subscription_id="sub_1", stripe_customer_id="cus_1",
    )
    db_session.add(existing)
    db_session.commit()

    event = {
        "type": "customer.subscription.deleted",
        "data": {"object": {"id": "sub_1", "customer": "cus_1", "status": "canceled"}},
    }
    _mock_construct_event(monkeypatch, event)

    result = stripe_service.handle_webhook(b"{}", "t=1,v1=fake", "whsec_test")

    assert result == {"status": "ok"}
    db_session.expire_all()
    deleted = db_session.query(UserSubscription).filter(UserSubscription.user_id == user.id).one()
    assert deleted.status == "canceled"
    assert deleted.plan == "pro"  # preserved - row is never deleted


def test_handle_webhook_invalid_signature_returns_400(stripe_service, monkeypatch):
    def _raise(payload, sig_header, secret):
        raise stripe.error.SignatureVerificationError("bad sig", "header")

    monkeypatch.setattr(stripe.Webhook, "construct_event", staticmethod(_raise))

    with pytest.raises(HTTPException) as exc_info:
        stripe_service.handle_webhook(b"{}", "bad-header", "whsec_test")

    assert exc_info.value.status_code == 400


def test_handle_webhook_unconfigured_stripe_is_ignored(db_session, monkeypatch):
    from app.stripe_integration.service import StripeService

    unconfigured_service = StripeService(db_session, secret_key=None)
    result = unconfigured_service.handle_webhook(b"{}", "t=1,v1=fake", "whsec_test")

    assert result == {"status": "ignored", "reason": "stripe not configured"}
