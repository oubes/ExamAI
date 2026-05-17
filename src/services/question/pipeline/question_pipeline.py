# ----- IMPORTS ----- #
import logging

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.di.llm import get_llm_service

from src.services.question.core.settings import Settings

from src.services.question.models.mcq_model import generate_mcq
from src.services.question.models.written_model import generate_written

from src.services.question.utils.utils import normalize_mcq

from src.domain.questions.services.question import QuestionService
from src.domain.questions.services.option import QuestionOptionService
from src.domain.questions.services.model_answer import ModelAnswerService
from src.domain.questions.services.question_skill import QuestionSkillService
from src.domain.questions.services.chunk import ChunkService


# ----- LOGGER ----- #
logger = logging.getLogger(__name__)


# ----- SETTINGS ----- #
settings = Settings()

DIFFICULTY_MAP = {
    "easy": 1,
    "medium": 2,
    "hard": 3,
}


# ----- QUESTION PIPELINE ----- #
class QuestionPipeline:

    # ----- INIT ----- #
    def __init__(self):

        self.llm = None

        self.question_service = QuestionService()
        self.option_service = QuestionOptionService()
        self.model_answer_service = ModelAnswerService()
        self.question_skill_service = QuestionSkillService()
        self.chunk_service = ChunkService()

    # ----- RUN ----- #
    async def run(
        self,
        session: AsyncSession,
        book_id: str,
        subject_id: str,
    ):

        logger.info("[PIPELINE] started")

        self.llm = await get_llm_service()

        chunks = await self.fetch_chunks(
            session=session,
            subject_id=subject_id,
            book_id=book_id,
        )

        logger.info(
            "[PIPELINE] chunks loaded | count=%s",
            len(chunks),
        )

        if not chunks:

            logger.warning("[PIPELINE] empty chunks")

            return {
                "status": "empty",
            }

        for index, chunk in enumerate(chunks):

            await self.process_chunk(
                session=session,
                chunk=chunk,
                chunk_index=index,
                subject_id=subject_id,
            )

        logger.info("[PIPELINE] committing session")

        await session.commit()

        logger.info("[PIPELINE] completed")

        return {
            "status": "completed",
            "chunks": len(chunks),
        }

    # ----- FETCH CHUNKS ----- #
    async def fetch_chunks(
        self,
        session: AsyncSession,
        subject_id: str,
        book_id: str,
    ):

        logger.info("[PIPELINE] fetching chunks")

        return await self.chunk_service.list_by_filters(
            session=session,
            subject_id=UUID(subject_id),
            book_id=UUID(book_id),
        )

    # ----- PROCESS CHUNK ----- #
    async def process_chunk(
        self,
        session: AsyncSession,
        chunk,
        chunk_index: int,
        subject_id: str,
    ):

        logger.info(
            "[CHUNK] started | index=%s | chapter_id=%s | topic_id=%s",
            chunk_index,
            chunk.chapter_id,
            chunk.topic_id,
        )

        topic_text = chunk.content
        topic_summary = topic_text[:1000]

        skills = getattr(chunk, "skills", []) or []

        logger.info(
            "[CHUNK] skills loaded | index=%s | count=%s",
            chunk_index,
            len(skills),
        )

        await self.process_mcq(
            session=session,
            chunk=chunk,
            subject_id=subject_id,
            topic_text=topic_text,
            topic_summary=topic_summary,
            skills=skills,
        )

        await self.process_written(
            session=session,
            chunk=chunk,
            subject_id=subject_id,
            topic_text=topic_text,
            topic_summary=topic_summary,
            skills=skills,
        )

        logger.info(
            "[CHUNK] completed | index=%s",
            chunk_index,
        )

    # ----- PROCESS MCQ ----- #
    async def process_mcq(
        self,
        session: AsyncSession,
        chunk,
        subject_id: str,
        topic_text: str,
        topic_summary: str,
        skills: list,
    ):

        for difficulty in settings.DIFFICULTY_LEVELS:

            logger.info(
                "[MCQ] generating | difficulty=%s",
                difficulty,
            )

            mcq_resp = await generate_mcq(
                self.llm,
                topic_text,
                topic_summary,
                difficulty,
            )

            logger.info(
                "[MCQ] response keys=%s",
                list(mcq_resp.keys()),
            )

            questions = mcq_resp.get("questions", [])

            logger.info(
                "[MCQ] questions count=%s",
                len(questions),
            )

            for q_index, q in enumerate(questions):

                q = normalize_mcq(q)

                logger.info(
                    "[MCQ] processing question | index=%s",
                    q_index,
                )

                question = await self.create_question(
                    session=session,
                    chunk=chunk,
                    subject_id=subject_id,
                    q=q,
                    difficulty=difficulty,
                    question_type="mcq",
                )

                await self.create_options(
                    session=session,
                    question_id=question.id,
                    q=q,
                )

                await self.link_skills(
                    session=session,
                    question_id=question.id,
                    skills=skills,
                    question_type="mcq",
                )

    # ----- PROCESS WRITTEN ----- #
    async def process_written(
        self,
        session: AsyncSession,
        chunk,
        subject_id: str,
        topic_text: str,
        topic_summary: str,
        skills: list,
    ):

        for difficulty in settings.DIFFICULTY_LEVELS:

            logger.info(
                "[WRITTEN] generating | difficulty=%s",
                difficulty,
            )

            written_resp = await generate_written(
                self.llm,
                topic_text,
                topic_summary,
                difficulty,
            )

            logger.info(
                "[WRITTEN] response keys=%s",
                list(written_resp.keys()),
            )

            questions = written_resp.get("questions", [])

            logger.info(
                "[WRITTEN] questions count=%s",
                len(questions),
            )

            for q_index, q in enumerate(questions):

                logger.info(
                    "[WRITTEN] processing question | index=%s",
                    q_index,
                )

                question = await self.create_question(
                    session=session,
                    chunk=chunk,
                    subject_id=subject_id,
                    q=q,
                    difficulty=difficulty,
                    question_type="written",
                )

                await self.create_model_answer(
                    session=session,
                    question_id=question.id,
                    q=q,
                )

                await self.link_skills(
                    session=session,
                    question_id=question.id,
                    skills=skills,
                    question_type="written",
                )

    # ----- CREATE QUESTION ----- #
    async def create_question(
        self,
        session: AsyncSession,
        chunk,
        subject_id: str,
        q: dict,
        difficulty: str,
        question_type: str,
    ):

        question = await self.question_service.create(
            session=session,
            payload={
                "subject_id": subject_id,
                "chapter_id": chunk.chapter_id,
                "topic_id": chunk.topic_id,
                "content": q.get("question") or q.get("content"),
                "explanation": q.get("explanation"),
                "type": question_type,
                "difficulty": DIFFICULTY_MAP[difficulty],
                "importance": q.get("importance", 1),
                "tags": ",".join(q.get("tags", []))
                if isinstance(q.get("tags"), list)
                else q.get("tags"),
                "embedding": q.get("embedding", []),
            },
        )

        logger.info(
            "[%s] stored question | question_id=%s",
            question_type.upper(),
            question.id,
        )

        return question

    # ----- CREATE OPTIONS ----- #
    async def create_options(
        self,
        session: AsyncSession,
        question_id,
        q: dict,
    ):

        options = self.normalize_options(q)

        logger.info(
            "[MCQ] normalized options count=%s | question_id=%s",
            len(options),
            question_id,
        )

        for index, option_data in enumerate(options):

            option_text = option_data.get("text")

            if not option_text:
                continue

            option = await self.option_service.create(
                session=session,
                payload={
                    "question_id": question_id,
                    "option_text": option_text,
                    "is_correct": option_data.get("is_correct", False),
                    "order": index,
                },
            )

            logger.info(
                "[MCQ] stored option | option_id=%s | question_id=%s",
                option.id,
                question_id,
            )

    # ----- CREATE MODEL ANSWER ----- #
    async def create_model_answer(
        self,
        session: AsyncSession,
        question_id,
        q: dict,
    ):

        answer = q.get("answer")

        if not answer:
            return

        model_answer = await self.model_answer_service.create(
            session=session,
            payload={
                "question_id": question_id,
                "answer_text": answer,
            },
        )

        logger.info(
            "[WRITTEN] stored model answer | answer_id=%s | question_id=%s",
            model_answer.id,
            question_id,
        )

    # ----- LINK SKILLS ----- #
    async def link_skills(
        self,
        session: AsyncSession,
        question_id,
        skills: list,
        question_type: str,
    ):

        logger.info(
            "[%s] linking skills | question_id=%s | count=%s",
            question_type.upper(),
            question_id,
            len(skills),
        )

        for skill_id in skills:

            link = await self.question_skill_service.create(
                session=session,
                payload={
                    "question_id": question_id,
                    "skill_id": skill_id,
                    "weight": 1.0,
                },
            )

            logger.info(
                "[%s] stored skill link | link_id=%s | question_id=%s | skill_id=%s",
                question_type.upper(),
                link.id,
                question_id,
                skill_id,
            )

    # ----- NORMALIZE OPTIONS ----- #
    def normalize_options(
        self,
        q: dict,
    ) -> list[dict]:

        options = q.get("options")

        if options is None:

            choices = q.get("choices", [])

            if isinstance(choices, dict):

                options = [
                    {
                        "text": value,
                        "is_correct": False,
                    }
                    for value in choices.values()
                ]

            else:

                options = [
                    {
                        "text": choice,
                        "is_correct": False,
                    }
                    for choice in choices
                ]

        normalized_options = []

        for option in options:

            if isinstance(option, str):

                normalized_options.append(
                    {
                        "text": option,
                        "is_correct": False,
                    }
                )

            elif isinstance(option, dict):

                normalized_options.append(
                    {
                        "text": (
                            option.get("text")
                            or option.get("option")
                            or option.get("value")
                        ),
                        "is_correct": option.get("is_correct", False),
                    }
                )

        if (
            normalized_options
            and not any(
                option["is_correct"]
                for option in normalized_options
            )
        ):
            normalized_options[0]["is_correct"] = True

        return normalized_options


# ----- ENTRYPOINT ----- #
async def run_question_pipeline(
    session: AsyncSession,
    book_id: str,
    subject_id: str,
):

    pipeline = QuestionPipeline()

    return await pipeline.run(
        session=session,
        book_id=book_id,
        subject_id=subject_id,
    )