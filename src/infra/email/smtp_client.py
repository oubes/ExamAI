# ---- Imports ---- #
import aiosmtplib
from email.message import EmailMessage

from src.core.di.settings import get_settings


# ---- Settings ---- #
settings = get_settings()


# ---- SMTP Client ---- #
class SMTPClient:

    async def send(
        self,
        to: str,
        subject: str,
        body: str,
        html: str | None = None,
    ) -> None:

        # ---- Build Message ---- #
        msg = EmailMessage()

        msg["From"] = settings.smtp_from
        msg["To"] = to
        msg["Subject"] = subject

        # ---- Plain Text Body ---- #
        msg.set_content(body)

        # ---- HTML Body ---- #
        if html:
            msg.add_alternative(html, subtype="html")

        # ---- Send Email ---- #
        await aiosmtplib.send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user,
            password=settings.smtp_password,
            use_tls=True,
            start_tls=False,
        )
