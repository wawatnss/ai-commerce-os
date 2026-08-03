"""Tests for StripeService._checkout_completed() (checkout.session.completed)."""
import pytest

from app.billing.models import UserSubscription
from config import settings


@pytest.fixture(autouse=True)
def configured_price_ids(monkeypatch):
    monkeypatch.setattr(settings, "STRIPE_PRICE_ID_FREE", "price_free_test")
    monkeypatch.setattr(settings, "STRIPE_PRICE_ID_PRO", "price_pro_test")
    monkeypatch.setattr(settings, "STRIPE_PRICE_ID_BUSINESS", "price_business_test")


def _checkout_session_event(user_id, price_id, customer="cus_test_1", subscription="sub_test_1"):
    """Shape of `event["data"]["object"]` for checkout.session.completed."""
    return {
        "id": "cs_test_1",
        "customer": customer,
        "subscription": subscription,
        "metadata": {"user_id": str(user_id), "price_id": price_id},
    }


def test_checkout_completed_creates_pro_subscription(stripe_service, db_session, user):
    stripe_service._checkout_completed(_checkout_session_event(user.id, "price_pro_test"))

    sub = db_session.query(UserSubscription).filter(UserSubscription.user_id == user.id).one()
    assert sub.plan == "pro"
    assert sub.status == "active"
    assert sub.stripe_customer_id == "cus_test_1"
    assert sub.stripe_subscription_id == "sub_test_1"
    assert sub.stripe_price_id == "price_pro_test"


def test_checkout_completed_maps_business_price(stripe_service, db_session, user):
    stripe_service._checkout_completed(_checkout_session_event(user.id, "price_business_test"))

    sub = db_session.query(UserSubscription).filter(UserSubscription.user_id == user.id).one()
    assert sub.plan == "business"


def test_checkout_completed_maps_free_price(stripe_service, db_session, user):
    stripe_service._checkout_completed(_checkout_session_event(user.id, "price_free_test"))

    sub = db_session.query(UserSubscription).filter(UserSubscription.user_id == user.id).one()
    assert sub.plan == "free"


def test_checkout_completed_upgrades_existing_subscription_in_place(stripe_service, db_session, user):
    stripe_service._checkout_completed(_checkout_session_event(user.id, "price_free_test", subscription="sub_free"))
    stripe_service._checkout_completed(_checkout_session_event(user.id, "price_pro_test", subscription="sub_pro"))

    subs = db_session.query(UserSubscription).filter(UserSubscription.user_id == user.id).all()
    assert len(subs) == 1  # updated in place, not duplicated
    assert subs[0].plan == "pro"
    assert subs[0].stripe_subscription_id == "sub_pro"


def test_checkout_completed_unknown_price_id_fails_safely(stripe_service, db_session, user):
    """An unrecognized price_id must never crash the webhook or guess a plan."""
    stripe_service._checkout_completed(_checkout_session_event(user.id, "price_totally_unknown"))

    sub = db_session.query(UserSubscription).filter(UserSubscription.user_id == user.id).first()
    assert sub is None


def test_checkout_completed_missing_price_id_fails_safely(stripe_service, db_session, user):
    stripe_service._checkout_completed(_checkout_session_event(user.id, price_id=None))

    sub = db_session.query(UserSubscription).filter(UserSubscription.user_id == user.id).first()
    assert sub is None


def test_checkout_completed_unknown_price_after_existing_subscription_leaves_it_untouched(
    stripe_service, db_session, user
):
    stripe_service._checkout_completed(_checkout_session_event(user.id, "price_pro_test"))
    stripe_service._checkout_completed(_checkout_session_event(user.id, "price_unknown_xyz", subscription="sub_new"))

    sub = db_session.query(UserSubscription).filter(UserSubscription.user_id == user.id).one()
    assert sub.plan == "pro"
    assert sub.stripe_subscription_id == "sub_test_1"
