# ---- Imports ---- #
from asgiref.sync import async_to_sync
import celery
import asyncio
from src.infra.queue.celery_app import celery_app
from src.infra.email.service import EmailService
from src.services.question.pipeline.segmentation_pipeline import run_pipeline as run_segmentation_pipeline
from src.core.di.db import session_local

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
    
# --------------- Segmentation tasks --------------- #
@celery_app.task
def segment_file(subject_id: str, book_id: str):
    async def run():
        async with session_local() as session:
            return await run_segmentation_pipeline(
                session=session,
                subject_id=subject_id,
                book_id=book_id,
            )

    return asyncio.run(run())

# --------------- Question Pipeline Task --------------- #
@celery_app.task
def run_question_pipeline(subject_id: str, book_id: str):

    async def run():
        async with session_local() as session:
            return await run_segmentation_pipeline(
                session=session,
                subject_id=subject_id,
                book_id=book_id,
            )

    return asyncio.run(run())