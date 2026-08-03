"""Tests for POST /api/v1/auth/login (JSON body)."""

LOGIN_URL = "/api/v1/auth/login"


def test_login_success(client, register_user):
    email, password = register_user("login.success@example.com")

    resp = client.post(LOGIN_URL, json={"email": email, "password": password})

    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str) and body["access_token"]


def test_login_wrong_password(client, register_user):
    email, _ = register_user("login.wrongpass@example.com")

    resp = client.post(LOGIN_URL, json={"email": email, "password": "TotallyWrongPassword!"})

    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid credentials"


def test_login_unknown_email(client):
    resp = client.post(LOGIN_URL, json={"email": "nobody@example.com", "password": "SuperSecret123!"})

    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid credentials"


def test_login_case_insensitive_email(client, register_user):
    email, password = register_user("Login.Case@Example.com")

    resp = client.post(LOGIN_URL, json={"email": "login.case@example.com", "password": password})

    assert resp.status_code == 200
