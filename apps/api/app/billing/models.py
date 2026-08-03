"""Billing and subscription models."""
import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from app.auth.base import Base


class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    plan = Column(String, nullable=False, default="free")
    status = Column(String, nullable=False, default="active")  # active, canceled, past_due
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    stripe_customer_id = Column(String, nullable=True, index=True)
    stripe_subscription_id = Column(String, nullable=True, unique=True, index=True)
    stripe_price_id = Column(String, nullable=True)


class UsageCounter(Base):
    """Persistent, monotonically-increasing usage counters for plan-limit
    enforcement (AI credits, generations, exports). One row per user.

    Counters are never reset automatically by this module - resetting them
    (e.g. on a monthly billing cycle) is a separate concern left for later.
    """
    __tablename__ = "usage_counters"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    ai_credits_used = Column(Integer, nullable=False, default=0)
    generations_used = Column(Integer, nullable=False, default=0)
    exports_used = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
