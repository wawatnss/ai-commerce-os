"""Billing and usage service."""
from typing import Optional
from sqlalchemy.orm import Session

from app.billing.models import UserSubscription
from app.billing.plans import PLANS
from app.store_builder.repositories.store_repository import StoreRepository


class BillingService:
    """Manage user subscriptions and enforce plan limits."""

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

    def can_create_store(self, user_id: int) -> bool:
        sub = self.get_or_create_subscription(user_id)
        plan = PLANS.get(sub.plan, PLANS["free"])
        if plan.max_stores == -1:
            return True
        store_count, _ = StoreRepository(self.db).list_stores_by_user(user_id, limit=9999)
        return len(store_count) < plan.max_stores

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
