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
from src.domain.questions.services.chunk import ChunkService

from uuid import UUID


# ----- SETTINGS ----- #
settings = Settings()
DIFFICULTY_MAP = {"easy": 1, "medium": 2, "hard": 3}


# ----- MAIN PIPELINE ----- #
async def run_question_pipeline(
    session: AsyncSession,
    book_id: str,
    subject_id: str,
):

    print("\n================ PIPELINE START ================\n")

    llm = await get_llm_service()

    question_service = QuestionService()
    option_service = QuestionOptionService()
    model_answer_service = ModelAnswerService()
    question_skill_service = QuestionSkillService()
    chunk_service = ChunkService()

    # ---------- FETCH CHUNKS ---------- #
    print("[STEP] fetching chunks...")

    chunks = await chunk_service.list_by_filters(
        session=session,
        subject_id=UUID(subject_id),
        book_id=UUID(book_id),
    )

    print(f"[STEP] chunks loaded = {len(chunks)}")

    if not chunks:
        print("[PIPELINE] EMPTY CHUNKS")
        return {"status": "empty"}

    # ---------- MAIN LOOP ---------- #
    for i, chunk in enumerate(chunks):

        print("\n--------------------------------------------------")
        print(f"[CHUNK {i}] START")
        print(f"chapter_id = {chunk.chapter_id}")
        print(f"topic_id   = {chunk.topic_id}")

        topic_text = chunk.content
        topic_summary = topic_text[:1000]

        skills = getattr(chunk, "skills", []) or []

        print(f"[CHUNK {i}] skills = {skills}")

        # ================= MCQ ================= #
        for difficulty in settings.DIFFICULTY_LEVELS:

            print(f"\n[MCQ] difficulty = {difficulty}")

            mcq_resp = await generate_mcq(
                llm,
                topic_text,
                topic_summary,
                difficulty,
            )

            print(f"[MCQ] keys = {mcq_resp.keys()}")

            questions = mcq_resp.get("questions", [])
            print(f"[MCQ] questions count = {len(questions)}")

            for q_idx, q in enumerate(questions):

                q = normalize_mcq(q)

                print(f"\n[MCQ] Q{q_idx}")
                print(q)

                question = await question_service.create(
                    session=session,
                    payload={
                        "subject_id": subject_id,
                        "chapter_id": chunk.chapter_id,
                        "topic_id": chunk.topic_id,
                        "content": q.get("question") or q.get("content"),
                        "explanation": q.get("explanation"),
                        "type": "mcq",
                        "difficulty": DIFFICULTY_MAP[difficulty],
                        "importance": q.get("importance", 1),
                        "tags": ",".join(q.get("tags", []))
                        if isinstance(q.get("tags"), list)
                        else q.get("tags"),
                        "embedding": q.get("embedding", []),
                    },
                )

                print(f"[MCQ] STORED QUESTION -> id={question.id}")

                # ---------- OPTIONS ---------- #
                options = q.get("options")

                if options is None:
                    choices = q.get("choices", [])

                    if isinstance(choices, dict):
                        options = [{"text": v, "is_correct": False} for v in choices.values()]
                    else:
                        options = [{"text": c, "is_correct": False} for c in choices]

                normalized_options = []

                for opt in options:

                    if isinstance(opt, str):
                        normalized_options.append({
                            "text": opt,
                            "is_correct": False
                        })

                    elif isinstance(opt, dict):
                        normalized_options.append({
                            "text": opt.get("text") or opt.get("option") or opt.get("value"),
                            "is_correct": opt.get("is_correct", False)
                        })

                if not any(o["is_correct"] for o in normalized_options) and normalized_options:
                    normalized_options[0]["is_correct"] = True

                print(f"[MCQ] options count = {len(normalized_options)}")

                for idx, opt in enumerate(normalized_options):

                    option_text = opt.get("text")

                    if option_text:
                        option = await option_service.create(
                            session=session,
                            payload={
                                "question_id": question.id,
                                "option_text": option_text,
                                "is_correct": opt.get("is_correct", False),
                                "order": idx,
                            },
                        )

                        print(
                            f"[MCQ] STORED OPTION -> id={option.id} | question_id={question.id}"
                        )

                # ---------- SKILLS ---------- #
                print(f"[MCQ] linking skills...")

                for skill_id in skills:

                    link = await question_skill_service.create(
                        session=session,
                        payload={
                            "question_id": question.id,
                            "skill_id": skill_id,
                            "weight": 1.0,
                        },
                    )

                    print(
                        f"[MCQ] STORED SKILL LINK -> id={link.id} | question_id={question.id} | skill_id={skill_id}"
                    )

        # ================= WRITTEN ================= #
        for difficulty in settings.DIFFICULTY_LEVELS:

            print(f"\n[WRITTEN] difficulty = {difficulty}")

            written_resp = await generate_written(
                llm,
                topic_text,
                topic_summary,
                difficulty,
            )

            print(f"[WRITTEN] keys = {written_resp.keys()}")

            questions = written_resp.get("questions", [])
            print(f"[WRITTEN] count = {len(questions)}")

            for q_idx, q in enumerate(questions):

                print(f"\n[WRITTEN] Q{q_idx}")
                print(q)

                question = await question_service.create(
                    session=session,
                    payload={
                        "subject_id": subject_id,
                        "chapter_id": chunk.chapter_id,
                        "topic_id": chunk.topic_id,
                        "content": q.get("question") or q.get("content"),
                        "explanation": q.get("explanation"),
                        "type": "written",
                        "difficulty": DIFFICULTY_MAP[difficulty],
                        "importance": q.get("importance", 1),
                        "tags": ",".join(q.get("tags", []))
                        if isinstance(q.get("tags"), list)
                        else q.get("tags"),
                        "embedding": q.get("embedding", []),
                    },
                )

                print(f"[WRITTEN] STORED QUESTION -> id={question.id}")

                # ---------- MODEL ANSWER ---------- #
                answer = q.get("answer")

                if answer:
                    ans = await model_answer_service.create(
                        session=session,
                        payload={
                            "question_id": question.id,
                            "answer_text": answer,
                        },
                    )

                    print(
                        f"[WRITTEN] STORED MODEL ANSWER -> id={ans.id} | question_id={question.id}"
                    )

                # ---------- SKILLS ---------- #
                print(f"[WRITTEN] linking skills...")

                for skill_id in skills:

                    link = await question_skill_service.create(
                        session=session,
                        payload={
                            "question_id": question.id,
                            "skill_id": skill_id,
                            "weight": 1.0,
                        },
                    )

                    print(
                        f"[WRITTEN] STORED SKILL LINK -> id={link.id} | question_id={question.id} | skill_id={skill_id}"
                    )

        print(f"\n[CHUNK {i}] END")

    # ---------- COMMIT ---------- #
    print("\n[STEP] committing session...")

    await session.commit()

    print("\n================ PIPELINE DONE ================\n")

    return {
        "status": "completed",
        "chunks": len(chunks),
    }