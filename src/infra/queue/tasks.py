# ---- Imports ---- #
from asgiref.sync import async_to_sync

from src.infra.queue.celery_app import celery_app
from src.infra.email.service import EmailService


# ---- Services ---- #
email_service = EmailService()


# --------------- Mail Tasks --------------- #
# ---- Welcome Email Task ---- #
@celery_app.task
def send_welcome_email(to: str, context: dict):

    return async_to_sync(email_service.send_from_template)(
        to=to,
        template_name="welcome.yml",
        context=context,
    )


# ---- Verify Email Task ---- #
@celery_app.task
def send_verify_email(to: str, context: dict):

    return async_to_sync(email_service.send_from_template)(
        to=to,
        template_name="verify_email.yml",
        context=context,
    )


# ---- Reset Password Email Task ---- #
@celery_app.task
def send_reset_password_email(to: str, context: dict):

    return async_to_sync(email_service.send_from_template)(
        to=to,
        template_name="reset_password.yml",
        context=context,
    )
    
@celery_app.task
def send_password_changed_email(to: str, context: dict):

    return async_to_sync(email_service.send_from_template)(
        to=to,
        template_name="password_changed.yml",
        context=context,
    )