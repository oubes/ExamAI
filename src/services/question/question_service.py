# ----- IMPORTS ----- #
import logging
from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.domain.questions.models.option import QuestionOption
from src.domain.questions.models.question import Question


# ----- LOGGING ----- #
logger = logging.getLogger(__name__)


# ----- AGGREGATE SERVICE ----- #
class QuestionAggregateService:

    # ---- INTERNAL SERIALIZER ---- #
    def _bundle(self, question: Question) -> dict:

        options = getattr(question, "options", []) or []
        model_answer = getattr(question, "model_answer", None)

        return {
            "question": {
                "id": question.id,
                "subject_id": question.subject_id,
                "chapter_id": question.chapter_id,
                "topic_id": question.topic_id,
                "content": question.content,
                "type": question.type,
                "difficulty": question.difficulty,
                "importance": question.importance,
            },

            "options": [
                {
                    "id": o.id,
                    "question_id": o.question_id,
                    "option_text": getattr(o, "option_text", None),
                    "is_correct": getattr(o, "is_correct", False),
                    "order": getattr(o, "order", 0),
                }
                for o in options
            ],

            "model_answer": (
                {
                    "id": model_answer.id,
                    "question_id": model_answer.question_id,
                    "answer_text": getattr(model_answer, "answer_text", None),
                }
                if model_answer else None
            ),
        }

    # ---- GET SINGLE ---- #
    async def get_full_question(
        self,
        session: AsyncSession,
        question_id: UUID,
    ) -> dict | None:

        try:
            stmt = (
                select(Question)
                .options(
                    selectinload(Question.options),
                    selectinload(Question.model_answer),
                )
                .where(Question.id == question_id)
            )

            result = await session.execute(stmt)
            question = result.scalar_one_or_none()

            if not question:
                return None

            return self._bundle(question)

        except Exception as e:
            logger.error(
                f"[QuestionAggregateService] get_full_question error: {e}",
                exc_info=True,
            )
            raise

    # ---- LIST ---- #
    async def list_full_questions(
        self,
        session: AsyncSession,
        subject_id: UUID | None = None,
        chapter_id: UUID | None = None,
        topic_id: UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:

        try:
            stmt = (
                select(Question)
                .options(
                    selectinload(Question.options),
                    selectinload(Question.model_answer),
                )
                .offset(offset)
                .limit(limit)
            )

            if subject_id:
                stmt = stmt.where(Question.subject_id == subject_id)

            if chapter_id:
                stmt = stmt.where(Question.chapter_id == chapter_id)

            if topic_id:
                stmt = stmt.where(Question.topic_id == topic_id)

            result = await session.execute(stmt)
            questions = result.scalars().all()

            return [self._bundle(q) for q in questions]

        except Exception as e:
            logger.error(
                f"[QuestionAggregateService] list_full_questions error: {e}",
                exc_info=True,
            )
            raise

    # ---- SEARCH ---- #
    async def search_questions(
        self,
        session: AsyncSession,
        query: str,
        limit: int = 20,
    ) -> list[dict]:

        try:
            stmt = (
                select(Question)
                .options(
                    selectinload(Question.options),
                    selectinload(Question.model_answer),
                )
                .where(Question.content.ilike(f"%{query}%"))
                .limit(limit)
            )

            result = await session.execute(stmt)
            questions = result.scalars().all()

            return [self._bundle(q) for q in questions]

        except Exception as e:
            logger.error(
                f"[QuestionAggregateService] search_questions error: {e}",
                exc_info=True,
            )
            raise

    # ----- UPDATE MCQ OPTIONS ----- #
    async def update_mcq_options(
        self,
        session: AsyncSession,
        question: Question,
        options: list[dict],
    ) -> None:

        await session.execute(
            delete(QuestionOption).where(QuestionOption.question_id == question.id)
        )

        question.options = []

        for opt in options:
            question.options.append(
                Question.options.property.mapper.class_(
                    option_text=opt.get("option_text"),
                    is_correct=opt.get("is_correct", False),
                    order=opt.get("order", 0),
                )
            )


    # ----- UPDATE WRITTEN MODEL ANSWER ----- #
    async def update_written_model_answer(
        self,
        session: AsyncSession,
        question: Question,
        model_answer: str | None,
    ) -> None:

        if model_answer is None:
            question.model_answer = None
            return

        if isinstance(model_answer, str):
            if question.model_answer:
                question.model_answer.answer_text = model_answer
            else:
                question.model_answer = Question.model_answer.property.mapper.class_(
                    answer_text=model_answer
                )
            return

        if isinstance(model_answer, dict):
            if question.model_answer:
                question.model_answer.answer_text = model_answer.get("answer_text")
            else:
                question.model_answer = Question.model_answer.property.mapper.class_(
                    answer_text=model_answer.get("answer_text")
                )
            return


    # ----- UPDATE (FULL ORM OWNERSHIP) ----- #
    async def update_full_question(
        self,
        session: AsyncSession,
        question_id: UUID,
        payload: dict,
    ) -> dict:

        try:
            stmt = (
                select(Question)
                .options(
                    selectinload(Question.options),
                    selectinload(Question.model_answer),
                )
                .where(Question.id == question_id)
            )

            result = await session.execute(stmt)
            question = result.scalar_one_or_none()

            if not question:
                raise ValueError("question not found")

            # ----- QUESTION FIELDS ----- #
            for k in ["content", "explanation", "difficulty", "importance", "tags"]:
                if k in payload and payload[k] is not None:
                    setattr(question, k, payload[k])

            # ----- MCQ ----- #
            if question.type == "mcq" and "options" in payload and payload["options"] is not None:
                await self.update_mcq_options(session, question, payload["options"])

            # ----- WRITTEN ----- #
            if question.type == "written" and "model_answer" in payload:
                await self.update_written_model_answer(session, question, payload["model_answer"])

            await session.commit()
            await session.refresh(question)

            return self._bundle(question)

        except Exception as e:
            await session.rollback()
            logger.error(
                f"[QuestionAggregateService] update_full_question error: {e}",
                exc_info=True,
            )
            raise

    # ---- DELETE ---- #
    async def delete_full_question(
        self,
        session: AsyncSession,
        question_id: UUID,
    ) -> bool:

        try:
            stmt = select(Question).where(Question.id == question_id)
            result = await session.execute(stmt)
            question = result.scalar_one_or_none()

            if not question:
                return False

            await session.delete(question)
            await session.commit()

            return True

        except Exception as e:
            await session.rollback()
            logger.error(
                f"[QuestionAggregateService] delete_full_question error: {e}",
                exc_info=True,
            )
            raise