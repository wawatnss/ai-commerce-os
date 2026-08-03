"""Tests for StripeService._subscription_deleted() (customer.subscription.deleted)."""
from app.billing.models import UserSubscription


def _existing_subscription(
    db_session, user, plan="pro", status="active", stripe_subscription_id="sub_1", stripe_customer_id="cus_1"
):
    sub = UserSubscription(
        user_id=user.id,
        plan=plan,
        status=status,
        stripe_customer_id=stripe_customer_id,
        stripe_subscription_id=stripe_subscription_id,
    )
    db_session.add(sub)
    db_session.commit()
    db_session.refresh(sub)
    return sub


def _subscription_deleted_event(sub_id, customer, ended_at=None):
    """Shape of `event["data"]["object"]` for customer.subscription.deleted."""
    return {"id": sub_id, "customer": customer, "status": "canceled", "ended_at": ended_at}


def test_subscription_deleted_marks_cancelled_without_deleting_row(stripe_service, db_session, user):
    _existing_subscription(db_session, user)

    stripe_service._subscription_deleted(_subscription_deleted_event("sub_1", "cus_1"))

    db_session.expire_all()
    # The row must still exist - historical data is preserved, never deleted.
    sub = db_session.query(UserSubscription).filter(UserSubscription.user_id == user.id).one()
    assert sub.status == "canceled"
    assert sub.plan == "pro"  # plan history preserved, not reset to free


def test_subscription_deleted_records_ended_at_as_expires_at(stripe_service, db_session, user):
    _existing_subscription(db_session, user)
    ended_at = 1798761600  # 2027-01-01T00:00:00Z

    stripe_service._subscription_deleted(_subscription_deleted_event("sub_1", "cus_1", ended_at=ended_at))

    db_session.expire_all()
    sub = db_session.query(UserSubscription).filter(UserSubscription.user_id == user.id).one()
    assert sub.expires_at is not None


def test_subscription_deleted_unknown_subscription_is_ignored(stripe_service, db_session, user):
    stripe_service._subscription_deleted(_subscription_deleted_event("sub_ghost", "cus_ghost"))

    assert db_session.query(UserSubscription).count() == 0


def test_subscription_deleted_falls_back_to_customer_id_match(stripe_service, db_session, user):
    _existing_subscription(db_session, user, stripe_subscription_id=None, stripe_customer_id="cus_1")

    stripe_service._subscription_deleted(_subscription_deleted_event("sub_unknown_at_delete_time", "cus_1"))

    db_session.expire_all()
    sub = db_session.query(UserSubscription).filter(UserSubscription.user_id == user.id).one()
    assert sub.status == "canceled"


def test_subscription_deleted_does_not_reduce_row_count(stripe_service, db_session, user):
    _existing_subscription(db_session, user)

    before = db_session.query(UserSubscription).count()
    stripe_service._subscription_deleted(_subscription_deleted_event("sub_1", "cus_1"))
    after = db_session.query(UserSubscription).count()

    assert before == after == 1
