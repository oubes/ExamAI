# ---- Imports ---- #
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from src.domain.education.models.skill import Skill
from src.domain.education.models.topic import Topic
from src.domain.education.models.chapter import Chapter


# ---- logging ---- #
logger = logging.getLogger(__name__)


# ---- Skill Service ---- #
class SkillService:

    # ---- Create Skill ---- #
    async def create(
        self,
        session: AsyncSession,
        data: dict,
    ) -> Skill:

        try:
            logger.debug(f"[SkillService] create: {data}")

            # ---- validate full hierarchy consistency ---- #
            stmt = select(Topic).where(
                and_(
                    Topic.id == data["topic_id"],
                    Topic.chapter_id == data["chapter_id"],
                    Topic.subject_id == data["subject_id"],
                )
            )

            result = await session.execute(stmt)
            topic = result.scalar_one_or_none()

            if not topic:
                raise ValueError("invalid subject/chapter/topic relationship")

            record = Skill(**data)

            session.add(record)
            await session.commit()
            await session.refresh(record)

            return record

        except Exception as e:
            logger.error(f"[SkillService] create error: {e}", exc_info=True)
            raise


    # ---- Get By ID ---- #
    async def get_by_id(
        self,
        session: AsyncSession,
        skill_id: int,
    ) -> Skill | None:

        try:
            return await session.get(Skill, skill_id)

        except Exception as e:
            logger.error(f"[SkillService] get_by_id error: {e}", exc_info=True)
            raise


    # ---- Get By Topic ---- #
    async def get_by_topic(
        self,
        session: AsyncSession,
        topic_id: int,
    ) -> list[Skill]:

        try:
            stmt = select(Skill).where(
                Skill.topic_id == topic_id
            ).order_by(
                Skill.importance_weight.desc()
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"[SkillService] get_by_topic error: {e}", exc_info=True)
            raise


    # ---- Get By Chapter ---- #
    async def get_by_chapter(
        self,
        session: AsyncSession,
        chapter_id: int,
    ) -> list[Skill]:

        try:
            stmt = select(Skill).where(
                Skill.chapter_id == chapter_id
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"[SkillService] get_by_chapter error: {e}", exc_info=True)
            raise


    # ---- Get By Subject ---- #
    async def get_by_subject(
        self,
        session: AsyncSession,
        subject_id: int,
    ) -> list[Skill]:

        try:
            stmt = select(Skill).where(
                Skill.subject_id == subject_id
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"[SkillService] get_by_subject error: {e}", exc_info=True)
            raise


    # ---- Update Skill ---- #
    async def update(
        self,
        session: AsyncSession,
        skill_id: int,
        updates: dict,
    ) -> Skill:

        try:
            record = await session.get(Skill, skill_id)

            if not record:
                raise ValueError("skill not found")

            # ---- protected fields ---- #
            protected = {"id", "subject_id", "chapter_id", "topic_id"}

            # ---- revalidate hierarchy if changed ---- #
            if any(k in updates for k in ["topic_id", "chapter_id", "subject_id"]):
                stmt = select(Topic).where(
                    and_(
                        Topic.id == updates.get("topic_id", record.topic_id),
                        Topic.chapter_id == updates.get("chapter_id", record.chapter_id),
                        Topic.subject_id == updates.get("subject_id", record.subject_id),
                    )
                )

                result = await session.execute(stmt)
                valid = result.scalar_one_or_none()

                if not valid:
                    raise ValueError("invalid hierarchy relationship")

            for key, value in updates.items():
                if key in protected:
                    continue
                setattr(record, key, value)

            await session.commit()
            await session.refresh(record)

            return record

        except Exception as e:
            logger.error(f"[SkillService] update error: {e}", exc_info=True)
            raise


    # ---- Delete Skill ---- #
    async def delete(
        self,
        session: AsyncSession,
        skill_id: int,
    ) -> bool:

        try:
            record = await session.get(Skill, skill_id)

            if not record:
                return False

            await session.delete(record)
            await session.commit()

            return True

        except Exception as e:
            logger.error(f"[SkillService] delete error: {e}", exc_info=True)
            raise


    # ---- Search ---- #
    async def search(
        self,
        session: AsyncSession,
        query: str,
        topic_id: int | None = None,
    ) -> list[Skill]:

        try:
            query = query.strip()

            if not query:
                return []

            stmt = select(Skill).where(
                Skill.name.ilike(f"%{query}%")
            )

            if topic_id:
                stmt = stmt.where(Skill.topic_id == topic_id)

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"[SkillService] search error: {e}", exc_info=True)
            raise


    # ---- Stats ---- #
    async def stats(
        self,
        session: AsyncSession,
        topic_id: int,
    ) -> dict:

        try:
            stmt = select(func.count()).where(
                Skill.topic_id == topic_id
            )

            result = await session.execute(stmt)

            return {
                "total": result.scalar()
            }

        except Exception as e:
            logger.error(f"[SkillService] stats error: {e}", exc_info=True)
            raise