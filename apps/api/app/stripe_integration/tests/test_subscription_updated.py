"""Tests for StripeService._subscription_updated() (customer.subscription.updated)."""
from datetime import datetime, timezone

import pytest

from app.billing.models import UserSubscription
from config import settings


@pytest.fixture(autouse=True)
def configured_price_ids(monkeypatch):
    monkeypatch.setattr(settings, "STRIPE_PRICE_ID_FREE", "price_free_test")
    monkeypatch.setattr(settings, "STRIPE_PRICE_ID_PRO", "price_pro_test")
    monkeypatch.setattr(settings, "STRIPE_PRICE_ID_BUSINESS", "price_business_test")


def _existing_subscription(
    db_session, user, plan="pro", status="active", stripe_subscription_id="sub_1", stripe_customer_id="cus_1"
):
    sub = UserSubscription(
        user_id=user.id,
        plan=plan,
        status=status,
        stripe_customer_id=stripe_customer_id,
        stripe_subscription_id=stripe_subscription_id,
        stripe_price_id="price_pro_test",
    )
    db_session.add(sub)
    db_session.commit()
    db_session.refresh(sub)
    return sub


def _subscription_updated_event(sub_id, customer, price_id, status="active", current_period_end=None):
    """Shape of `event["data"]["object"]` for customer.subscription.updated."""
    return {
        "id": sub_id,
        "customer": customer,
        "status": status,
        "items": {"data": [{"price": {"id": price_id}}]},
        "current_period_end": current_period_end,
    }


def test_subscription_updated_syncs_plan_status_and_expiry(stripe_service, db_session, user):
    _existing_subscription(db_session, user)
    period_end = int(datetime(2027, 1, 1, tzinfo=timezone.utc).timestamp())

    stripe_service._subscription_updated(
        _subscription_updated_event("sub_1", "cus_1", "price_business_test", status="active", current_period_end=period_end)
    )

    db_session.expire_all()
    sub = db_session.query(UserSubscription).filter(UserSubscription.user_id == user.id).one()
    assert sub.plan == "business"
    assert sub.status == "active"
    assert sub.expires_at.replace(tzinfo=None) == datetime(2027, 1, 1)


def test_subscription_updated_falls_back_to_customer_id_match(stripe_service, db_session, user):
    _existing_subscription(db_session, user, stripe_subscription_id=None, stripe_customer_id="cus_1")

    stripe_service._subscription_updated(
        _subscription_updated_event("sub_new_id", "cus_1", "price_pro_test", status="active")
    )

    db_session.expire_all()
    sub = db_session.query(UserSubscription).filter(UserSubscription.user_id == user.id).one()
    assert sub.stripe_subscription_id == "sub_new_id"


def test_subscription_updated_unknown_subscription_is_ignored(stripe_service, db_session, user):
    stripe_service._subscription_updated(
        _subscription_updated_event("sub_ghost", "cus_ghost", "price_pro_test", status="active")
    )

    assert db_session.query(UserSubscription).count() == 0


def test_subscription_updated_unknown_price_id_keeps_existing_plan(stripe_service, db_session, user):
    _existing_subscription(db_session, user, plan="pro")

    stripe_service._subscription_updated(
        _subscription_updated_event("sub_1", "cus_1", "price_totally_unknown", status="past_due")
    )

    db_session.expire_all()
    sub = db_session.query(UserSubscription).filter(UserSubscription.user_id == user.id).one()
    assert sub.plan == "pro"  # unchanged - unknown price never clobbers a known plan
    assert sub.status == "past_due"  # status still syncs independently of plan mapping


def test_subscription_updated_status_transitions_to_past_due(stripe_service, db_session, user):
    _existing_subscription(db_session, user, status="active")

    stripe_service._subscription_updated(
        _subscription_updated_event("sub_1", "cus_1", "price_pro_test", status="past_due")
    )

    db_session.expire_all()
    sub = db_session.query(UserSubscription).filter(UserSubscription.user_id == user.id).one()
    assert sub.status == "past_due"


def test_subscription_updated_without_current_period_end_keeps_existing_expiry(stripe_service, db_session, user):
    sub = _existing_subscription(db_session, user)
    sub.expires_at = datetime(2026, 6, 1)
    db_session.commit()

    stripe_service._subscription_updated(
        _subscription_updated_event("sub_1", "cus_1", "price_pro_test", status="active", current_period_end=None)
    )

    db_session.expire_all()
    updated = db_session.query(UserSubscription).filter(UserSubscription.user_id == user.id).one()
    assert updated.expires_at == datetime(2026, 6, 1)
