# ----- IMPORTS ----- #
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


# ----- SETTINGS ----- #
settings = Settings()

DIFFICULTY_MAP = {"easy": 1, "medium": 2, "hard": 3}


# ----- MAIN QUESTION PIPELINE ----- #
async def run_question_pipeline(
    session: AsyncSession,
    segmentation_results: list,
    subject_id,
):

    print("\n[QUESTION PIPELINE] STARTED")

    llm = await get_llm_service()

    question_service = QuestionService()
    option_service = QuestionOptionService()
    model_answer_service = ModelAnswerService()
    question_skill_service = QuestionSkillService()

    for block in segmentation_results:

        chapter_id = block["chapter_id"]
        topic_id = block["topic_id"]
        skills = block["skills"]

        # You will fetch real topic summary from DB in production
        topic_summary = ""

        # ================= MCQ ================= #
        for difficulty in settings.DIFFICULTY_LEVELS:

            mcq_resp = await generate_mcq(
                llm,
                "topic_placeholder",
                topic_summary,
                difficulty,
            )

            for q in mcq_resp.get("questions", []):

                q = normalize_mcq(q)

                question = await question_service.create(
                    session=session,
                    payload={
                        "subject_id": subject_id,
                        "chapter_id": chapter_id,
                        "topic_id": topic_id,
                        "content": q.get("question") or q.get("content"),
                        "explanation": q.get("explanation"),
                        "type": "mcq",
                        "difficulty": DIFFICULTY_MAP[difficulty],
                        "importance": q.get("importance", 1),
                        "tags": ",".join(q.get("tags", [])) if isinstance(q.get("tags"), list) else q.get("tags"),
                        "embedding": q.get("embedding", []),
                    },
                )

                # OPTIONS (FIXED ISOLATION ISSUE)
                for idx, opt in enumerate(q.get("options", [])):
                    await option_service.create(
                        session=session,
                        payload={
                            "question_id": question.id,
                            "option_text": opt.get("text"),
                            "is_correct": opt.get("is_correct", False),
                            "order": idx,
                        },
                    )

                for skill in skills:
                    await question_skill_service.create(
                        session=session,
                        payload={
                            "question_id": question.id,
                            "skill_id": skill,
                            "weight": 1.0,
                        },
                    )

        # ================= WRITTEN ================= #
        for difficulty in settings.DIFFICULTY_LEVELS:

            written_resp = await generate_written(
                llm,
                "topic_placeholder",
                topic_summary,
                difficulty,
            )

            for q in written_resp.get("questions", []):

                question = await question_service.create(
                    session=session,
                    payload={
                        "subject_id": subject_id,
                        "chapter_id": chapter_id,
                        "topic_id": topic_id,
                        "content": q.get("question") or q.get("content"),
                        "explanation": q.get("explanation"),
                        "type": "written",
                        "difficulty": DIFFICULTY_MAP[difficulty],
                        "importance": q.get("importance", 1),
                        "tags": ",".join(q.get("tags", [])) if isinstance(q.get("tags"), list) else q.get("tags"),
                        "embedding": q.get("embedding", []),
                    },
                )

                if q.get("answer"):
                    await model_answer_service.create(
                        session=session,
                        payload={
                            "question_id": question.id,
                            "answer_text": q["answer"],
                        },
                    )

                for skill in skills:
                    await question_skill_service.create(
                        session=session,
                        payload={
                            "question_id": question.id,
                            "skill_id": skill,
                            "weight": 1.0,
                        },
                    )

    print("\n[QUESTION PIPELINE] COMPLETED")

    return {
        "status": "completed",
        "blocks": len(segmentation_results),
    }