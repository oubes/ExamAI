# ----- IMPORTS ----- #
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_community.document_loaders import PyMuPDFLoader

from src.core.di.llm import get_llm_service

from src.services.question.utils.utils import chunk_text, normalize_mcq
from src.services.question.state.state import state
from src.services.question.state.state_transition import update_state

from src.services.question.core.settings import Settings

from src.services.question.models.chapter_model import analyze_chapter
from src.services.question.models.topic_model import analyze_topic
from src.services.question.models.skills_model import extract_skills
from src.services.question.models.mcq_model import generate_mcq
from src.services.question.models.written_model import generate_written

from src.domain.education.services.chapter import ChapterService
from src.domain.education.services.topic import TopicService
from src.domain.education.services.skill import SkillService

from src.domain.questions.services.question import QuestionService
from src.domain.questions.services.option import QuestionOptionService
from src.domain.questions.services.model_answer import ModelAnswerService
from src.domain.questions.services.question_skill import QuestionSkillService


# ----- SETTINGS ----- #
settings = Settings()

# ----- INIT STATE ----- #
state["question_bank"] = []

# ----- DIFFICULTY MAP ----- #
DIFFICULTY_MAP = {
    "easy": 1,
    "medium": 2,
    "hard": 3,
}

# ----- MAIN PIPELINE ----- #
async def run_pipeline(
    session: AsyncSession,
    subject_id,
    on_chunk_update=None,
):

    print("\n[PIPELINE] STARTED")
    print(f"[PIPELINE] subject_id = {subject_id}")

    # ----- SERVICES ----- #
    chapter_service = ChapterService()
    topic_service = TopicService()
    skill_service = SkillService()

    question_service = QuestionService()
    option_service = QuestionOptionService()
    model_answer_service = ModelAnswerService()
    question_skill_service = QuestionSkillService()

    # ----- LLM ----- #
    llm = await get_llm_service()
    print("[PIPELINE] LLM initialized")

    # ----- CONTEXT ----- #
    state["subject_id"] = subject_id

    # ----- LOAD DOC ----- #
    print("[PIPELINE] Loading document...")
    loader = PyMuPDFLoader(settings.get_file_path())
    docs = loader.load()

    text = "\n".join(d.page_content for d in docs)
    chunks = list(chunk_text(text, settings.CHUNK_SIZE))

    print(f"[PIPELINE] Total chunks = {len(chunks)}")

    # ----- LOOP ----- #
    for i, chunk in enumerate(chunks):

        print("\n" + "-" * 60)
        print(f"[CHUNK {i}] START")

        # ----- ANALYSIS ----- #
        chapter_pred = await analyze_chapter(llm, chunk, state)
        topic_pred = await analyze_topic(llm, chunk, state)

        update_state(chapter_pred, topic_pred, chunk)

        print(f"[CHUNK {i}] chapter = {state.get('chapter')}")
        print(f"[CHUNK {i}] topic = {state.get('topic')}")

        # ================= CHAPTER ================= #
        if state.get("chapter"):

            chapter_id = state.get("chapter_id")

            if not chapter_id:

                existing_chapters = await chapter_service.list_by_subject(
                    session=session,
                    subject_id=subject_id,
                )

                match = next(
                    (
                        c for c in existing_chapters
                        if c.title.lower() == str(state["chapter"]).lower()
                    ),
                    None,
                )

                if match:
                    chapter_id = match.id
                else:
                    chapter = await chapter_service.create(
                        session=session,
                        data={
                            "subject_id": subject_id,
                            "title": state["chapter"],
                            "description": state.get("chapter_summary"),
                            "order_index": 0,
                        },
                    )
                    chapter_id = chapter.id

            state["chapter_id"] = chapter_id
            print(f"[CHUNK {i}] chapter_id = {chapter_id}")

        # ================= TOPIC ================= #
        if state.get("topic") and state.get("chapter_id"):

            topic_id = state.get("topic_id")

            if not topic_id:

                topic = await topic_service.create(
                    session=session,
                    payload={
                        "subject_id": subject_id,
                        "chapter_id": state["chapter_id"],
                        "title": state["topic"],
                        "description": state.get("topic_summary"),
                        "difficulty_weight": 1.0,
                    },
                )

                topic_id = topic.id

            state["topic_id"] = topic_id
            print(f"[CHUNK {i}] topic_id = {topic_id}")

        # ================= SKILLS ================= #
        if state.get("topic") and state.get("topic_id") and not state.get("skills"):

            skills_resp = await extract_skills(
                llm,
                state["topic"],
                state["topic_summary"],
            )

            skills = skills_resp.get("skills", [])
            state["skills"] = skills

            persisted_skills = []

            for name in skills:
                skill = await skill_service.create(
                    session=session,
                    payload={
                        "subject_id": subject_id,
                        "chapter_id": state["chapter_id"],
                        "topic_id": state["topic_id"],
                        "name": name,
                        "description": None,
                        "importance_weight": 1.0,
                    },
                )

                persisted_skills.append(skill)

            state["persisted_skills"] = persisted_skills
            print(f"[CHUNK {i}] skills = {len(persisted_skills)}")

        # ----- TOPIC READY ----- #
        topic_ready = state.get("topic") and len(state.get("topic_summary", "").split()) > 200

        print(f"[CHUNK {i}] topic_ready = {topic_ready}")

        if not topic_ready:
            if on_chunk_update:
                await on_chunk_update(i, "skipped", state)
            continue

        # ================= MCQ ================= #
        all_mcq = []

        for difficulty in settings.DIFFICULTY_LEVELS:

            mcq_resp = await generate_mcq(
                llm,
                state["topic"],
                state["topic_summary"],
                difficulty,
            )

            mcq_questions = [
                normalize_mcq(q)
                for q in mcq_resp.get("questions", [])
            ]

            for q in mcq_questions:
                q["difficulty"] = DIFFICULTY_MAP.get(difficulty, 1)

            all_mcq.extend(mcq_questions)

        state["question_bank"].extend(all_mcq)

        # ----- PERSIST MCQ ----- #
        for q in all_mcq:

            question = await question_service.create(
                session=session,
                payload={
                    "subject_id": subject_id,
                    "chapter_id": state["chapter_id"],
                    "topic_id": state["topic_id"],
                    "content": q.get("question") or q.get("content"),
                    "explanation": q.get("explanation"),
                    "type": "mcq",
                    "difficulty": q.get("difficulty", 1),
                    "importance": q.get("importance", 1),
                    "tags": ",".join(q.get("tags", [])) if isinstance(q.get("tags"), list) else q.get("tags"),
                    "embedding": q.get("embedding", []),
                },
            )

            # ---------------- MCQ OPTIONS ONLY ---------------- #
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

            # ---------------- SKILLS LINK ---------------- #
            for skill in state.get("persisted_skills", []):
                await question_skill_service.create(
                    session=session,
                    payload={
                        "question_id": question.id,
                        "skill_id": skill.id,
                        "weight": 1.0,
                    },
                )

        if on_chunk_update:
            await on_chunk_update(i, "mcq", state)

        # ================= WRITTEN ================= #
        all_written = []

        for difficulty in settings.DIFFICULTY_LEVELS:

            written_resp = await generate_written(
                llm,
                state["topic"],
                state["topic_summary"],
                difficulty,
            )

            written_questions = written_resp.get("questions", [])

            for q in written_questions:
                q["difficulty"] = DIFFICULTY_MAP.get(difficulty, 1)

            all_written.extend(written_questions)

        state["question_bank"].extend(all_written)

        # ----- PERSIST WRITTEN ----- #
        for q in all_written:

            question = await question_service.create(
                session=session,
                payload={
                    "subject_id": subject_id,
                    "chapter_id": state["chapter_id"],
                    "topic_id": state["topic_id"],
                    "content": q.get("question") or q.get("content"),
                    "explanation": q.get("explanation"),
                    "type": "written",
                    "difficulty": q.get("difficulty", 1),
                    "importance": q.get("importance", 1),
                    "tags": ",".join(q.get("tags", [])) if isinstance(q.get("tags"), list) else q.get("tags"),
                    "embedding": q.get("embedding", []),
                },
            )

            # ---------------- MODEL ANSWER ONLY FOR WRITTEN ---------------- #
            if q.get("answer"):
                await model_answer_service.create(
                    session=session,
                    payload={
                        "question_id": question.id,
                        "answer_text": q["answer"],
                    },
                )

            # ---------------- SKILLS LINK ---------------- #
            for skill in state.get("persisted_skills", []):
                await question_skill_service.create(
                    session=session,
                    payload={
                        "question_id": question.id,
                        "skill_id": skill.id,
                        "weight": 1.0,
                    },
                )

        if on_chunk_update:
            await on_chunk_update(i, "written", state)

        print(f"[CHUNK {i}] END")

    print("\n[PIPELINE] COMPLETED")

    return {
        "status": "completed",
        "total_chunks": len(chunks),
        "total_questions": len(state["question_bank"]),
        "chapter": state.get("chapter"),
        "topic": state.get("topic"),
        "skills": state.get("skills", []),
    }