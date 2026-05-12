# ---- Imports ---- #
import logging
from uuid import UUID

from sqlalchemy import select, func, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.education.models.skill import Skill
from src.domain.education.models.subject import Subject
from src.domain.education.models.chapter import Chapter
from src.domain.education.models.topic import Topic


# ---- Logging ---- #
logger = logging.getLogger(__name__)


# ---- Skill Service ---- #
class SkillService:

    # ---- Create ---- #
    async def create(
        self,
        session: AsyncSession,
        payload: dict,
    ) -> Skill | None:

        try:
            subject_id = payload["subject_id"]
            chapter_id = payload["chapter_id"]
            topic_id = payload["topic_id"]
            name = str(payload["name"]).strip()

            subject_stmt = select(Subject.id).where(Subject.id == subject_id)
            chapter_stmt = select(Chapter.id).where(Chapter.id == chapter_id)
            topic_stmt = select(Topic.id).where(Topic.id == topic_id)

            subject_result = await session.execute(subject_stmt)
            chapter_result = await session.execute(chapter_stmt)
            topic_result = await session.execute(topic_stmt)

            if not subject_result.scalar_one_or_none():
                return None

            if not chapter_result.scalar_one_or_none():
                return None

            if not topic_result.scalar_one_or_none():
                return None

            dedup_stmt = select(Skill.id).where(
                Skill.subject_id == subject_id,
                Skill.chapter_id == chapter_id,
                Skill.topic_id == topic_id,
                func.lower(Skill.name) == name.lower(),
            )

            dedup_result = await session.execute(dedup_stmt)
            existing_id = dedup_result.scalar_one_or_none()

            if existing_id:
                return await self.get_by_id(session, existing_id)

            record = Skill(
                subject_id=subject_id,
                chapter_id=chapter_id,
                topic_id=topic_id,
                name=name,
                description=payload.get("description"),
                importance_weight=float(payload.get("importance_weight", 1.0)),
            )

            session.add(record)
            await session.commit()
            await session.refresh(record)

            return record

        except IntegrityError as e:
            await session.rollback()
            logger.error(f"[SkillService] create integrity error: {e}", exc_info=True)
            raise

        except Exception as e:
            await session.rollback()
            logger.error(f"[SkillService] create error: {e}", exc_info=True)
            raise


    # ---- Bulk Create ---- #
    async def bulk_create(
        self,
        session: AsyncSession,
        payloads: list[dict],
    ) -> list[Skill]:

        try:
            if not payloads:
                return []

            subject_ids = {p["subject_id"] for p in payloads}
            chapter_ids = {p["chapter_id"] for p in payloads}
            topic_ids = {p["topic_id"] for p in payloads}

            subject_stmt = select(Subject.id).where(Subject.id.in_(subject_ids))
            chapter_stmt = select(Chapter.id).where(Chapter.id.in_(chapter_ids))
            topic_stmt = select(Topic.id).where(Topic.id.in_(topic_ids))

            subject_result = await session.execute(subject_stmt)
            chapter_result = await session.execute(chapter_stmt)
            topic_result = await session.execute(topic_stmt)

            existing_subjects = set(subject_result.scalars().all())
            existing_chapters = set(chapter_result.scalars().all())
            existing_topics = set(topic_result.scalars().all())

            if subject_ids - existing_subjects:
                return []

            if chapter_ids - existing_chapters:
                return []

            if topic_ids - existing_topics:
                return []

            existing_stmt = select(
                Skill.subject_id,
                Skill.chapter_id,
                Skill.topic_id,
                Skill.name,
            ).where(Skill.topic_id.in_(topic_ids))

            existing_result = await session.execute(existing_stmt)

            existing_set = {
                (s_id, c_id, t_id, name.lower())
                for s_id, c_id, t_id, name in existing_result.all()
            }

            records: list[Skill] = []

            for p in payloads:

                key = (
                    p["subject_id"],
                    p["chapter_id"],
                    p["topic_id"],
                    str(p["name"]).strip().lower(),
                )

                if key in existing_set:
                    continue

                records.append(
                    Skill(
                        subject_id=p["subject_id"],
                        chapter_id=p["chapter_id"],
                        topic_id=p["topic_id"],
                        name=str(p["name"]).strip(),
                        description=p.get("description"),
                        importance_weight=float(p.get("importance_weight", 1.0)),
                    )
                )

            session.add_all(records)
            await session.commit()

            for r in records:
                await session.refresh(r)

            return records

        except Exception as e:
            await session.rollback()
            logger.error(f"[SkillService] bulk_create error: {e}", exc_info=True)
            raise


    # ---- Exists ---- #
    async def exists(
        self,
        session: AsyncSession,
        skill_id: UUID,
    ) -> bool:

        try:
            stmt = select(Skill.id).where(Skill.id == skill_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none() is not None

        except Exception as e:
            logger.error(f"[SkillService] exists error: {e}", exc_info=True)
            raise


    # ---- Get By ID ---- #
    async def get_by_id(
        self,
        session: AsyncSession,
        skill_id: UUID,
    ) -> Skill | None:

        try:
            stmt = select(Skill).where(Skill.id == skill_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"[SkillService] get_by_id error: {e}", exc_info=True)
            raise


    # ---- Get Full ---- #
    async def get_full(
        self,
        session: AsyncSession,
        skill_id: UUID,
    ) -> Skill | None:

        try:
            stmt = (
                select(Skill)
                .options(
                    selectinload(Skill.subject),
                    selectinload(Skill.chapter),
                    selectinload(Skill.topic),
                    selectinload(Skill.skill_questions),
                )
                .where(Skill.id == skill_id)
            )

            result = await session.execute(stmt)
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"[SkillService] get_full error: {e}", exc_info=True)
            raise


    # ---- Get Many ---- #
    async def get_many_by_ids(
        self,
        session: AsyncSession,
        skill_ids: list[UUID],
    ) -> list[Skill]:

        try:
            if not skill_ids:
                return []

            stmt = select(Skill).where(Skill.id.in_(skill_ids))
            result = await session.execute(stmt)
            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"[SkillService] get_many_by_ids error: {e}", exc_info=True)
            raise


    # ---- List ---- #
    async def list_skills(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Skill]:

        try:
            stmt = (
                select(Skill)
                .order_by(Skill.name.asc())
                .limit(limit)
                .offset(offset)
            )

            result = await session.execute(stmt)
            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"[SkillService] list_skills error: {e}", exc_info=True)
            raise


    # ---- List By Topic ---- #
    async def list_by_topic(
        self,
        session: AsyncSession,
        topic_id: UUID,
    ) -> list[Skill]:

        try:
            stmt = (
                select(Skill)
                .where(Skill.topic_id == topic_id)
                .order_by(Skill.importance_weight.desc())
            )

            result = await session.execute(stmt)
            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"[SkillService] list_by_topic error: {e}", exc_info=True)
            raise


    # ---- Search ---- #
    async def search(
        self,
        session: AsyncSession,
        query: str,
        limit: int = 20,
    ) -> list[Skill]:

        try:
            q = query.strip()

            stmt = (
                select(Skill)
                .where(
                    Skill.name.ilike(f"%{q}%")
                    | Skill.description.ilike(f"%{q}%")
                )
                .order_by(Skill.importance_weight.desc())
                .limit(limit)
            )

            result = await session.execute(stmt)
            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"[SkillService] search error: {e}", exc_info=True)
            raise


    # ---- Count ---- #
    async def count(
        self,
        session: AsyncSession,
    ) -> int:

        try:
            stmt = select(func.count(Skill.id))
            result = await session.execute(stmt)
            return int(result.scalar() or 0)

        except Exception as e:
            logger.error(f"[SkillService] count error: {e}", exc_info=True)
            raise


    # ---- Delete ---- #
    async def delete(
        self,
        session: AsyncSession,
        skill_id: UUID,
    ) -> bool:

        try:
            record = await self.get_full(session, skill_id)

            if not record:
                return False

            if record.skill_questions:
                return False

            await session.delete(record)
            await session.commit()

            return True

        except Exception as e:
            await session.rollback()
            logger.error(f"[SkillService] delete error: {e}", exc_info=True)
            raise


    # ---- Hard Delete ---- #
    async def hard_delete(
        self,
        session: AsyncSession,
        skill_id: UUID,
    ) -> bool:

        try:
            stmt = delete(Skill).where(Skill.id == skill_id)
            result = await session.execute(stmt)
            await session.commit()

            affected = result.rowcount  # type: ignore
            return bool(affected and affected > 0)

        except Exception as e:
            await session.rollback()
            logger.error(f"[SkillService] hard_delete error: {e}", exc_info=True)
            raise