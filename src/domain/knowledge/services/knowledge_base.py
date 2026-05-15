# ---- Imports ---- #
import logging
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.knowledge.models.knowledge_base import KnowledgeBase
from src.domain.education.models.subject import Subject


# ---- Logging ---- #
logger = logging.getLogger(__name__)


# ---- Knowledge Base Service ---- #
class KnowledgeBaseService:

    # ---- Create ---- #
    async def create(
        self,
        session: AsyncSession,
        payload: dict,
    ) -> KnowledgeBase:

        try:
            subject_id = payload["subject_id"]

            subject_stmt = select(Subject.id).where(
                Subject.id == subject_id
            )

            subject_result = await session.execute(subject_stmt)

            if not subject_result.scalar_one_or_none():
                raise ValueError("subject not found")

            record = KnowledgeBase(
                subject_id=subject_id,
                document_id=payload["document_id"],
                chunk_index=int(payload.get("chunk_index", 0)),
                content=str(payload["content"]),
                summary=payload.get("summary"),
                keywords=payload.get("keywords"),
                source_type=str(payload.get("source_type", "text")),
                quality_score=float(
                    payload.get("quality_score", 0.0)
                ),
                importance_score=float(
                    payload.get("importance_score", 0.0)
                ),
                embedding=payload["embedding"],
            )

            session.add(record)

            await session.commit()
            await session.refresh(record)

            return record

        except IntegrityError as e:
            await session.rollback()

            logger.error(
                f"[KnowledgeBaseService] create integrity error: {e}",
                exc_info=True,
            )
            raise

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[KnowledgeBaseService] create error: {e}",
                exc_info=True,
            )
            raise


    # ---- Bulk Create ---- #
    async def bulk_create(
        self,
        session: AsyncSession,
        payloads: list[dict],
    ) -> list[KnowledgeBase]:

        try:
            if not payloads:
                return []

            subject_ids = {p["subject_id"] for p in payloads}

            subject_stmt = select(Subject.id).where(
                Subject.id.in_(subject_ids)
            )

            subject_result = await session.execute(subject_stmt)

            existing_subjects = set(subject_result.scalars().all())

            if subject_ids - existing_subjects:
                raise ValueError("invalid subject_ids")


            records: list[KnowledgeBase] = [
                KnowledgeBase(
                    subject_id=p["subject_id"],
                    document_id=p["document_id"],
                    chunk_index=int(p.get("chunk_index", 0)),
                    content=str(p["content"]),
                    summary=p.get("summary"),
                    keywords=p.get("keywords"),
                    source_type=str(p.get("source_type", "text")),
                    quality_score=float(
                        p.get("quality_score", 0.0)
                    ),
                    importance_score=float(
                        p.get("importance_score", 0.0)
                    ),
                    embedding=p["embedding"],
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
                f"[KnowledgeBaseService] bulk_create error: {e}",
                exc_info=True,
            )
            raise

    # ---- Update Chunk By ID ---- #
    async def update_chunk(
        self,
        session: AsyncSession,
        record_id: UUID,
        payload: dict,
    ) -> int:

        try:
            # ---- Safety: allowed fields only ---- #
            allowed_fields = {
                "content",
                "summary",
                "keywords",
                "source_type",
                "quality_score",
                "importance_score",
            }

            clean_payload = {
                k: v for k, v in payload.items()
                if k in allowed_fields
            }

            if not clean_payload:
                return 0

            stmt = (
                update(KnowledgeBase)
                .where(KnowledgeBase.id == record_id)
                .values(**clean_payload)
                .execution_options(synchronize_session=False)
            )

            result = await session.execute(stmt)
            await session.commit()

            return result.rowcount or 0 # type: ignore

        except Exception as e:
            await session.rollback()

            logger.error(
                f"[KnowledgeBaseService] update_chunk error: {e}",
                exc_info=True,
            )
            raise

    # ---- Exists ---- #
    async def exists(
        self,
        session: AsyncSession,
        record_id: UUID,
    ) -> bool:

        try:
            stmt = select(KnowledgeBase.id).where(
                KnowledgeBase.id == record_id
            )

            result = await session.execute(stmt)

            return result.scalar_one_or_none() is not None

        except Exception as e:
            logger.error(
                f"[KnowledgeBaseService] exists error: {e}",
                exc_info=True,
            )
            raise


    # ---- Get By ID ---- #
    async def get_by_id(
        self,
        session: AsyncSession,
        record_id: UUID,
    ) -> KnowledgeBase | None:

        try:
            stmt = select(KnowledgeBase).where(
                KnowledgeBase.id == record_id
            )

            result = await session.execute(stmt)

            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(
                f"[KnowledgeBaseService] get_by_id error: {e}",
                exc_info=True,
            )
            raise


    # ---- List By Subject ---- #
    async def list_by_subject(
        self,
        session: AsyncSession,
        subject_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[KnowledgeBase]:

        try:
            stmt = (
                select(KnowledgeBase)
                .where(KnowledgeBase.subject_id == subject_id)
                .order_by(KnowledgeBase.chunk_index.asc())
                .limit(limit)
                .offset(offset)
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(
                f"[KnowledgeBaseService] list_by_subject error: {e}",
                exc_info=True,
            )
            raise


    # ---- Search Text ---- #
    async def search_text(
        self,
        session: AsyncSession,
        query: str,
        limit: int = 20,
    ) -> list[KnowledgeBase]:

        try:
            stmt = (
                select(KnowledgeBase)
                .where(KnowledgeBase.content.ilike(f"%{query}%"))
                .limit(limit)
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(
                f"[KnowledgeBaseService] search_text error: {e}",
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
                f"[KnowledgeBaseService] delete error: {e}",
                exc_info=True,
            )
            raise
        
    # ---- List By Subject And Document ---- #
    async def list_by_subject_and_document(
        self,
        session: AsyncSession,
        subject_id: UUID,
        document_id: UUID,
        limit: int = 100,
    ) -> list[KnowledgeBase]:

        try:
            stmt = (
                select(KnowledgeBase)
                .where(
                    KnowledgeBase.subject_id == subject_id,
                    KnowledgeBase.document_id == document_id,
                )
                .order_by(KnowledgeBase.chunk_index.asc())
                .limit(limit)
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(
                f"[KnowledgeBaseService] list_by_subject_and_document error: {e}",
                exc_info=True,
            )
            raise
        
    async def update_by_subject_document_and_chunk(
        self,
        session: AsyncSession,
        subject_id: UUID,
        document_id: UUID,
        chunk_id: UUID,
        payload: dict,
    ) -> int:

        stmt = (
            update(KnowledgeBase)
            .where(
                KnowledgeBase.subject_id == subject_id,
                KnowledgeBase.document_id == document_id,
                KnowledgeBase.document_id == chunk_id,
            )
            .values(**payload)
            .execution_options(synchronize_session=False)
        )

        result = await session.execute(stmt)
        await session.commit()

        return result.rowcount or 0 # type: ignore