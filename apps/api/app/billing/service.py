"""Billing and usage service."""
from typing import Optional
from sqlalchemy.orm import Session

from app.billing.models import UserSubscription, UsageCounter
from app.billing.plans import PLANS
from app.store_builder.repositories.store_repository import StoreRepository

UNLIMITED = -1  # sentinel used throughout app/billing/plans.py for "no limit"


class BillingService:
    """Manage user subscriptions and enforce plan limits."""

    # Flat AI-credit cost of a single AI-backed generation call. Kept as a
    # class constant rather than per-engine token accounting so it stays
    # simple, deterministic, and testable without calling a real AI provider.
    AI_CREDITS_PER_GENERATION = 1

    def __init__(self, db: Session):
        self.db = db

    def get_or_create_subscription(self, user_id: int, plan: str = "free") -> UserSubscription:
        sub = self.db.query(UserSubscription).filter(UserSubscription.user_id == user_id).first()
        if not sub:
            sub = UserSubscription(user_id=user_id, plan=plan)
            self.db.add(sub)
            self.db.commit()
            self.db.refresh(sub)
        return sub

    def get_or_create_usage(self, user_id: int) -> UsageCounter:
        usage = self.db.query(UsageCounter).filter(UsageCounter.user_id == user_id).first()
        if not usage:
            usage = UsageCounter(user_id=user_id)
            self.db.add(usage)
            self.db.commit()
            self.db.refresh(usage)
        return usage

    def _plan_for(self, user_id: int):
        sub = self.get_or_create_subscription(user_id)
        return PLANS.get(sub.plan, PLANS["free"])

    def can_create_store(self, user_id: int) -> bool:
        sub = self.get_or_create_subscription(user_id)
        plan = PLANS.get(sub.plan, PLANS["free"])
        if plan.max_stores == UNLIMITED:
            return True
        store_count, _ = StoreRepository(self.db).list_stores_by_user(user_id, limit=9999)
        return len(store_count) < plan.max_stores

    # -- AI credits -----------------------------------------------------

    def remaining_ai_credits(self, user_id: int) -> int:
        """Remaining AI credits for this billing period, or -1 if unlimited."""
        plan = self._plan_for(user_id)
        if plan.ai_credits == UNLIMITED:
            return UNLIMITED
        usage = self.get_or_create_usage(user_id)
        return max(0, plan.ai_credits - usage.ai_credits_used)

    # -- Generations ------------------------------------------------------

    def remaining_generations(self, user_id: int) -> int:
        """Remaining generation actions for this billing period, or -1 if unlimited."""
        plan = self._plan_for(user_id)
        if plan.max_generations == UNLIMITED:
            return UNLIMITED
        usage = self.get_or_create_usage(user_id)
        return max(0, plan.max_generations - usage.generations_used)

    def can_generate(self, user_id: int, use_ai: bool = False) -> bool:
        """Whether the user may perform one more generation action.

        `max_generations` is enforced regardless of `use_ai`. If the
        generation is AI-backed, `ai_credits` is additionally enforced -
        a plan can have generation slots left but zero AI credits (e.g.
        the free plan), in which case an AI-backed generation must still
        be rejected.
        """
        remaining_gen = self.remaining_generations(user_id)
        if remaining_gen != UNLIMITED and remaining_gen <= 0:
            return False
        if use_ai:
            remaining_credits = self.remaining_ai_credits(user_id)
            if remaining_credits != UNLIMITED and remaining_credits <= 0:
                return False
        return True

    def record_generation(self, user_id: int, use_ai: bool = False) -> UsageCounter:
        """Record that a generation action happened. Must only be called
        after a successful generation, and after `can_generate()` was
        checked - this method does not itself enforce the limit."""
        usage = self.get_or_create_usage(user_id)
        usage.generations_used += 1
        if use_ai:
            usage.ai_credits_used += self.AI_CREDITS_PER_GENERATION
        self.db.commit()
        self.db.refresh(usage)
        return usage

    # -- Exports ----------------------------------------------------------

    def remaining_exports(self, user_id: int) -> int:
        """Remaining export actions for this billing period, or -1 if unlimited."""
        plan = self._plan_for(user_id)
        if plan.max_exports == UNLIMITED:
            return UNLIMITED
        usage = self.get_or_create_usage(user_id)
        return max(0, plan.max_exports - usage.exports_used)

    def can_export(self, user_id: int) -> bool:
        remaining = self.remaining_exports(user_id)
        return remaining == UNLIMITED or remaining > 0

    def record_export(self, user_id: int) -> UsageCounter:
        """Record that an export action happened. Must only be called after
        a successful export, and after `can_export()` was checked."""
        usage = self.get_or_create_usage(user_id)
        usage.exports_used += 1
        self.db.commit()
        self.db.refresh(usage)
        return usage

    def get_plan(self, user_id: int) -> dict:
        sub = self.get_or_create_subscription(user_id)
        plan = PLANS.get(sub.plan, PLANS["free"])
        store_count, _ = StoreRepository(self.db).list_stores_by_user(user_id, limit=9999)
        return {
            "plan": plan.slug,
            "name": plan.name,
            "status": sub.status,
            "max_stores": plan.max_stores,
            "stores_used": len(store_count),
            "max_exports": plan.max_exports,
            "max_generations": plan.max_generations,
            "ai_credits": plan.ai_credits,
            "support": plan.support,
        }
