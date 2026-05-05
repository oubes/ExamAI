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

        msg = EmailMessage()

        msg["From"] = settings.SMTP_FROM
        msg["To"] = to
        msg["Subject"] = subject

        # ---- Plain Text Body ---- #
        msg.set_content(body)

        # ---- HTML Body (optional) ---- #
        if html:
            msg.add_alternative(html, subtype="html")

        # ---- Send Email ---- #
        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            start_tls=True,
        )