"""Tests for GET /api/v1/auth/me."""

ME_URL = "/api/v1/auth/me"


def _login_and_get_token(client, email: str, password: str) -> str:
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def test_me_authenticated(client, register_user):
    email, password = register_user("me.authenticated@example.com")
    token = _login_and_get_token(client, email, password)

    resp = client.get(ME_URL, headers={"Authorization": f"Bearer {token}"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == email
    assert body["is_active"] is True
    assert body["email_verified"] is False


def test_me_missing_token(client):
    resp = client.get(ME_URL)

    assert resp.status_code == 401


def test_me_invalid_token(client):
    resp = client.get(ME_URL, headers={"Authorization": "Bearer this.is.not.a.valid.jwt"})

    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid token"


def test_me_malformed_authorization_header(client):
    """No 'Bearer ' scheme prefix at all."""
    resp = client.get(ME_URL, headers={"Authorization": "not-a-bearer-token"})

    assert resp.status_code == 401
