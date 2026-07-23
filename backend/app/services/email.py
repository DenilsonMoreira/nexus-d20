import asyncio
import smtplib
from email.message import EmailMessage

from app.core.config import settings


def _send_email_sync(message: EmailMessage) -> None:
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
        if settings.smtp_starttls:
            smtp.starttls()
        if settings.smtp_username:
            smtp.login(settings.smtp_username, settings.smtp_password)
        smtp.send_message(message)


async def send_password_reset_email(recipient: str, token: str) -> None:
    reset_url = f"{settings.app_url.rstrip('/')}/recuperar-acesso?token={token}"
    message = EmailMessage()
    message["Subject"] = "Recuperação de acesso — Nexus d20"
    message["From"] = settings.mail_from
    message["To"] = recipient
    message.set_content(
        "Recebemos uma solicitação para redefinir sua senha do Nexus d20.\n\n"
        f"Use este link em até {settings.password_reset_ttl_minutes} minutos:\n"
        f"{reset_url}\n\n"
        "Se você não fez esta solicitação, ignore esta mensagem."
    )
    await asyncio.to_thread(_send_email_sync, message)


async def deliver_password_reset_safely(recipient: str, token: str) -> None:
    try:
        await send_password_reset_email(recipient, token)
    except (OSError, TimeoutError, ValueError, smtplib.SMTPException):
        return
