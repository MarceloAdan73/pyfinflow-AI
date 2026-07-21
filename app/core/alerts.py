import smtplib
import ssl
from email.message import EmailMessage
from typing import Optional

import structlog

from app.core.config import settings

logger = structlog.get_logger()


def send_alert_email(
    subject: str,
    body: str,
    to_email: Optional[str] = None,
) -> bool:
    if not settings.ALERT_EMAIL_TO:
        logger.debug("alert_email_not_configured", subject=subject)
        return False

    try:
        msg = EmailMessage()
        msg["Subject"] = f"[PyStreamFlow] {subject}"
        msg["From"] = settings.SMTP_USER or "alerts@pystreamflow.app"
        msg["To"] = to_email or settings.ALERT_EMAIL_TO
        msg.set_content(body)

        context = ssl.create_default_context()
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_TLS:
                server.starttls(context=context)
            if settings.SMTP_USER:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)

        logger.info("alert_email_sent", subject=subject, to=msg["To"])
        return True
    except Exception as e:
        logger.error("alert_email_failed", subject=subject, error=str(e))
        return False


def alert_critical_error(error_type: str, error_message: str, path: str = ""):
    subject = f"CRITICAL: {error_type}"
    body = (
        f"Error Type: {error_type}\n"
        f"Message: {error_message}\n"
        f"Path: {path}\n"
    )
    send_alert_email(subject, body)


def alert_rate_limit_hit(ip: str, path: str):
    subject = "Rate Limit Hit"
    body = f"IP: {ip}\nPath: {path}\n"
    send_alert_email(subject, body)
