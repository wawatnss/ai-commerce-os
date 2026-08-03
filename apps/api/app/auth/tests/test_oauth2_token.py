"""Tests for POST /api/v1/auth/token (OAuth2 password flow, form-encoded).

This is the endpoint `OAuth2PasswordBearer`'s `tokenUrl` points at, and the
one Swagger UI's "Authorize" dialog submits to.
"""

TOKEN_URL = "/api/v1/auth/token"


def _post_token(client, username: str, password: str):
    # Sent as a form body, exactly like Swagger's Authorize dialog / any
    # OAuth2 client, never JSON.
    return client.post(
        TOKEN_URL,
        data={"username": username, "password": password, "grant_type": "password"},
    )


def test_token_success(client, register_user):
    email, password = register_user("token.success@example.com")

    resp = _post_token(client, email, password)

    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str) and body["access_token"]


def test_token_wrong_password(client, register_user):
    email, _ = register_user("token.wrongpass@example.com")

    resp = _post_token(client, email, "TotallyWrongPassword!")

    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid credentials"


def test_token_invalid_username(client):
    resp = _post_token(client, "no.such.user@example.com", "SuperSecret123!")

    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid credentials"


def test_token_request_body_is_form_encoded_in_openapi(client):
    """Guards against the original bug: Swagger's Authorize button sends
    application/x-www-form-urlencoded, so /token must document exactly that
    (not application/json) or Swagger's request will fail with 422."""
    schema = client.get("/openapi.json").json()

    content_types = schema["paths"]["/api/v1/auth/token"]["post"]["requestBody"]["content"]
    assert list(content_types.keys()) == ["application/x-www-form-urlencoded"]
    assert (
        schema["components"]["securitySchemes"]["OAuth2PasswordBearer"]["flows"]["password"]["tokenUrl"]
        == "/api/v1/auth/token"
    )
