# ---- Imports ---- #
import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.questions.models.question_skill import QuestionSkill
from src.domain.questions.models.question import Question
from src.domain.education.models.skill import Skill


# ---- Logging ---- #
logger = logging.getLogger(__name__)


# ---- Question Skill Service ---- #
class QuestionSkillService:

    # ---- Create ---- #
    async def create(
        self,
        session: AsyncSession,
        payload: dict,
    ) -> QuestionSkill:

        try:
            question_id = payload["question_id"]
            skill_id = payload["skill_id"]

            question_stmt = select(Question.id).where(
                Question.id == question_id
            )

            skill_stmt = select(Skill.id).where(
                Skill.id == skill_id
            )

            question_result = await session.execute(question_stmt)
            skill_result = await session.execute(skill_stmt)

            if not question_result.scalar_one_or_none():
                raise ValueError("question not found")

            if not skill_result.scalar_one_or_none():
                raise ValueError("skill not found")

            record = QuestionSkill(
                question_id=question_id,
                skill_id=skill_id,
                weight=float(payload.get("weight", 1.0)),
            )

            session.add(record)

            await session.commit()
            await session.refresh(record)

            return record

        except IntegrityError as e:
            await session.rollback()

            logger.error(
                f"[QuestionSkillService] create integrity error: {e}",
                exc_info=True,
            )
            raise

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[QuestionSkillService] create error: {e}",
                exc_info=True,
            )
            raise


    # ---- Bulk Create ---- #
    async def bulk_create(
        self,
        session: AsyncSession,
        payloads: list[dict],
    ) -> list[QuestionSkill]:

        try:
            if not payloads:
                return []

            question_ids = {p["question_id"] for p in payloads}
            skill_ids = {p["skill_id"] for p in payloads}

            question_stmt = select(Question.id).where(
                Question.id.in_(question_ids)
            )

            skill_stmt = select(Skill.id).where(
                Skill.id.in_(skill_ids)
            )

            question_result = await session.execute(question_stmt)
            skill_result = await session.execute(skill_stmt)

            existing_questions = set(question_result.scalars().all())
            existing_skills = set(skill_result.scalars().all())

            if question_ids - existing_questions:
                raise ValueError("invalid question_ids")

            if skill_ids - existing_skills:
                raise ValueError("invalid skill_ids")

            records: list[QuestionSkill] = [
                QuestionSkill(
                    question_id=p["question_id"],
                    skill_id=p["skill_id"],
                    weight=float(p.get("weight", 1.0)),
                )
                for p in payloads
            ]

            session.add_all(records)

            await session.commit()

            for r in records:
                await session.refresh(r)

            return records

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[QuestionSkillService] bulk_create error: {e}",
                exc_info=True,
            )
            raise


    # ---- Get By ID ---- #
    async def get_by_id(
        self,
        session: AsyncSession,
        record_id: UUID,
    ) -> QuestionSkill | None:

        try:
            stmt = select(QuestionSkill).where(
                QuestionSkill.id == record_id
            )

            result = await session.execute(stmt)

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(
                f"[QuestionSkillService] get_by_id error: {e}",
                exc_info=True,
            )
            raise


    # ---- List By Question ---- #
    async def list_by_question(
        self,
        session: AsyncSession,
        question_id: UUID,
    ) -> list[QuestionSkill]:

        try:
            stmt = (
                select(QuestionSkill)
                .where(QuestionSkill.question_id == question_id)
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(
                f"[QuestionSkillService] list_by_question error: {e}",
                exc_info=True,
            )
            raise


    # ---- Update ---- #
    async def update(
        self,
        session: AsyncSession,
        record_id: UUID,
        updates: dict,
    ) -> QuestionSkill:

        try:
            record = await self.get_by_id(
                session=session,
                record_id=record_id,
            )

            if not record:
                raise ValueError("question skill not found")

            if "question_id" in updates or "skill_id" in updates:
                raise ValueError("foreign keys are immutable")

            if "weight" in updates:
                record.weight = float(updates["weight"])

            await session.commit()
            await session.refresh(record)

            return record

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[QuestionSkillService] update error: {e}",
                exc_info=True,
            )
            raise


    # ---- Delete ---- #
    async def delete(
        self,
        session: AsyncSession,
        record_id: UUID,
    ) -> bool:

        try:
            record = await self.get_by_id(
                session=session,
                record_id=record_id,
            )

            if not record:
                return False

            await session.delete(record)

            await session.commit()

            return True

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[QuestionSkillService] delete error: {e}",
                exc_info=True,
            )
            raise