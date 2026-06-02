from __future__ import annotations

import asyncio
import smtplib
from abc import ABC, abstractmethod
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import TYPE_CHECKING

from app.core.logging import get_logger

if TYPE_CHECKING:
    from app.core.config import Settings

log = get_logger(__name__)


def build_verification_email(*, recipient: str, verification_link: str, app_name: str, from_name: str) -> tuple[str, str, str]:
    subject = f"Verify your {app_name} email address"
    text_body = (
        f"Hello,\n\n"
        f"Please verify your email address by opening the link below:\n\n"
        f"{verification_link}\n\n"
        f"If you did not create an account, you can ignore this email.\n\n"
        f"— {from_name}\n"
    )
    html_body = f"""\
<!DOCTYPE html>
<html>
<body style="font-family: sans-serif; line-height: 1.5; color: #111;">
  <p>Hello,</p>
  <p>Please verify your email address by clicking the button below:</p>
  <p>
    <a href="{verification_link}"
       style="display: inline-block; padding: 10px 18px; background: #2563eb; color: #fff;
              text-decoration: none; border-radius: 6px;">
      Verify email
    </a>
  </p>
  <p>Or copy and paste this link into your browser:</p>
  <p><a href="{verification_link}">{verification_link}</a></p>
  <p>If you did not create an account, you can ignore this email.</p>
  <p>— {from_name}</p>
</body>
</html>
"""
    return subject, text_body, html_body


class EmailSender(ABC):
    @abstractmethod
    async def send_verification_email(self, *, to: str, verification_link: str) -> None: ...


class SmtpEmailSender(EmailSender):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @property
    def is_configured(self) -> bool:
        return bool(
            self._settings.smtp_host
            and self._settings.smtp_port
            and self._settings.mail_from
        )

    async def send_verification_email(self, *, to: str, verification_link: str) -> None:
        if not self.is_configured:
            raise RuntimeError("SMTP is not configured")

        subject, text_body, html_body = build_verification_email(
            recipient=to,
            verification_link=verification_link,
            app_name=self._settings.app_name,
            from_name=self._settings.mail_from_name,
        )

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{self._settings.mail_from_name} <{self._settings.mail_from}>"
        message["To"] = to
        message.attach(MIMEText(text_body, "plain", "utf-8"))
        message.attach(MIMEText(html_body, "html", "utf-8"))

        log.info(
            "smtp_send_start",
            extra={
                "to": to,
                "smtp_host": self._settings.smtp_host,
                "smtp_port": self._settings.smtp_port,
                "mail_from": self._settings.mail_from,
            },
        )

        try:
            await asyncio.to_thread(self._send_sync, message, to)
        except smtplib.SMTPException as exc:
            log.error(
                "smtp_send_failed",
                extra={
                    "to": to,
                    "smtp_host": self._settings.smtp_host,
                    "smtp_port": self._settings.smtp_port,
                    "error": repr(exc),
                },
            )
            raise
        except OSError as exc:
            log.error(
                "smtp_connection_failed",
                extra={
                    "to": to,
                    "smtp_host": self._settings.smtp_host,
                    "smtp_port": self._settings.smtp_port,
                    "error": repr(exc),
                },
            )
            raise

        log.info("smtp_send_success", extra={"to": to})

    def _send_sync(self, message: MIMEMultipart, to: str) -> None:
        host = self._settings.smtp_host
        port = self._settings.smtp_port
        assert host is not None and port is not None

        with smtplib.SMTP(host, port, timeout=30) as smtp:
            smtp.ehlo()
            if self._settings.smtp_use_tls:
                smtp.starttls()
                smtp.ehlo()
            username = self._settings.smtp_username
            password = self._settings.smtp_password
            if username and password:
                smtp.login(username, password)
            smtp.sendmail(self._settings.mail_from, [to], message.as_string())


class LoggingEmailSender(EmailSender):
    """Fallback when SMTP is not configured — logs the link instead of sending."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def send_verification_email(self, *, to: str, verification_link: str) -> None:
        log.warning(
            "verification_email_not_sent_smtp_unconfigured",
            extra={
                "to": to,
                "verification_link": verification_link,
                "hint": "Configure APP_SMTP_HOST, APP_SMTP_PORT, and APP_MAIL_FROM to send emails.",
            },
        )


def create_email_sender(settings: Settings) -> EmailSender:
    sender = SmtpEmailSender(settings)
    if sender.is_configured:
        return sender
    return LoggingEmailSender(settings)
