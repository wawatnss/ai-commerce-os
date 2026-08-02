"""Email provider implementations."""
import abc
import logging
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from typing import Dict


logger = logging.getLogger("ai_commerce")


@dataclass
class EmailMessage:
    to: str
    subject: str
    text: str
    html: str | None = None
    from_address: str | None = None


class BaseEmailProvider(abc.ABC):
    @abc.abstractmethod
    def send(self, message: EmailMessage) -> bool:
        ...


class ConsoleProvider(BaseEmailProvider):
    """Logs emails to the console for dev/testing."""

    def send(self, message: EmailMessage) -> bool:
        logger.info("[EMAIL] to=%s subject=%s\n%s", message.to, message.subject, message.text)
        return True


class SMTPProvider(BaseEmailProvider):
    """Sends emails via a standard SMTP server."""

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        use_tls: bool = True,
        from_address: str = "noreply@ai-commerce.com",
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.from_address = from_address

    def send(self, message: EmailMessage) -> bool:
        try:
            from_addr = message.from_address or self.from_address
            msg = MIMEMultipart("alternative")
            msg["Subject"] = message.subject
            msg["From"] = from_addr
            msg["To"] = message.to

            msg.attach(MIMEText(message.text, "plain"))
            if message.html:
                msg.attach(MIMEText(message.html, "html"))

            with smtplib.SMTP(self.host, self.port) as server:
                if self.use_tls:
                    server.starttls()
                if self.username and self.password:
                    server.login(self.username, self.password)
                server.sendmail(from_addr, [message.to], msg.as_string())
            return True
        except Exception:
            logger.exception("SMTP send failed")
            return False


class SendgridProvider(BaseEmailProvider):
    """Placeholder for SendGrid integration."""

    def __init__(self, api_key: str, from_address: str = "noreply@ai-commerce.com"):
        self.api_key = api_key
        self.from_address = from_address

    def send(self, message: EmailMessage) -> bool:
        try:
            import httpx
            url = "https://api.sendgrid.com/v3/mail/send"
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            payload = {
                "personalizations": [{"to": [{"email": message.to}]}],
                "from": {"email": message.from_address or self.from_address},
                "subject": message.subject,
                "content": [
                    {"type": "text/plain", "value": message.text},
                    {"type": "text/html", "value": message.html or message.text},
                ],
            }
            resp = httpx.post(url, headers=headers, json=payload)
            return resp.status_code == 202
        except Exception:
            logger.exception("SendGrid send failed")
            return False


class MailgunProvider(BaseEmailProvider):
    """Placeholder for Mailgun integration."""

    def __init__(self, api_key: str, domain: str, from_address: str = "noreply@ai-commerce.com"):
        self.api_key = api_key
        self.domain = domain
        self.from_address = from_address

    def send(self, message: EmailMessage) -> bool:
        try:
            import httpx
            url = f"https://api.mailgun.net/v3/{self.domain}/messages"
            auth = ("api", self.api_key)
            data = {
                "from": message.from_address or self.from_address,
                "to": message.to,
                "subject": message.subject,
                "text": message.text,
                "html": message.html or message.text,
            }
            resp = httpx.post(url, auth=auth, data=data)
            return resp.status_code == 200
        except Exception:
            logger.exception("Mailgun send failed")
            return False


PROVIDERS: Dict[str, BaseEmailProvider] = {
    "console": ConsoleProvider(),
}


def get_provider(provider: str, config: dict) -> BaseEmailProvider:
    if provider == "smtp":
        return SMTPProvider(
            host=config["host"],
            port=int(config["port"]),
            username=config["username"],
            password=config["password"],
            use_tls=config.get("use_tls", True),
            from_address=config.get("from_address", "noreply@ai-commerce.com"),
        )
    if provider == "sendgrid":
        return SendgridProvider(api_key=config["api_key"], from_address=config.get("from_address", "noreply@ai-commerce.com"))
    if provider == "mailgun":
        return MailgunProvider(
            api_key=config["api_key"],
            domain=config["domain"],
            from_address=config.get("from_address", "noreply@ai-commerce.com"),
        )
    return ConsoleProvider()
