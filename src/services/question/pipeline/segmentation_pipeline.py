# ----- IMPORTS ----- #
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_community.document_loaders import PyMuPDFLoader

from src.core.di.llm import get_llm_service

from src.services.question.utils.utils import chunk_text
from src.services.question.state.state import state
from src.services.question.state.state_transition import update_state

from src.services.question.core.settings import Settings

from src.services.question.models.chapter_model import analyze_chapter
from src.services.question.models.topic_model import analyze_topic
from src.services.question.models.skills_model import extract_skills

from src.domain.education.services.chapter import ChapterService
from src.domain.education.services.topic import TopicService
from src.domain.education.services.skill import SkillService

from src.domain.questions.services.chunk import ChunkService
from src.domain.questions.services.pipeline_job import PipelineJobService


# ----- SETTINGS ----- #
settings = Settings()

# ----- STATE ----- #
state["question_bank"] = []


# ----- MAIN PIPELINE ----- #
async def run_pipeline(
    session: AsyncSession,
    subject_id,
    book_id,
    on_chunk_update=None,
):

    print("\n[PIPELINE] STARTED")

    # ----- SERVICES ----- #
    chapter_service = ChapterService()
    topic_service = TopicService()
    skill_service = SkillService()
    chunk_service = ChunkService()
    job_service = PipelineJobService()

    # ----- LLM ----- #
    llm = await get_llm_service()

    # ----- CONTEXT ----- #
    state["subject_id"] = subject_id
    state["book_id"] = book_id

    # ------------ RESUME OR CREATE JOB ------------ #
    existing_job = await job_service.get_by_subject_and_book(
        session=session,
        subject_id=subject_id,
        book_id=book_id,
    )

    if existing_job:
        job = existing_job
        print(f"[PIPELINE] RESUMING job_id = {job.id}")
    else:
        job = await job_service.create(
            session=session,
            payload={
                "book_id": book_id,
                "subject_id": subject_id,
                "status": "running",
                "current_chunk": 0,
                "total_chunks": 0,
            },
        )
        print(f"[PIPELINE] NEW job_id = {job.id}")

    job_id = job.id
    state["job_id"] = job_id

    # ----- LOAD DOC ----- #
    loader = PyMuPDFLoader(settings.get_file_path())
    docs = loader.load()

    text = "\n".join(d.page_content for d in docs)
    chunks = list(chunk_text(text, settings.CHUNK_SIZE))

    total_chunks = len(chunks)

    # ------------ UPDATE TOTAL CHUNKS ------------ #
    await job_service.update_total_chunks(
        session=session,
        record_id=job_id,
        total_chunks=total_chunks,
    )

    # ------------ RESUME POSITION ------------ #
    start_index = job.current_chunk if job else 0

    print(f"[PIPELINE] start_index = {start_index} / total = {total_chunks}")

    # ------------ LOOP ------------ #
    for i in range(start_index, total_chunks):

        chunk = chunks[i]

        print(f"[CHUNK {i}] START")

        # ----- PROGRESS UPDATE ----- #
        await job_service.update_progress(
            session=session,
            record_id=job_id,
            current_chunk=i,
        )

        # ----- ANALYSIS ----- #
        chapter_pred = await analyze_chapter(llm, chunk, state)
        topic_pred = await analyze_topic(llm, chunk, state)

        update_state(chapter_pred, topic_pred, chunk)

        # ------------ CHAPTER ------------ #
        if state.get("chapter"):
            chapter_id = state.get("chapter_id")

            if not chapter_id:
                existing = await chapter_service.list_by_subject(
                    session=session,
                    subject_id=subject_id,
                )

                match = next(
                    (
                        c for c in existing
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

        # ------------ TOPIC ------------ #
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

        # ------------ SKILLS ------------ #
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

        # ------------ SAVE CHUNK ------------ #
        await chunk_service.create(
            session=session,
            payload={
                "book_id": book_id,
                "subject_id": subject_id,
                "chapter_id": state.get("chapter_id"),
                "topic_id": state.get("topic_id"),
                "chunk_index": i,
                "content": str(chunk),
            },
        )

        if on_chunk_update:
            await on_chunk_update(i, "processed", state)

        print(f"[CHUNK {i}] END")

    # ------------ COMPLETE ------------ #
    await job_service.update_progress(session, job_id, total_chunks)
    await job_service.update_status(session, job_id, "completed")

    print("\n[PIPELINE] COMPLETED")

    return {
        "job_id": job_id,
        "status": "completed",
        "total_chunks": total_chunks,
    }