# ---- Imports ---- #
import logging
from uuid import UUID
from datetime import datetime

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
    async def create_subject(
        self,
        session: AsyncSession,
        data: dict,
    ) -> Subject:

        try:
            code = str(data["code"]).strip().upper()
            title = str(data["title"]).strip()

            stmt = select(Subject).where(
                func.lower(Subject.code) == code.lower()
            )

            result = await session.execute(stmt)

            if result.scalar_one_or_none():
                raise ValueError("subject code already exists")

            record = Subject(
                title=title,
                code=code,
                description=data.get("description"),
                is_active=True,
                is_deleted=False,
            )

            session.add(record)
            await session.commit()
            await session.refresh(record)

            return record

        except IntegrityError as e:
            await session.rollback()
            logger.error(f"[SubjectService] create integrity error: {e}", exc_info=True)
            raise

        except Exception as e:
            await session.rollback()
            logger.error(f"[SubjectService] create error: {e}", exc_info=True)
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
                c.lower()
                for c in result.scalars().all()
            }

            duplicated = [
                c for c in normalized_codes
                if c.lower() in existing_codes
            ]

            if duplicated:
                raise ValueError(f"subject codes already exist: {duplicated}")

            records = [
                Subject(
                    title=str(item["title"]).strip(),
                    code=str(item["code"]).strip().upper(),
                    description=item.get("description"),
                    is_active=True,
                    is_deleted=False,
                )
                for item in payloads
            ]

            session.add_all(records)
            await session.commit()

            for r in records:
                await session.refresh(r)

            return records

        except Exception as e:
            await session.rollback()
            logger.error(f"[SubjectService] bulk_create error: {e}", exc_info=True)
            raise


    # ---- Exists ---- #
    async def exists(
        self,
        session: AsyncSession,
        subject_id: UUID,
    ) -> bool:

        try:
            stmt = select(Subject.id).where(
                Subject.id == subject_id,
                Subject.is_deleted == False,  # noqa
            )

            result = await session.execute(stmt)
            return result.scalar_one_or_none() is not None

        except Exception as e:
            logger.error(f"[SubjectService] exists error: {e}", exc_info=True)
            raise


    # ---- Get By ID ---- #
    async def get_by_id(
        self,
        session: AsyncSession,
        subject_id: UUID,
        include_deleted: bool = False,
    ) -> Subject | None:

        try:
            stmt = select(Subject).where(Subject.id == subject_id)

            if not include_deleted:
                stmt = stmt.where(Subject.is_deleted == False)  # noqa

            result = await session.execute(stmt)
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"[SubjectService] get_by_id error: {e}", exc_info=True)
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
                .where(
                    Subject.id == subject_id,
                    Subject.is_deleted == False,  # noqa
                )
            )

            result = await session.execute(stmt)
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"[SubjectService] get_full error: {e}", exc_info=True)
            raise


    # ---- Get By Code ---- #
    async def get_by_code(
        self,
        session: AsyncSession,
        code: str,
    ) -> Subject | None:

        try:
            stmt = select(Subject).where(
                func.lower(Subject.code) == code.strip().lower(),
                Subject.is_deleted == False,  # noqa
            )

            result = await session.execute(stmt)
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"[SubjectService] get_by_code error: {e}", exc_info=True)
            raise


    # ---- List ---- #
    async def list_subjects(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
        include_inactive: bool = True,
    ) -> list[Subject]:

        try:
            stmt = select(Subject)

            if not include_inactive:
                stmt = stmt.where(
                    Subject.is_deleted == False,  # noqa
                    Subject.is_active == True,    # noqa
                )

            stmt = stmt.order_by(Subject.title.asc()).offset(offset).limit(limit)

            result = await session.execute(stmt)
            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"[SubjectService] list_subjects error: {e}", exc_info=True)
            raise
        
    # ---- List Deleted Subjects ---- #
    async def list_deleted_subjects(
        self,
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Subject]:

        try:
            stmt = (
                select(Subject)
                .where(
                    Subject.is_deleted == True,  # noqa
                )
                .order_by(Subject.updated_at.desc())
                .offset(offset)
                .limit(limit)
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(
                f"[SubjectService] list_deleted_subjects error: {e}",
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
            q = query.strip()

            stmt = (
                select(Subject)
                .where(
                    (Subject.title.ilike(f"%{q}%") |
                     Subject.code.ilike(f"%{q}%")),
                    Subject.is_deleted == False,  # noqa
                )
                .order_by(Subject.title.asc())
                .limit(limit)
            )

            result = await session.execute(stmt)
            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"[SubjectService] search error: {e}", exc_info=True)
            raise


    # ---- Update ---- #
    async def update(
        self,
        session: AsyncSession,
        subject_id: UUID,
        updates: dict,
    ) -> Subject:

        try:
            record = await self.get_by_id(session, subject_id)

            if not record:
                raise ValueError("subject not found")

            if record.is_deleted:
                raise ValueError("cannot update deleted subject")

            if "code" in updates:
                new_code = str(updates["code"]).strip().upper()

                stmt = select(Subject).where(
                    func.lower(Subject.code) == new_code.lower(),
                    Subject.id != subject_id,
                )

                result = await session.execute(stmt)

                if result.scalar_one_or_none():
                    raise ValueError("subject code already exists")

                updates["code"] = new_code

            updates["updated_at"] = datetime.utcnow()

            for k, v in updates.items():
                setattr(record, k, v)

            await session.commit()
            await session.refresh(record)

            return record

        except Exception as e:
            await session.rollback()
            logger.error(f"[SubjectService] update error: {e}", exc_info=True)
            raise


    # ---- Soft Delete ---- #
    async def delete(
        self,
        session: AsyncSession,
        subject_id: UUID,
    ) -> bool:

        try:
            stmt = select(Subject).where(Subject.id == subject_id)
            result = await session.execute(stmt)

            subject = result.scalar_one_or_none()

            if not subject:
                return False

            subject.is_deleted = True
            subject.is_active = False
            subject.updated_at = datetime.utcnow()

            await session.commit()
            return True

        except Exception as e:
            await session.rollback()
            logger.error(f"[SubjectService] delete error: {e}", exc_info=True)
            raise


    # ---- Hard Delete ---- #
    async def hard_delete(
        self,
        session: AsyncSession,
        subject_id: UUID,
    ) -> bool:

        try:
            stmt = delete(Subject).where(Subject.id == subject_id)

            result = await session.execute(stmt)
            await session.commit()

            return bool(getattr(result, "rowcount", 0))

        except Exception as e:
            await session.rollback()
            logger.error(f"[SubjectService] hard_delete error: {e}", exc_info=True)
            raise


    # ---- Stats ---- #
    async def stats(
        self,
        session: AsyncSession,
        subject_id: UUID,
    ) -> dict:

        try:
            chapter_stmt = select(func.count(Chapter.id)).where(
                Chapter.subject_id == subject_id
            )

            enrollment_stmt = select(func.count(Enrollment.id)).where(
                Enrollment.subject_id == subject_id
            )

            exam_stmt = select(func.count(Exam.id)).where(
                Exam.subject_id == subject_id
            )

            chapters = await session.execute(chapter_stmt)
            enrollments = await session.execute(enrollment_stmt)
            exams = await session.execute(exam_stmt)

            return {
                "chapters": int(chapters.scalar() or 0),
                "enrollments": int(enrollments.scalar() or 0),
                "exams": int(exams.scalar() or 0),
            }

        except Exception as e:
            logger.error(f"[SubjectService] stats error: {e}", exc_info=True)
            raise