"""Shared fixtures for the app/auth test suite.

Design goals (see task requirements):
- Every test gets a brand-new, isolated SQLite database file - never the
  real Postgres/Render database.
- No Redis, no SMTP, no outbound network calls of any kind.
- Deterministic: no shared mutable state leaks between tests.
- Production code is not modified to make this possible; isolation is
  achieved entirely from the test side via FastAPI's
  `app.dependency_overrides` mechanism and `monkeypatch`.
"""
import importlib
import sys
import uuid
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# apps/api must be importable so that `import main`, `from config import
# settings`, `from database import get_db`, etc. (all written as absolute
# imports rooted at apps/api) resolve correctly, regardless of the cwd
# pytest was invoked from.
_API_ROOT = Path(__file__).resolve().parents[3]
if str(_API_ROOT) not in sys.path:
    sys.path.insert(0, str(_API_ROOT))

import main  # noqa: E402
from app.auth import models as _auth_models  # noqa: E402,F401  (registers User on AuthBase)
from app.auth.base import Base as AuthBase  # noqa: E402
from database import get_db  # noqa: E402

# `app/auth/__init__.py` does `from app.auth.router import router`, which
# rebinds the `router` *attribute* on the `app.auth` package to the
# `APIRouter` instance, shadowing the `router` *submodule* for any
# attribute-chain-based resolution - including `import app.auth.router as x`
# and `monkeypatch.setattr("app.auth.router....")`, both of which resolve
# dotted names via getattr(), not via `sys.modules`. Pulling the module
# straight out of `sys.modules` (populated by the import machinery under the
# exact key "app.auth.router", independent of that later attribute rebind)
# sidesteps the shadowing entirely.
importlib.import_module("app.auth.router")
auth_router_module = sys.modules["app.auth.router"]


@pytest.fixture()
def db_session(tmp_path):
    """A fresh, file-backed SQLite database, unique to this test.

    A real file (not `sqlite:///:memory:`) is used so that every
    `Depends(get_db)` call during the test - however many separate
    connections/requests it triggers - sees the same schema and data,
    without needing a custom connection pool.
    """
    db_path = tmp_path / f"test_auth_{uuid.uuid4().hex}.db"
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
def client(db_session):
    """A TestClient wired to the isolated per-test database."""

    def _override_get_db():
        yield db_session

    main.app.dependency_overrides[get_db] = _override_get_db
    # The global per-IP rate limiter in main.py keys off `request.client.host`,
    # which TestClient always reports as the same fake host. Clear it before
    # each test so no test's request budget is affected by tests that ran
    # before it, keeping the suite deterministic regardless of run order.
    main._request_log.clear()
    try:
        with TestClient(main.app) as test_client:
            yield test_client
    finally:
        main.app.dependency_overrides.pop(get_db, None)


@pytest.fixture(autouse=True)
def mock_email_service(monkeypatch):
    """Replace `EmailService` used by the auth router with a mock.

    Guarantees zero SMTP/HTTP calls from these tests while still letting
    tests assert whether a given "send" method was (or wasn't) invoked.

    Patched on the module object pulled from `sys.modules` (see
    `auth_router_module` above) rather than via the dotted string
    `"app.auth.router.EmailService"`, to avoid the `router`
    attribute-shadowing issue described above.
    """
    mock_cls = MagicMock(name="EmailServiceClass")
    monkeypatch.setattr(auth_router_module, "EmailService", mock_cls)
    return mock_cls


@pytest.fixture()
def register_user(client):
    """Helper: register a user via the real endpoint and return (email, password)."""

    def _register(email: str = "user@example.com", password: str = "SuperSecret123!"):
        resp = client.post("/api/v1/auth/register", json={"email": email, "password": password})
        assert resp.status_code == 201, resp.text
        return email, password

    return _register
