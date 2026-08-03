"""Tests for BillingService's plan-limit enforcement: AI credits,
max_generations, and max_exports, across the free/pro/business plans and at
their exact boundaries. Pure unit tests against an isolated SQLite DB - no
network, no Stripe API, no Render.
"""
import pytest

from app.billing.models import UsageCounter
from app.billing.plans import PLANS
from app.billing.tests.conftest import set_plan


# ---------------------------------------------------------------------------
# remaining_* on a brand-new user (no usage recorded yet)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("plan_slug", ["free", "pro", "business"])
def test_remaining_generations_defaults_to_plan_limit(billing, db_session, user, plan_slug):
    set_plan(db_session, user.id, plan_slug)
    expected = PLANS[plan_slug].max_generations
    assert billing.remaining_generations(user.id) == expected


@pytest.mark.parametrize("plan_slug", ["free", "pro", "business"])
def test_remaining_exports_defaults_to_plan_limit(billing, db_session, user, plan_slug):
    set_plan(db_session, user.id, plan_slug)
    expected = PLANS[plan_slug].max_exports
    assert billing.remaining_exports(user.id) == expected


@pytest.mark.parametrize("plan_slug", ["free", "pro", "business"])
def test_remaining_ai_credits_defaults_to_plan_limit(billing, db_session, user, plan_slug):
    set_plan(db_session, user.id, plan_slug)
    expected = PLANS[plan_slug].ai_credits
    assert billing.remaining_ai_credits(user.id) == expected


# ---------------------------------------------------------------------------
# max_generations - enforced globally, regardless of AI usage
# ---------------------------------------------------------------------------

def test_free_plan_can_generate_up_to_its_limit(billing, db_session, user):
    set_plan(db_session, user.id, "free")
    limit = PLANS["free"].max_generations  # 5

    for _ in range(limit):
        assert billing.can_generate(user.id, use_ai=False) is True
        billing.record_generation(user.id, use_ai=False)

    # Exactly at the boundary: the limit-th generation was allowed, the
    # (limit+1)-th must not be.
    assert billing.remaining_generations(user.id) == 0
    assert billing.can_generate(user.id, use_ai=False) is False


def test_pro_plan_generation_limit(billing, db_session, user):
    set_plan(db_session, user.id, "pro")
    limit = PLANS["pro"].max_generations  # 50

    for _ in range(limit):
        billing.record_generation(user.id, use_ai=False)

    assert billing.remaining_generations(user.id) == 0
    assert billing.can_generate(user.id, use_ai=False) is False


def test_business_plan_has_unlimited_generations(billing, db_session, user):
    set_plan(db_session, user.id, "business")

    # Business's max_generations is the -1 "unlimited" sentinel; recording a
    # very large number of generations must never exhaust it.
    for _ in range(1000):
        billing.record_generation(user.id, use_ai=False)

    assert billing.remaining_generations(user.id) == -1
    assert billing.can_generate(user.id, use_ai=False) is True


def test_generation_limit_applies_even_without_ai(billing, db_session, user):
    """max_generations must be enforced globally - AI-less generations count too."""
    set_plan(db_session, user.id, "free")
    for _ in range(PLANS["free"].max_generations):
        billing.record_generation(user.id, use_ai=False)

    assert billing.can_generate(user.id, use_ai=False) is False


# ---------------------------------------------------------------------------
# AI credits - decremented only on AI-backed generations, reject when exhausted
# ---------------------------------------------------------------------------

def test_free_plan_has_zero_ai_credits_and_cannot_use_ai_at_all(billing, db_session, user):
    set_plan(db_session, user.id, "free")

    assert billing.remaining_ai_credits(user.id) == 0
    # Generation slots are available (5 on free), but AI credits are not.
    assert billing.remaining_generations(user.id) > 0
    assert billing.can_generate(user.id, use_ai=True) is False
    # A non-AI generation must still be allowed.
    assert billing.can_generate(user.id, use_ai=False) is True


