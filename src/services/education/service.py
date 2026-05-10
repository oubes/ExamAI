# ---- Imports ---- #
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.education.services.subject import SubjectService


# ---- Logging ---- #
logger = logging.getLogger(__name__)


# ---- Services ---- #
subject_service = SubjectService()


# ---- Education Service ---- #
class EducationService:

    # ---- Add Subject ---- #
    async def add_subject(
        self,
        session: AsyncSession,
        payload: dict,
    ):

        try:
            record = await subject_service.create_subject(
                session=session,
                data=payload,
            )

            return self._format_subject(record)

        except Exception as e:
            logger.error(
                f"[EducationService] add_subject error: {e}",
                exc_info=True,
            )

            raise


    # ---- Get Subject ---- #
    async def get_subject(
        self,
        session: AsyncSession,
        subject_id,
    ):

        try:
            record = await subject_service.get_by_id(
                session=session,
                subject_id=subject_id,
            )

            if not record:
                raise ValueError("subject not found")

            return self._format_subject(record)

        except Exception as e:
            logger.error(
                f"[EducationService] get_subject error: {e}",
                exc_info=True,
            )

            raise


    # ---- List Subjects ---- #
    async def list_subjects(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ):

        try:
            records = await subject_service.list_subjects(
                session=session,
                limit=limit,
                offset=offset,
            )

            return [
                self._format_subject(record)
                for record in records
            ]

        except Exception as e:
            logger.error(
                f"[EducationService] list_subjects error: {e}",
                exc_info=True,
            )

            raise


    # ---- Update Subject ---- #
    async def update_subject(
        self,
        session: AsyncSession,
        subject_id,
        updates: dict,
    ):

        try:
            record = await subject_service.update(
                session=session,
                subject_id=subject_id,
                updates=updates,
            )

            return self._format_subject(record)

        except Exception as e:
            logger.error(
                f"[EducationService] update_subject error: {e}",
                exc_info=True,
            )

            raise


    # ---- Delete Subject ---- #
    async def delete_subject(
        self,
        session: AsyncSession,
        subject_id,
    ) -> bool:

        try:
            deleted = await subject_service.delete(
                session=session,
                subject_id=subject_id,
            )

            if not deleted:
                raise ValueError("subject not found")

            return deleted

        except Exception as e:
            logger.error(
                f"[EducationService] delete_subject error: {e}",
                exc_info=True,
            )

            raise
        
    # ---- Hard Delete Subject ---- #
    async def hard_delete_subject(
        self,
        session: AsyncSession,
        subject_id,
    ) -> bool:

        try:
            deleted = await subject_service.hard_delete(
                session=session,
                subject_id=subject_id,
            )

            if not deleted:
                raise ValueError("subject not found")

            return deleted

        except Exception as e:
            logger.error(
                f"[EducationService] hard_delete_subject error: {e}",
                exc_info=True,
            )

            raise


    # ---- Formatter ---- #
    def _format_subject(
        self,
        record,
    ):

        return {
            "id": record.id,
            "title": record.title,
            "code": record.code,
            "description": record.description,
            "is_active": record.is_active,
            "created_at": record.created_at,
            "updated_at": record.updated_at,
        }