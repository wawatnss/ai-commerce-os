"""Tests for POST /api/v1/auth/password-reset-confirm."""
from datetime import datetime, timedelta, timezone

from jose import jwt

from app.auth.models import User
from app.auth.service import generate_password_reset_token
from config import settings

RESET_CONFIRM_URL = "/api/v1/auth/password-reset-confirm"
LOGIN_URL = "/api/v1/auth/login"


def _get_user(db_session, email: str) -> User:
    return db_session.query(User).filter(User.email == email).one()


def test_password_reset_confirm_valid_token(client, register_user, db_session):
    email, old_password = register_user("reset.confirm.valid@example.com")
    user = _get_user(db_session, email)
    token = generate_password_reset_token(user)
    new_password = "BrandNewPassword456!"

    resp = client.post(RESET_CONFIRM_URL, json={"token": token, "new_password": new_password})

    assert resp.status_code == 200
    assert resp.json() == {"message": "Password updated"}

    # New password works, old one no longer does.
    assert client.post(LOGIN_URL, json={"email": email, "password": new_password}).status_code == 200
    assert client.post(LOGIN_URL, json={"email": email, "password": old_password}).status_code == 401


def test_password_reset_confirm_expired_token(client, register_user, db_session):
    email, old_password = register_user("reset.confirm.expired@example.com")
    user = _get_user(db_session, email)

    expired_token = jwt.encode(
        {
            "sub": user.email,
            "type": "reset",
            "jti": "expired-jti",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    resp = client.post(RESET_CONFIRM_URL, json={"token": expired_token, "new_password": "NewPassword789!"})

    assert resp.status_code == 400
    assert resp.json()["detail"] == "Invalid or expired token"
    # Old password must still work - the reset must not have been applied.
    assert client.post(LOGIN_URL, json={"email": email, "password": old_password}).status_code == 200


def test_password_reset_confirm_invalid_token(client):
    resp = client.post(RESET_CONFIRM_URL, json={"token": "not-a-jwt-at-all", "new_password": "NewPassword789!"})

    assert resp.status_code == 400
    assert resp.json()["detail"] == "Invalid or expired token"


def test_password_reset_confirm_wrong_token_type(client, register_user, db_session):
    """A verify-email token must not be usable to reset a password."""
    from app.auth.service import generate_verification_token

    email, old_password = register_user("reset.confirm.wrongtype@example.com")
    user = _get_user(db_session, email)
    verify_token = generate_verification_token(user)

    resp = client.post(RESET_CONFIRM_URL, json={"token": verify_token, "new_password": "NewPassword789!"})

    assert resp.status_code == 400


def test_password_reset_confirm_weak_new_password(client, register_user, db_session):
    email, _ = register_user("reset.confirm.weak@example.com")
    user = _get_user(db_session, email)
    token = generate_password_reset_token(user)

    resp = client.post(RESET_CONFIRM_URL, json={"token": token, "new_password": "short"})

    assert resp.status_code == 422
