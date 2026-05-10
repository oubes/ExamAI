# ---- Imports ---- #
import logging
from uuid import UUID

from sqlalchemy import func, select, update, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.education.models.subject import Subject
from src.domain.education.models.chapter import Chapter
from src.domain.education.models.enrollment import Enrollment
from src.domain.education.models.exam import Exam


# ---- Logging ---- #
logger = logging.getLogger(__name__)


# ---- Subject Service ---- #
class SubjectService:

    # ---- Create ---- #
    async def create(
        self,
        session: AsyncSession,
        data: dict,
    ) -> Subject:

        try:
            code = str(data["code"]).strip().upper()

            exists_stmt = select(Subject).where(
                func.lower(Subject.code) == code.lower()
            )

            exists_result = await session.execute(exists_stmt)

            if exists_result.scalar_one_or_none():
                raise ValueError("subject code already exists")

            record = Subject(
                title=str(data["title"]).strip(),
                code=code,
            )

            session.add(record)

            await session.commit()
            await session.refresh(record)

            return record

        except IntegrityError as e:
            await session.rollback()

            logger.error(
                f"[SubjectService] create integrity error: {e}",
                exc_info=True,
            )

            raise

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[SubjectService] create error: {e}",
                exc_info=True,
            )

            raise


    # ---- Bulk Create ---- #
    async def bulk_create(
        self,
        session: AsyncSession,
        payloads: list[dict],
    ) -> list[Subject]:

        try:
            normalized_codes = [
                str(item["code"]).strip().upper()
                for item in payloads
            ]

            if len(normalized_codes) != len(set(normalized_codes)):
                raise ValueError("duplicate subject codes in payload")

            stmt = select(Subject.code)

            result = await session.execute(stmt)

            existing_codes = {
                row.lower()
                for row in result.scalars().all()
            }

            duplicated = [
                code
                for code in normalized_codes
                if code.lower() in existing_codes
            ]

            if duplicated:
                raise ValueError(
                    f"subject codes already exist: {duplicated}"
                )

            records = [
                Subject(
                    title=str(item["title"]).strip(),
                    code=str(item["code"]).strip().upper(),
                )
                for item in payloads
            ]

            session.add_all(records)

            await session.commit()

            for record in records:
                await session.refresh(record)

            return records

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[SubjectService] bulk_create error: {e}",
                exc_info=True,
            )

            raise


    # ---- Exists ---- #
    async def exists(
        self,
        session: AsyncSession,
        subject_id: UUID,
    ) -> bool:

        try:
            stmt = select(Subject.id).where(
                Subject.id == subject_id
            )

            result = await session.execute(stmt)

            return result.scalar_one_or_none() is not None

        except Exception as e:
            logger.error(
                f"[SubjectService] exists error: {e}",
                exc_info=True,
            )

            raise


    # ---- Get By ID ---- #
    async def get_by_id(
        self,
        session: AsyncSession,
        subject_id: UUID,
    ) -> Subject | None:

        try:
            stmt = (
                select(Subject)
                .where(Subject.id == subject_id)
            )

            result = await session.execute(stmt)

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(
                f"[SubjectService] get_by_id error: {e}",
                exc_info=True,
            )

            raise


    # ---- Get Full ---- #
    async def get_full(
        self,
        session: AsyncSession,
        subject_id: UUID,
    ) -> Subject | None:

        try:
            stmt = (
                select(Subject)
                .options(
                    selectinload(Subject.chapters),
                    selectinload(Subject.enrollments),
                    selectinload(Subject.exams),
                )
                .where(Subject.id == subject_id)
            )

            result = await session.execute(stmt)

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(
                f"[SubjectService] get_full error: {e}",
                exc_info=True,
            )

            raise


    # ---- Get By Code ---- #
    async def get_by_code(
        self,
        session: AsyncSession,
        code: str,
    ) -> Subject | None:

        try:
            stmt = select(Subject).where(
                func.lower(Subject.code) == code.strip().lower()
            )

            result = await session.execute(stmt)

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(
                f"[SubjectService] get_by_code error: {e}",
                exc_info=True,
            )

            raise


    # ---- Get Many By IDs ---- #
    async def get_many_by_ids(
        self,
        session: AsyncSession,
        subject_ids: list[UUID],
    ) -> list[Subject]:

        try:
            if not subject_ids:
                return []

            stmt = select(Subject).where(
                Subject.id.in_(subject_ids)
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(
                f"[SubjectService] get_many_by_ids error: {e}",
                exc_info=True,
            )

            raise


    # ---- List ---- #
    async def list_subjects(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Subject]:

        try:
            stmt = (
                select(Subject)
                .order_by(Subject.title.asc())
                .offset(offset)
                .limit(limit)
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(
                f"[SubjectService] list_subjects error: {e}",
                exc_info=True,
            )

            raise


    # ---- Search ---- #
    async def search(
        self,
        session: AsyncSession,
        query: str,
        limit: int = 20,
    ) -> list[Subject]:

        try:
            normalized_query = query.strip()

            stmt = (
                select(Subject)
                .where(
                    Subject.title.ilike(f"%{normalized_query}%")
                    | Subject.code.ilike(f"%{normalized_query}%")
                )
                .order_by(Subject.title.asc())
                .limit(limit)
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(
                f"[SubjectService] search error: {e}",
                exc_info=True,
            )

            raise


    # ---- Count ---- #
    async def count(
        self,
        session: AsyncSession,
    ) -> int:

        try:
            stmt = select(func.count(Subject.id))

            result = await session.execute(stmt)

            return int(result.scalar() or 0)

        except Exception as e:
            logger.error(
                f"[SubjectService] count error: {e}",
                exc_info=True,
            )

            raise


    # ---- Update ---- #
    async def update(
        self,
        session: AsyncSession,
        subject_id: UUID,
        updates: dict,
    ) -> Subject:

        try:
            record = await self.get_by_id(
                session=session,
                subject_id=subject_id,
            )

            if not record:
                raise ValueError("subject not found")

            protected_fields = {"id"}

            if "code" in updates:
                normalized_code = str(
                    updates["code"]
                ).strip().upper()

                stmt = select(Subject).where(
                    func.lower(Subject.code) == normalized_code.lower(),
                    Subject.id != subject_id,
                )

                result = await session.execute(stmt)

                if result.scalar_one_or_none():
                    raise ValueError("subject code already exists")

                updates["code"] = normalized_code

            for key, value in updates.items():
                if key in protected_fields:
                    continue

                setattr(record, key, value)

            await session.commit()
            await session.refresh(record)

            return record

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[SubjectService] update error: {e}",
                exc_info=True,
            )

            raise


    # ---- Patch Title ---- #
    async def patch_title(
        self,
        session: AsyncSession,
        subject_id: UUID,
        title: str,
    ) -> bool:

        try:
            stmt = (
                update(Subject)
                .where(Subject.id == subject_id)
                .values(
                    title=title.strip(),
                )
            )

            result = await session.execute(stmt)

            await session.commit()

            return getattr(result, "rowcount", 0) > 0

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[SubjectService] patch_title error: {e}",
                exc_info=True,
            )

            raise


    # ---- Delete ---- #
    async def delete(
        self,
        session: AsyncSession,
        subject_id: UUID,
    ) -> bool:

        try:
            subject = await self.get_full(
                session=session,
                subject_id=subject_id,
            )

            if not subject:
                return False

            if subject.chapters:
                raise ValueError(
                    "cannot delete subject with chapters"
                )

            if subject.exams:
                raise ValueError(
                    "cannot delete subject with exams"
                )

            if subject.enrollments:
                raise ValueError(
                    "cannot delete subject with enrollments"
                )

            await session.delete(subject)

            await session.commit()

            return True

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[SubjectService] delete error: {e}",
                exc_info=True,
            )

            raise


    # ---- Hard Delete ---- #
    async def hard_delete(
        self,
        session: AsyncSession,
        subject_id: UUID,
    ) -> bool:

        try:
            stmt = delete(Subject).where(
                Subject.id == subject_id
            )

            result = await session.execute(stmt)

            await session.commit()

            return bool(getattr(result, "rowcount", 0))

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[SubjectService] hard_delete error: {e}",
                exc_info=True,
            )

            raise


    # ---- Stats ---- #
    async def stats(
        self,
        session: AsyncSession,
        subject_id: UUID,
    ) -> dict:

        try:
            chapter_stmt = select(
                func.count(Chapter.id)
            ).where(
                Chapter.subject_id == subject_id
            )

            enrollment_stmt = select(
                func.count(Enrollment.id) # type: ignore
            ).where(
                Enrollment.subject_id == subject_id
            )

            exam_stmt = select(
                func.count(Exam.id)
            ).where(
                Exam.subject_id == subject_id
            )

            chapters_result = await session.execute(chapter_stmt)
            enrollments_result = await session.execute(enrollment_stmt)
            exams_result = await session.execute(exam_stmt)

            return {
                "chapters": int(chapters_result.scalar() or 0),
                "enrollments": int(enrollments_result.scalar() or 0),
                "exams": int(exams_result.scalar() or 0),
            }

        except Exception as e:
            logger.error(
                f"[SubjectService] stats error: {e}",
                exc_info=True,
            )

            raise