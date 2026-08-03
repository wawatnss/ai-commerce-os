"""Shared fixtures for the app/billing test suite.

- Every test gets a fresh, isolated SQLite database file - never the real
  Postgres/Render database.
- No Stripe API calls, no real AI provider/network calls: endpoint-level
  tests monkeypatch the generation service methods instead of running the
  real engine pipelines (which is exactly what those AI-provider-agnostic
  billing checks are meant to gate, not what they need to re-test).
"""
import sys
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

_API_ROOT = Path(__file__).resolve().parents[3]
if str(_API_ROOT) not in sys.path:
    sys.path.insert(0, str(_API_ROOT))

import main  # noqa: E402
from app.auth.base import Base as AuthBase  # noqa: E402
from app.auth.models import User  # noqa: E402
from app.auth.dependencies import get_current_user, get_current_user_optional  # noqa: E402
import app.billing.models  # noqa: E402,F401  (registers UserSubscription/UsageCounter on AuthBase)
from app.billing.models import UserSubscription  # noqa: E402
from app.billing.service import BillingService  # noqa: E402
from app.store_builder.models.store import Base as StoreBase  # noqa: E402
from app.brand_builder.models.brand import Base as BrandBase  # noqa: E402
from database import get_db  # noqa: E402


@pytest.fixture()
def db_session(tmp_path):
    """A fresh, file-backed SQLite database, unique to this test."""
    db_path = tmp_path / f"test_billing_{uuid.uuid4().hex}.db"
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    AuthBase.metadata.create_all(bind=engine)
    StoreBase.metadata.create_all(bind=engine)
    BrandBase.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def billing(db_session):
    return BillingService(db_session)


@pytest.fixture()
def user(db_session):
    u = User(email="billing.test@example.com", hashed_password="not-a-real-hash")
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


def set_plan(db_session, user_id: int, plan: str):
    """Test helper: force a user's subscription onto a specific plan."""
    sub = db_session.query(UserSubscription).filter(UserSubscription.user_id == user_id).first()
    if sub:
        sub.plan = plan
    else:
        sub = UserSubscription(user_id=user_id, plan=plan, status="active")
        db_session.add(sub)
    db_session.commit()
    return sub


@pytest.fixture()
def client(db_session, user):
    """A TestClient authenticated as `user`, wired to the isolated per-test DB."""

    def _override_get_db():
        yield db_session

    main.app.dependency_overrides[get_db] = _override_get_db
    main.app.dependency_overrides[get_current_user] = lambda: user
    main.app.dependency_overrides[get_current_user_optional] = lambda: user
    main._request_log.clear()
    try:
        with TestClient(main.app) as test_client:
            yield test_client
    finally:
        main.app.dependency_overrides.pop(get_db, None)
        main.app.dependency_overrides.pop(get_current_user, None)
        main.app.dependency_overrides.pop(get_current_user_optional, None)
