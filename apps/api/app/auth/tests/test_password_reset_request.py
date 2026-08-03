"""Tests for POST /api/v1/auth/password-reset-request."""

RESET_REQUEST_URL = "/api/v1/auth/password-reset-request"
GENERIC_MESSAGE = {"message": "If the email exists, a reset link has been sent"}


def test_password_reset_request_existing_email(client, register_user, mock_email_service):
    email, _ = register_user("reset.request.existing@example.com")
    mock_email_service.reset_mock()

    resp = client.post(RESET_REQUEST_URL, json={"email": email})

    assert resp.status_code == 200
    assert resp.json() == GENERIC_MESSAGE
    mock_email_service.return_value.send_password_reset.assert_called_once()
    called_email = mock_email_service.return_value.send_password_reset.call_args.args[0]
    assert called_email == email


def test_password_reset_request_unknown_email(client, mock_email_service):
    mock_email_service.reset_mock()

    resp = client.post(RESET_REQUEST_URL, json={"email": "nobody@example.com"})

    # Same generic response as a known email - must never reveal whether an
    # account exists.
    assert resp.status_code == 200
    assert resp.json() == GENERIC_MESSAGE
    mock_email_service.return_value.send_password_reset.assert_not_called()


def test_password_reset_request_invalid_email_format(client):
    resp = client.post(RESET_REQUEST_URL, json={"email": "not-an-email"})

    assert resp.status_code == 422
