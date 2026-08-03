"""Shared fixtures for the app/stripe_integration test suite.

- Every test gets a fresh, isolated SQLite database file - never the real
  Postgres/Render database.
- No real Stripe API calls are made anywhere in this suite: the DB-sync
  methods (`_checkout_completed`, `_subscription_updated`,
  `_subscription_deleted`) never touch the network by themselves, and
  `handle_webhook()` tests mock `stripe.Webhook.construct_event` instead of
  performing real signature cryptography or any HTTP call.
"""
import sys
import uuid
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

_API_ROOT = Path(__file__).resolve().parents[3]
if str(_API_ROOT) not in sys.path:
    sys.path.insert(0, str(_API_ROOT))

from app.auth.base import Base as AuthBase  # noqa: E402
from app.auth.models import User  # noqa: E402
import app.billing.models  # noqa: E402,F401  (registers UserSubscription on AuthBase)
from app.stripe_integration.service import StripeService  # noqa: E402


@pytest.fixture()
def db_session(tmp_path):
    """A fresh, file-backed SQLite database, unique to this test."""
    db_path = tmp_path / f"test_stripe_{uuid.uuid4().hex}.db"
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    AuthBase.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def user(db_session):
    """A real local user row, matching what a Stripe customer would be tied to."""
    u = User(email="stripe.customer@example.com", hashed_password="not-a-real-hash")
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


@pytest.fixture()
def stripe_service(db_session):
    # A non-empty fake secret key is enough to exercise handle_webhook()'s
    # dispatch logic; the real Stripe API is never called in this suite.
    return StripeService(db_session, secret_key="sk_test_fake")
