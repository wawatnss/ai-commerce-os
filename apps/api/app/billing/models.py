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
