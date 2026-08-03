"""Tests for POST /api/v1/auth/send-verification."""

SEND_VERIFICATION_URL = "/api/v1/auth/send-verification"


def _login_and_get_token(client, email: str, password: str) -> str:
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def test_send_verification_authenticated_user(client, register_user, mock_email_service):
    email, password = register_user("send.verification.auth@example.com")
    token = _login_and_get_token(client, email, password)
    # Registration itself already triggers one send_verification call; reset
    # the mock so this test only reflects the /send-verification call.
    mock_email_service.reset_mock()

    resp = client.post(SEND_VERIFICATION_URL, headers={"Authorization": f"Bearer {token}"})

    assert resp.status_code == 200
    assert resp.json() == {"message": "Verification email sent if configured"}
    mock_email_service.return_value.send_verification.assert_called_once()
    called_email = mock_email_service.return_value.send_verification.call_args.args[0]
    assert called_email == email


def test_send_verification_unauthenticated_user(client, mock_email_service):
    mock_email_service.reset_mock()

    resp = client.post(SEND_VERIFICATION_URL)

    assert resp.status_code == 401
    mock_email_service.return_value.send_verification.assert_not_called()


def test_send_verification_invalid_token(client, mock_email_service):
    mock_email_service.reset_mock()

    resp = client.post(SEND_VERIFICATION_URL, headers={"Authorization": "Bearer garbage"})

    assert resp.status_code == 401
    mock_email_service.return_value.send_verification.assert_not_called()
