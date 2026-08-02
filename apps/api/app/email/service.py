"""Email service."""
import logging

from app.email.providers import EmailMessage, get_provider
from app.email.templates import welcome_email, verification_email, password_reset_email
from config import settings

logger = logging.getLogger("ai_commerce")


class EmailService:
    """High-level email facade with provider abstraction."""

    def __init__(self):
        self.provider_name = getattr(settings, "EMAIL_PROVIDER", "console").lower()
        self.config = {
            "host": getattr(settings, "SMTP_HOST", "localhost"),
            "port": getattr(settings, "SMTP_PORT", 587),
            "username": getattr(settings, "SMTP_USERNAME", ""),
            "password": getattr(settings, "SMTP_PASSWORD", ""),
            "use_tls": getattr(settings, "SMTP_USE_TLS", True),
            "from_address": getattr(settings, "EMAIL_FROM", "noreply@ai-commerce.com"),
            "api_key": getattr(settings, "EMAIL_API_KEY", ""),
            "domain": getattr(settings, "EMAIL_DOMAIN", ""),
        }
        self.provider = get_provider(self.provider_name, self.config)

    def _send(self, to: str, template) -> bool:
        message = EmailMessage(
            to=to,
            from_address=self.config.get("from_address"),
            subject=template.subject,
            text=template.text,
            html=template.html,
        )
        ok = self.provider.send(message)
        if not ok:
            logger.warning("Failed to send email to %s", to)
        return ok

    def send_welcome(self, email: str) -> bool:
        return self._send(email, welcome_email(email))

    def send_verification(self, email: str, token: str) -> bool:
        base_url = getattr(settings, "PUBLIC_ADMIN_URL", "https://admin.ai-commerce.com")
        return self._send(email, verification_email(email, token, base_url))

    def send_password_reset(self, email: str, token: str) -> bool:
        base_url = getattr(settings, "PUBLIC_ADMIN_URL", "https://admin.ai-commerce.com")
        return self._send(email, password_reset_email(email, token, base_url))
