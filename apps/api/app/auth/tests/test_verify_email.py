"""Tests for POST /api/v1/auth/verify-email."""
from datetime import datetime, timedelta, timezone

from jose import jwt

from app.auth.models import User
from app.auth.service import generate_verification_token
from config import settings

VERIFY_URL = "/api/v1/auth/verify-email"


def _get_user(db_session, email: str) -> User:
    return db_session.query(User).filter(User.email == email).one()


def test_verify_email_valid_token(client, register_user, db_session):
    email, _ = register_user("verify.valid@example.com")
    user = _get_user(db_session, email)
    token = generate_verification_token(user)

    resp = client.post(VERIFY_URL, json={"token": token})

    assert resp.status_code == 200
    assert resp.json() == {"message": "Email verified"}

    db_session.expire_all()
    assert _get_user(db_session, email).email_verified is True


def test_verify_email_expired_token(client, register_user, db_session):
    email, _ = register_user("verify.expired@example.com")
    user = _get_user(db_session, email)

    expired_token = jwt.encode(
        {
            "sub": user.email,
            "type": "verify",
            "jti": "expired-jti",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    resp = client.post(VERIFY_URL, json={"token": expired_token})

    assert resp.status_code == 400
    assert resp.json()["detail"] == "Invalid or expired token"

    db_session.expire_all()
    assert _get_user(db_session, email).email_verified is False


def test_verify_email_tampered_token(client, register_user, db_session):
    email, _ = register_user("verify.tampered@example.com")
    user = _get_user(db_session, email)
    token = generate_verification_token(user)

    # Flip the last character of the signature so it no longer verifies.
    tampered = token[:-1] + ("A" if token[-1] != "A" else "B")

    resp = client.post(VERIFY_URL, json={"token": tampered})

    assert resp.status_code == 400
    assert resp.json()["detail"] == "Invalid or expired token"

    db_session.expire_all()
    assert _get_user(db_session, email).email_verified is False


def test_verify_email_garbage_token(client):
    resp = client.post(VERIFY_URL, json={"token": "not-a-jwt-at-all"})

    assert resp.status_code == 400
    assert resp.json()["detail"] == "Invalid or expired token"


def test_verify_email_wrong_token_type(client, register_user, db_session):
    """A password-reset token must not be usable to verify an email."""
    from app.auth.service import generate_password_reset_token

    email, _ = register_user("verify.wrongtype@example.com")
    user = _get_user(db_session, email)
    reset_token = generate_password_reset_token(user)

    resp = client.post(VERIFY_URL, json={"token": reset_token})

    assert resp.status_code == 400


def test_verify_email_already_verified_user_is_idempotent(client, register_user, db_session):
    """Verifying an already-verified user again must not error."""
    email, _ = register_user("verify.already@example.com")
    user = _get_user(db_session, email)

    first_token = generate_verification_token(user)
    resp1 = client.post(VERIFY_URL, json={"token": first_token})
    assert resp1.status_code == 200

    db_session.expire_all()
    user = _get_user(db_session, email)
    assert user.email_verified is True

    second_token = generate_verification_token(user)
    resp2 = client.post(VERIFY_URL, json={"token": second_token})

    assert resp2.status_code == 200
    db_session.expire_all()
    assert _get_user(db_session, email).email_verified is True
