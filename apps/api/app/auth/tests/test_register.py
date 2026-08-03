"""Tests for POST /api/v1/auth/register."""
from app.auth.models import User

REGISTER_URL = "/api/v1/auth/register"


def test_register_success(client, db_session):
    resp = client.post(REGISTER_URL, json={"email": "new.user@example.com", "password": "SuperSecret123!"})

    assert resp.status_code == 201
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str) and body["access_token"]

    user = db_session.query(User).filter(User.email == "new.user@example.com").first()
    assert user is not None
    assert user.email == "new.user@example.com"
    assert user.hashed_password != "SuperSecret123!"  # never store plaintext
    assert user.is_active is True
    assert user.email_verified is False


def test_register_duplicate_email(client, register_user):
    email, password = register_user("duplicate@example.com")

    resp = client.post(REGISTER_URL, json={"email": email, "password": password})

    assert resp.status_code == 400
    assert resp.json()["detail"] == "Email already registered"


def test_register_duplicate_email_case_insensitive(client, register_user):
    register_user("Case.Sensitive@Example.com")

    resp = client.post(
        REGISTER_URL,
        json={"email": "case.sensitive@example.com", "password": "AnotherPass123!"},
    )

    assert resp.status_code == 400


def test_register_invalid_email(client):
    resp = client.post(REGISTER_URL, json={"email": "not-an-email", "password": "SuperSecret123!"})

    assert resp.status_code == 422


def test_register_weak_password(client):
    """UserCreate.password enforces min_length=8 - anything shorter must be rejected."""
    resp = client.post(REGISTER_URL, json={"email": "weakpass@example.com", "password": "short1"})

    assert resp.status_code == 422


def test_register_missing_fields(client):
    resp = client.post(REGISTER_URL, json={"email": "missing@example.com"})

    assert resp.status_code == 422
