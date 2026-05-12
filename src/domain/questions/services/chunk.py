# ---- Imports ---- #
import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.education.models.subject import Subject
from src.domain.education.models.chapter import Chapter
from src.domain.education.models.topic import Topic
from src.domain.questions.models.chunk import DocumentChunk


# ---- Logging ---- #
logger = logging.getLogger(__name__)


# ---- Chunk Service ---- #
class ChunkService:

    # ---- Create ---- #
    async def create(
        self,
        session: AsyncSession,
        payload: dict,
    ) -> DocumentChunk:

        try:
            subject_id = payload["subject_id"]
            book_id = payload["book_id"]
            chapter_id = payload.get("chapter_id")
            topic_id = payload.get("topic_id")

            # ---------- VALIDATION QUERIES ---------- #
            subject_stmt = select(Subject.id).where(Subject.id == subject_id)
            subject_result = await session.execute(subject_stmt)

            if not subject_result.scalar_one_or_none():
                raise ValueError("subject not found")

            # ---------- CHAPTER CHECK ---------- #
            if chapter_id is not None:
                chapter_stmt = select(Chapter.id).where(Chapter.id == chapter_id)
                chapter_result = await session.execute(chapter_stmt)

                if not chapter_result.scalar_one_or_none():
                    raise ValueError("chapter not found")

            # ---------- TOPIC CHECK ---------- #
            if topic_id is not None:
                topic_stmt = select(Topic.id).where(Topic.id == topic_id)
                topic_result = await session.execute(topic_stmt)

                if not topic_result.scalar_one_or_none():
                    raise ValueError("topic not found")

            # ---------- INSERT ---------- #
            record = DocumentChunk(
                book_id=book_id,
                subject_id=subject_id,
                chapter_id=chapter_id,
                topic_id=topic_id,
                chunk_index=int(payload["chunk_index"]),
                content=str(payload["content"]),
            )

            session.add(record)
            await session.commit()
            await session.refresh(record)

            return record

        except IntegrityError as e:
            await session.rollback()

            logger.error(
                f"[ChunkService] create integrity error: {e}",
                exc_info=True,
            )
            raise

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[ChunkService] create error: {e}",
                exc_info=True,
            )
            raise


    # ---- Bulk Create ---- #
    async def bulk_create(
        self,
        session: AsyncSession,
        payloads: list[dict],
    ) -> list[DocumentChunk]:

        try:
            if not payloads:
                return []

            subject_ids = {p["subject_id"] for p in payloads}
            book_ids = {p["book_id"] for p in payloads}
            chapter_ids = {p.get("chapter_id") for p in payloads if p.get("chapter_id")}
            topic_ids = {p.get("topic_id") for p in payloads if p.get("topic_id")}

            # ---------- SUBJECT CHECK ---------- #
            subject_stmt = select(Subject.id).where(Subject.id.in_(subject_ids))
            subject_result = await session.execute(subject_stmt)

            if subject_ids - set(subject_result.scalars().all()):
                raise ValueError("invalid subject_ids")

            # ---------- BOOK CHECK (no FK table, assumed valid upload) ---------- #

            # ---------- CHAPTER CHECK ---------- #
            if chapter_ids:
                chapter_stmt = select(Chapter.id).where(Chapter.id.in_(chapter_ids))
                chapter_result = await session.execute(chapter_stmt)

                if chapter_ids - set(chapter_result.scalars().all()):
                    raise ValueError("invalid chapter_ids")

            # ---------- TOPIC CHECK ---------- #
            if topic_ids:
                topic_stmt = select(Topic.id).where(Topic.id.in_(topic_ids))
                topic_result = await session.execute(topic_stmt)

                if topic_ids - set(topic_result.scalars().all()):
                    raise ValueError("invalid topic_ids")

            # ---------- INSERT ---------- #
            records: list[DocumentChunk] = [
                DocumentChunk(
                    book_id=p["book_id"],
                    subject_id=p["subject_id"],
                    chapter_id=p.get("chapter_id"),
                    topic_id=p.get("topic_id"),
                    chunk_index=int(p["chunk_index"]),
                    content=str(p["content"]),
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
                f"[ChunkService] bulk_create error: {e}",
                exc_info=True,
            )
            raise


    # ---- Get By ID ---- #
    async def get_by_id(
        self,
        session: AsyncSession,
        record_id: UUID,
    ) -> DocumentChunk | None:

        try:
            stmt = select(DocumentChunk).where(
                DocumentChunk.id == record_id
            )

            result = await session.execute(stmt)
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(
                f"[ChunkService] get_by_id error: {e}",
                exc_info=True,
            )
            raise


    # ---- List By Filters ---- #
    async def list_by_filters(
        self,
        session: AsyncSession,
        subject_id: UUID | None = None,
        book_id: UUID | None = None,
        chapter_id: UUID | None = None,
        topic_id: UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[DocumentChunk]:

        try:
            stmt = select(DocumentChunk)

            if subject_id is not None:
                stmt = stmt.where(DocumentChunk.subject_id == subject_id)

            if book_id is not None:
                stmt = stmt.where(DocumentChunk.book_id == book_id)

            if chapter_id is not None:
                stmt = stmt.where(DocumentChunk.chapter_id == chapter_id)

            if topic_id is not None:
                stmt = stmt.where(DocumentChunk.topic_id == topic_id)

            stmt = stmt.limit(limit).offset(offset)

            result = await session.execute(stmt)
            return list(result.scalars().all())

        except Exception as e:
            logger.error(
                f"[ChunkService] list_by_filters error: {e}",
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

            if record is None:
                return False

            await session.delete(record)
            await session.commit()

            return True

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[ChunkService] delete error: {e}",
                exc_info=True,
            )
            raise