def test_pro_plan_ai_credits_decrement_and_reject_when_exhausted(billing, db_session, user):
    """pro's max_generations (50) is far smaller than its ai_credits (500),
    so the AI-credit boundary is tested directly by seeding the counter
    close to its limit rather than looping hundreds of real generations
    (which would hit the *generation* limit first and test the wrong
    thing)."""
    set_plan(db_session, user.id, "pro")
    limit = PLANS["pro"].ai_credits  # 500

    usage = UsageCounter(user_id=user.id, ai_credits_used=limit - 1)
    db_session.add(usage)
    db_session.commit()

    assert billing.remaining_ai_credits(user.id) == 1
    assert billing.can_generate(user.id, use_ai=True) is True
    billing.record_generation(user.id, use_ai=True)

    assert billing.remaining_ai_credits(user.id) == 0
    assert billing.can_generate(user.id, use_ai=True) is False


def test_business_plan_ai_credits_are_capped_not_unlimited(billing, db_session, user):
    """Unlike max_stores/max_exports/max_generations, business's ai_credits
    is a real cap (5000), not the -1 unlimited sentinel."""
    set_plan(db_session, user.id, "business")
    limit = PLANS["business"].ai_credits  # 5000
    assert limit != -1

    usage = db_session.query(UsageCounter).filter(UsageCounter.user_id == user.id).first()
    if not usage:
        usage = UsageCounter(user_id=user.id)
        db_session.add(usage)
    usage.ai_credits_used = limit
    db_session.commit()

    assert billing.remaining_ai_credits(user.id) == 0
    assert billing.can_generate(user.id, use_ai=True) is False
    # Non-AI generations are unaffected (business generations are unlimited).
    assert billing.can_generate(user.id, use_ai=False) is True


def test_record_generation_only_consumes_ai_credit_when_use_ai_true(billing, db_session, user):
    set_plan(db_session, user.id, "pro")

    billing.record_generation(user.id, use_ai=False)
    usage = db_session.query(UsageCounter).filter(UsageCounter.user_id == user.id).one()
    assert usage.generations_used == 1
    assert usage.ai_credits_used == 0

    billing.record_generation(user.id, use_ai=True)
    db_session.refresh(usage)
    assert usage.generations_used == 2
    assert usage.ai_credits_used == billing.AI_CREDITS_PER_GENERATION


# ---------------------------------------------------------------------------
# max_exports - enforced globally
# ---------------------------------------------------------------------------

def test_free_plan_export_limit(billing, db_session, user):
    set_plan(db_session, user.id, "free")
    limit = PLANS["free"].max_exports  # 1

    assert billing.can_export(user.id) is True
    billing.record_export(user.id)

    assert billing.remaining_exports(user.id) == 0
    assert billing.can_export(user.id) is False


def test_pro_plan_export_limit(billing, db_session, user):
    set_plan(db_session, user.id, "pro")
    limit = PLANS["pro"].max_exports  # 10

    for _ in range(limit):
        assert billing.can_export(user.id) is True
        billing.record_export(user.id)

    assert billing.remaining_exports(user.id) == 0
    assert billing.can_export(user.id) is False


def test_business_plan_has_unlimited_exports(billing, db_session, user):
    set_plan(db_session, user.id, "business")

    for _ in range(1000):
        billing.record_export(user.id)

    assert billing.remaining_exports(user.id) == -1
    assert billing.can_export(user.id) is True


# ---------------------------------------------------------------------------
# Misc / fallback behavior
# ---------------------------------------------------------------------------

def test_unknown_plan_falls_back_to_free_limits(billing, db_session, user):
    set_plan(db_session, user.id, "some-plan-that-does-not-exist")

    assert billing.remaining_generations(user.id) == PLANS["free"].max_generations
    assert billing.remaining_exports(user.id) == PLANS["free"].max_exports
    assert billing.remaining_ai_credits(user.id) == PLANS["free"].ai_credits


def test_usage_counters_are_isolated_per_user(billing, db_session, user):
    other = user.__class__(email="other.billing.test@example.com", hashed_password="x")
    db_session.add(other)
    db_session.commit()
    db_session.refresh(other)

    set_plan(db_session, user.id, "free")
    set_plan(db_session, other.id, "free")

    for _ in range(PLANS["free"].max_generations):
        billing.record_generation(user.id, use_ai=False)

    assert billing.can_generate(user.id, use_ai=False) is False
    assert billing.can_generate(other.id, use_ai=False) is True


def test_get_or_create_usage_is_idempotent(billing, db_session, user):
    first = billing.get_or_create_usage(user.id)
    second = billing.get_or_create_usage(user.id)
    assert first.id == second.id
    assert db_session.query(UsageCounter).filter(UsageCounter.user_id == user.id).count() == 1
