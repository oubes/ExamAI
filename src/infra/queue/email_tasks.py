# ---- Imports ---- #
import asyncio

from src.infra.queue.celery_app import celery_app
from src.infra.email.service import EmailService


email_service = EmailService()


# ---- Helper runner ---- #
def run_async(coro):
    return asyncio.run(coro)


# ---- Welcome Email Task ---- #
@celery_app.task
def send_welcome_email(to: str, context: dict):

    return run_async(
        email_service.send_from_template(
            to=to,
            template_name="welcome.yml",
            context=context,
        )
    )


# ---- Verify Email Task ---- #
@celery_app.task
def send_verify_email(to: str, context: dict):

    return run_async(
        email_service.send_from_template(
            to=to,
            template_name="verify_email.yml",
            context=context,
        )
    )
    
# ---- Reset Password Email Task ---- #
@celery_app.task
def send_reset_password_email(to: str, context: dict):

    return run_async(
        email_service.send_from_template(
            to=to,
            template_name="reset_password.yml",
            context=context,
        )
    )