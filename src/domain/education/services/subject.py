# ---- Imports ---- #
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.domain.education.models.subject import Subject


# ---- logging ---- #
logger = logging.getLogger(__name__)


# ---- Subject Service ---- #
class SubjectService:

    # ---- Create Subject ---- #
    async def create(
        self,
        session: AsyncSession,
        data: dict,
    ) -> Subject:

        try:
            logger.debug(f"[SubjectService] create: {data}")

            # ---- ensure unique code ---- #
            stmt = select(Subject).where(Subject.code == data.get("code"))
            result = await session.execute(stmt)

            if result.scalar_one_or_none():
                raise ValueError("subject code already exists")

            record = Subject(**data)

            session.add(record)
            await session.commit()
            await session.refresh(record)

            return record

        except Exception as e:
            logger.error(f"[SubjectService] create error: {e}", exc_info=True)
            raise


    # ---- Get By ID ---- #
    async def get_by_id(
        self,
        session: AsyncSession,
        subject_id: int,
    ) -> Subject | None:

        try:
            return await session.get(Subject, subject_id)

        except Exception as e:
            logger.error(f"[SubjectService] get_by_id error: {e}", exc_info=True)
            raise


    # ---- Get By Code ---- #
    async def get_by_code(
        self,
        session: AsyncSession,
        code: str,
    ) -> Subject | None:

        try:
            stmt = select(Subject).where(Subject.code == code)
            result = await session.execute(stmt)

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"[SubjectService] get_by_code error: {e}", exc_info=True)
            raise


    # ---- List Subjects ---- #
    async def list(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Subject]:

        try:
            stmt = select(Subject).offset(offset).limit(limit)
            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"[SubjectService] list error: {e}", exc_info=True)
            raise


    # ---- Search ---- #
    async def search(
        self,
        session: AsyncSession,
        query: str,
        limit: int = 20,
    ) -> list[Subject]: # type: ignore

        try:
            stmt = select(Subject).where(
                Subject.title.ilike(f"%{query}%")
            ).limit(limit)

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"[SubjectService] search error: {e}", exc_info=True)
            raise


    # ---- Update Subject ---- #
    async def update(
        self,
        session: AsyncSession,
        subject_id: int,
        updates: dict,
    ) -> Subject:

        try:
            record = await session.get(Subject, subject_id)

            if not record:
                raise ValueError("subject not found")

            # ---- protected fields ---- #
            protected = {"id"}

            # ---- enforce unique code update ---- #
            if "code" in updates:
                stmt = select(Subject).where(
                    Subject.code == updates["code"]
                )
                result = await session.execute(stmt)

                existing = result.scalar_one_or_none()

                if existing and existing.id != subject_id:
                    raise ValueError("subject code already exists")

            for k, v in updates.items():
                if k in protected:
                    continue
                setattr(record, k, v)

            await session.commit()
            await session.refresh(record)

            return record

        except Exception as e:
            logger.error(f"[SubjectService] update error: {e}", exc_info=True)
            raise


    # ---- Delete Subject ---- #
    async def delete(
        self,
        session: AsyncSession,
        subject_id: int,
    ) -> bool:

        try:
            record = await session.get(Subject, subject_id)

            if not record:
                return False

            await session.delete(record)
            await session.commit()

            return True

        except Exception as e:
            logger.error(f"[SubjectService] delete error: {e}", exc_info=True)
            raise


    # ---- Get Subject With Relations ---- #
    async def get_full(
        self,
        session: AsyncSession,
        subject_id: int,
    ) -> Subject | None:

        try:
            stmt = select(Subject).where(
                Subject.id == subject_id
            )

            result = await session.execute(stmt)

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"[SubjectService] get_full error: {e}", exc_info=True)
            raise


    # ---- Stats ---- #
    async def stats(
        self,
        session: AsyncSession,
        subject_id: int,
    ) -> dict:

        try:
            # ---- chapters count ---- #
            chapters = await session.execute(
                select(func.count()).select_from(
                    Subject.chapters.property.mapper.class_
                ).where(
                    Subject.chapters.property.mapper.class_.subject_id == subject_id
                )
            )

            # ---- exams count ---- #
            exams = await session.execute(
                select(func.count()).select_from(
                    Subject.exams.property.mapper.class_
                ).where(
                    Subject.exams.property.mapper.class_.subject_id == subject_id
                )
            )

            # ---- enrollments count ---- #
            enrollments = await session.execute(
                select(func.count()).select_from(
                    Subject.enrollments.property.mapper.class_
                ).where(
                    Subject.enrollments.property.mapper.class_.subject_id == subject_id
                )
            )

            return {
                "chapters": chapters.scalar(),
                "exams": exams.scalar(),
                "enrollments": enrollments.scalar(),
            }

        except Exception as e:
            logger.error(f"[SubjectService] stats error: {e}", exc_info=True)
            raise