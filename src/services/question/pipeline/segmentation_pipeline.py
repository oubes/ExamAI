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

from src.domain.storage.services.upload_file import UploadService

from src.domain.questions.services.chunk import ChunkService
from pathlib import Path


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
    upload_service = UploadService()

    # ----- LLM ----- #
    llm = await get_llm_service()

    # ----- CONTEXT ----- #
    state["subject_id"] = subject_id
    state["book_id"] = book_id

    # ----- LOAD FILE ----- #
    file_record = await upload_service.get_by_id(
        session=session,
        file_id=book_id,
    )

    file_path = Path(file_record.path)
    print(f"[PIPELINE] Loading file from {file_path}")

    loader = PyMuPDFLoader(str(file_path))
    docs = loader.load()

    text = "\n".join(d.page_content for d in docs)
    chunks = list(chunk_text(text, settings.CHUNK_SIZE))

    total_chunks = len(chunks)

    print(f"[PIPELINE] total_chunks = {total_chunks}")

    # ----- EXISTING CHUNKS ----- #
    existing_rows = await chunk_service.list_by_filters(
        session=session,
        subject_id=subject_id,
        book_id=book_id,
    )

    existing_indexes = {row.chunk_index for row in existing_rows}

    # ----- LOOP ----- #
    processed = 0
    skipped = 0

    for chunk_index, chunk in enumerate(chunks):

        print(f"[CHUNK {chunk_index}] START")

        # ----- CHECK EXISTENCE (TRUE SOURCE) ----- #
        if chunk_index in existing_indexes:
            skipped += 1
            print(f"[SKIP] chunk_index={chunk_index}/{total_chunks}")
            continue

        # ----- ANALYSIS ----- #
        chapter_pred = await analyze_chapter(llm, chunk, state)
        topic_pred = await analyze_topic(llm, chunk, state)

        update_state(chapter_pred, topic_pred, chunk)

        # ----- CHAPTER ----- #
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

        # ----- TOPIC ----- #
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

        # ----- SKILLS ----- #
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

        # ----- SAVE CHUNK ----- #
        await chunk_service.create(
            session=session,
            payload={
                "book_id": book_id,
                "subject_id": subject_id,
                "chapter_id": state.get("chapter_id"),
                "topic_id": state.get("topic_id"),
                "chunk_index": chunk_index,
                "content": str(chunk),
            },
        )

        processed += 1

        if on_chunk_update:
            await on_chunk_update(chunk_index, "processed", state)

        print(f"[CHUNK {chunk_index}] END")

    print("\n[PIPELINE] COMPLETED")

    return {
        "status": "completed",
        "total_chunks": total_chunks,
        "processed": processed,
        "skipped": skipped,
    }