# ---- Imports ---- #
from src.infra.email.smtp_client import SMTPClient
from src.infra.email.renderer import render_template


# ---- Email Service ---- #
class EmailService:

    def __init__(self):
        self.smtp = SMTPClient()

    async def send_from_template(
        self,
        to: str,
        template_name: str,
        context: dict,
    ) -> None:

        rendered = render_template(template_name, context)

        await self.smtp.send(
            to=to,
            subject=rendered["subject"],
            body=rendered["body"],
            html=rendered.get("html"),
        )