import pytest
from unittest.mock import patch, MagicMock
from app.core.alerts import send_alert_email, alert_critical_error, alert_rate_limit_hit


# ============================
# send_alert_email
# ============================

@patch("app.core.alerts.settings")
@patch("app.core.alerts.smtplib")
def test_send_alert_email_success(mock_smtplib, mock_settings):
    mock_settings.ALERT_EMAIL_TO = "admin@test.com"
    mock_settings.SMTP_HOST = "smtp.test.com"
    mock_settings.SMTP_PORT = 587
    mock_settings.SMTP_USER = "user@test.com"
    mock_settings.SMTP_PASSWORD = "pass"
    mock_settings.SMTP_TLS = True

    mock_server = MagicMock()
    mock_smtplib.SMTP.return_value.__enter__ = lambda s: mock_server
    mock_smtplib.SMTP.return_value.__exit__ = MagicMock(return_value=False)

    result = send_alert_email("Test Subject", "Test body")
    assert result is True


@patch("app.core.alerts.settings")
def test_send_alert_email_no_recipient(mock_settings):
    mock_settings.ALERT_EMAIL_TO = ""
    result = send_alert_email("Test Subject", "Test body")
    assert result is False


@patch("app.core.alerts.settings")
@patch("app.core.alerts.smtplib")
def test_send_alert_email_smtp_error(mock_smtplib, mock_settings):
    mock_settings.ALERT_EMAIL_TO = "admin@test.com"
    mock_settings.SMTP_HOST = "smtp.test.com"
    mock_settings.SMTP_PORT = 587
    mock_settings.SMTP_USER = ""
    mock_settings.SMTP_PASSWORD = ""
    mock_settings.SMTP_TLS = False

    mock_smtplib.SMTP.side_effect = Exception("Connection refused")

    result = send_alert_email("Test Subject", "Test body")
    assert result is False


# ============================
# alert_critical_error
# ============================

@patch("app.core.alerts.send_alert_email")
def test_alert_critical_error(mock_send):
    alert_critical_error("InternalServerError", "Something broke", "/api/test")
    mock_send.assert_called_once()
    args = mock_send.call_args
    assert "CRITICAL: InternalServerError" in args[0][0]
    assert "Something broke" in args[0][1]
    assert "/api/test" in args[0][1]


# ============================
# alert_rate_limit_hit
# ============================

@patch("app.core.alerts.send_alert_email")
def test_alert_rate_limit_hit(mock_send):
    alert_rate_limit_hit("127.0.0.1", "/auth/login")
    mock_send.assert_called_once()
    args = mock_send.call_args
    assert "Rate Limit Hit" in args[0][0]
    assert "127.0.0.1" in args[0][1]
    assert "/auth/login" in args[0][1]
