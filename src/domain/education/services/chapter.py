# ---- Imports ---- #
import logging
from uuid import UUID

from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.education.models.chapter import Chapter
from src.domain.education.models.subject import Subject
from src.domain.education.models.topic import Topic
from src.domain.education.models.skill import Skill
from src.domain.questions.models.question import Question


# ---- Logging ---- #
logger = logging.getLogger(__name__)


# ---- Chapter Service ---- #
class ChapterService:

    # ---- Create ---- #
    async def create(
        self,
        session: AsyncSession,
        data: dict,
    ) -> Chapter:

        try:
            subject_stmt = select(Subject.id).where(
                Subject.id == data["subject_id"]
            )

            subject_result = await session.execute(subject_stmt)

            if not subject_result.scalar_one_or_none():
                raise ValueError("subject not found")

            order_index = data.get("order_index")

            if order_index is None:
                max_stmt = select(
                    func.max(Chapter.order_index)
                ).where(
                    Chapter.subject_id == data["subject_id"]
                )

                max_result = await session.execute(max_stmt)

                current_max = max_result.scalar()

                order_index = (
                    int(current_max) + 1
                    if current_max is not None
                    else 0
                )

            record = Chapter(
                subject_id=data["subject_id"],
                title=str(data["title"]).strip(),
                description=data.get("description"),
                order_index=order_index,
            )

            session.add(record)

            await session.commit()
            await session.refresh(record)

            return record

        except IntegrityError as e:
            await session.rollback()

            logger.error(
                f"[ChapterService] create integrity error: {e}",
                exc_info=True,
            )

            raise

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[ChapterService] create error: {e}",
                exc_info=True,
            )

            raise


    # ---- Bulk Create ---- #
    async def bulk_create(
        self,
        session: AsyncSession,
        payloads: list[dict],
    ) -> list[Chapter]:

        try:
            if not payloads:
                return []

            subject_ids = {
                payload["subject_id"]
                for payload in payloads
            }

            subject_stmt = select(Subject.id).where(
                Subject.id.in_(subject_ids)
            )

            subject_result = await session.execute(subject_stmt)

            existing_subject_ids = set(
                subject_result.scalars().all()
            )

            missing_subjects = (
                subject_ids - existing_subject_ids
            )

            if missing_subjects:
                raise ValueError(
                    f"subjects not found: {missing_subjects}"
                )

            records: list[Chapter] = []

            for payload in payloads:
                order_index = payload.get("order_index")

                if order_index is None:
                    max_stmt = select(
                        func.max(Chapter.order_index)
                    ).where(
                        Chapter.subject_id == payload["subject_id"]
                    )

                    max_result = await session.execute(max_stmt)

                    current_max = max_result.scalar()

                    order_index = (
                        int(current_max) + 1
                        if current_max is not None
                        else 0
                    )

                records.append(
                    Chapter(
                        subject_id=payload["subject_id"],
                        title=str(payload["title"]).strip(),
                        description=payload.get("description"),
                        order_index=order_index,
                    )
                )

            session.add_all(records)

            await session.commit()

            for record in records:
                await session.refresh(record)

            return records

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[ChapterService] bulk_create error: {e}",
                exc_info=True,
            )

            raise


    # ---- Exists ---- #
    async def exists(
        self,
        session: AsyncSession,
        chapter_id: UUID,
    ) -> bool:

        try:
            stmt = select(Chapter.id).where(
                Chapter.id == chapter_id
            )

            result = await session.execute(stmt)

            return result.scalar_one_or_none() is not None

        except Exception as e:
            logger.error(
                f"[ChapterService] exists error: {e}",
                exc_info=True,
            )

            raise


    # ---- Get By ID ---- #
    async def get_by_id(
        self,
        session: AsyncSession,
        chapter_id: UUID,
    ) -> Chapter | None:

        try:
            stmt = select(Chapter).where(
                Chapter.id == chapter_id
            )

            result = await session.execute(stmt)

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(
                f"[ChapterService] get_by_id error: {e}",
                exc_info=True,
            )

            raise


    # ---- Get Full ---- #
    async def get_full(
        self,
        session: AsyncSession,
        chapter_id: UUID,
    ) -> Chapter | None:

        try:
            stmt = (
                select(Chapter)
                .options(
                    selectinload(Chapter.subject),
                    selectinload(Chapter.topics),
                    selectinload(Chapter.skills),
                    selectinload(Chapter.questions),
                )
                .where(Chapter.id == chapter_id)
            )

            result = await session.execute(stmt)

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(
                f"[ChapterService] get_full error: {e}",
                exc_info=True,
            )

            raise


    # ---- Get Many By IDs ---- #
    async def get_many_by_ids(
        self,
        session: AsyncSession,
        chapter_ids: list[UUID],
    ) -> list[Chapter]:

        try:
            if not chapter_ids:
                return []

            stmt = select(Chapter).where(
                Chapter.id.in_(chapter_ids)
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(
                f"[ChapterService] get_many_by_ids error: {e}",
                exc_info=True,
            )

            raise


    # ---- List ---- #
    async def list_chapters(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Chapter]:

        try:
            stmt = (
                select(Chapter)
                .order_by(
                    Chapter.order_index.asc(),
                    Chapter.title.asc(),
                )
                .offset(offset)
                .limit(limit)
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(
                f"[ChapterService] list_chapters error: {e}",
                exc_info=True,
            )

            raise


    # ---- List By Subject ---- #
    async def list_by_subject(
        self,
        session: AsyncSession,
        subject_id: UUID,
    ) -> list[Chapter]:

        try:
            stmt = (
                select(Chapter)
                .where(Chapter.subject_id == subject_id)
                .order_by(
                    Chapter.order_index.asc(),
                    Chapter.title.asc(),
                )
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(
                f"[ChapterService] list_by_subject error: {e}",
                exc_info=True,
            )

            raise


    # ---- Search ---- #
    async def search(
        self,
        session: AsyncSession,
        query: str,
        limit: int = 20,
    ) -> list[Chapter]:

        try:
            normalized_query = query.strip()

            stmt = (
                select(Chapter)
                .where(
                    Chapter.title.ilike(f"%{normalized_query}%")
                    | Chapter.description.ilike(
                        f"%{normalized_query}%"
                    )
                )
                .order_by(Chapter.order_index.asc())
                .limit(limit)
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(
                f"[ChapterService] search error: {e}",
                exc_info=True,
            )

            raise


    # ---- Count ---- #
    async def count(
        self,
        session: AsyncSession,
    ) -> int:

        try:
            stmt = select(func.count(Chapter.id))

            result = await session.execute(stmt)

            return int(result.scalar() or 0)

        except Exception as e:
            logger.error(
                f"[ChapterService] count error: {e}",
                exc_info=True,
            )

            raise


    # ---- Count By Subject ---- #
    async def count_by_subject(
        self,
        session: AsyncSession,
        subject_id: UUID,
    ) -> int:

        try:
            stmt = select(
                func.count(Chapter.id)
            ).where(
                Chapter.subject_id == subject_id
            )

            result = await session.execute(stmt)

            return int(result.scalar() or 0)

        except Exception as e:
            logger.error(
                f"[ChapterService] count_by_subject error: {e}",
                exc_info=True,
            )

            raise


    # ---- Update ---- #
    async def update(
        self,
        session: AsyncSession,
        chapter_id: UUID,
        updates: dict,
    ) -> Chapter:

        try:
            record = await self.get_by_id(
                session=session,
                chapter_id=chapter_id,
            )

            if not record:
                raise ValueError("chapter not found")

            protected_fields = {"id"}

            if "subject_id" in updates:
                subject_stmt = select(Subject.id).where(
                    Subject.id == updates["subject_id"]
                )

                subject_result = await session.execute(
                    subject_stmt
                )

                if not subject_result.scalar_one_or_none():
                    raise ValueError("subject not found")

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
                f"[ChapterService] update error: {e}",
                exc_info=True,
            )

            raise


    # ---- Reorder ---- #
    async def reorder(
        self,
        session: AsyncSession,
        chapter_id: UUID,
        order_index: int,
    ) -> bool:

        try:
            stmt = (
                update(Chapter)
                .where(Chapter.id == chapter_id)
                .values(order_index=order_index)
            )

            result = await session.execute(stmt)

            await session.commit()

            return bool(getattr(result, "rowcount", 0))

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[ChapterService] reorder error: {e}",
                exc_info=True,
            )

            raise


    # ---- Delete ---- #
    async def delete(
        self,
        session: AsyncSession,
        chapter_id: UUID,
    ) -> bool:

        try:
            record = await self.get_full(
                session=session,
                chapter_id=chapter_id,
            )

            if not record:
                return False

            if record.topics:
                raise ValueError(
                    "cannot delete chapter with topics"
                )

            if record.skills:
                raise ValueError(
                    "cannot delete chapter with skills"
                )

            if record.questions:
                raise ValueError(
                    "cannot delete chapter with questions"
                )

            await session.delete(record)

            await session.commit()

            return True

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[ChapterService] delete error: {e}",
                exc_info=True,
            )

            raise


    # ---- Hard Delete ---- #
    async def hard_delete(
        self,
        session: AsyncSession,
        chapter_id: UUID,
    ) -> bool:

        try:
            stmt = delete(Chapter).where(
                Chapter.id == chapter_id
            )

            result = await session.execute(stmt)

            await session.commit()

            return bool(getattr(result, "rowcount", 0))

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[ChapterService] hard_delete error: {e}",
                exc_info=True,
            )

            raise


    # ---- Stats ---- #
    async def stats(
        self,
        session: AsyncSession,
        chapter_id: UUID,
    ) -> dict:

        try:
            topics_stmt = select(
                func.count(Topic.id)
            ).where(
                Topic.chapter_id == chapter_id
            )

            skills_stmt = select(
                func.count(Skill.id)
            ).where(
                Skill.chapter_id == chapter_id
            )

            questions_stmt = select(
                func.count(Question.id)
            ).where(
                Question.chapter_id == chapter_id
            )

            topics_result = await session.execute(topics_stmt)
            skills_result = await session.execute(skills_stmt)
            questions_result = await session.execute(
                questions_stmt
            )

            return {
                "topics": int(topics_result.scalar() or 0),
                "skills": int(skills_result.scalar() or 0),
                "questions": int(
                    questions_result.scalar() or 0
                ),
            }

        except Exception as e:
            logger.error(
                f"[ChapterService] stats error: {e}",
                exc_info=True,
            )

            raise