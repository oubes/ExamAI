# ---- Imports ---- #
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func

from src.domain.knowledge.models.knowledge_base import KnowledgeBase


# ---- logging ---- #
logger = logging.getLogger(__name__)


# ---- Knowledge Base Service ---- #
class KnowledgeBaseService:

    # ---- Create Chunk ---- #
    async def create(
        self,
        session: AsyncSession,
        data: dict,
    ) -> KnowledgeBase:

        try:
            logger.debug(f"[KnowledgeBase] create: subject_id={data.get('subject_id')}")

            record = KnowledgeBase(**data)

            session.add(record)
            await session.commit()
            await session.refresh(record)

            return record

        except Exception as e:
            logger.error(f"[KnowledgeBase] create error: {e}", exc_info=True)
            raise


    # ---- Get By ID ---- #
    async def get_by_id(
        self,
        session: AsyncSession,
        kb_id: int,
    ) -> KnowledgeBase | None:

        try:
            return await session.get(KnowledgeBase, kb_id)

        except Exception as e:
            logger.error(f"[KnowledgeBase] get_by_id error: {e}", exc_info=True)
            raise


    # ---- Get By Document ---- #
    async def get_by_document(
        self,
        session: AsyncSession,
        document_id: int,
    ) -> list[KnowledgeBase]:

        try:
            stmt = select(KnowledgeBase).where(
                KnowledgeBase.document_id == document_id
            )

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"[KnowledgeBase] get_by_document error: {e}", exc_info=True)
            raise


    # ---- Get By Subject ---- #
    async def get_by_subject(
        self,
        session: AsyncSession,
        subject_id: int,
        limit: int = 50,
        offset: int = 0,
    ) -> list[KnowledgeBase]:

        try:
            stmt = select(KnowledgeBase).where(
                KnowledgeBase.subject_id == subject_id
            ).order_by(
                KnowledgeBase.quality_score.desc(),
                KnowledgeBase.importance_score.desc()
            ).offset(offset).limit(limit)

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"[KnowledgeBase] get_by_subject error: {e}", exc_info=True)
            raise


    # ---- Update Chunk ---- #
    async def update(
        self,
        session: AsyncSession,
        kb_id: int,
        updates: dict,
    ) -> KnowledgeBase:

        try:
            record = await session.get(KnowledgeBase, kb_id)

            if not record:
                raise ValueError("knowledge base record not found")

            protected = {"id", "document_id"}

            for k, v in updates.items():
                if k in protected:
                    continue
                setattr(record, k, v)

            await session.commit()
            await session.refresh(record)

            return record

        except Exception as e:
            logger.error(f"[KnowledgeBase] update error: {e}", exc_info=True)
            raise


    # ---- Delete Chunk ---- #
    async def delete(
        self,
        session: AsyncSession,
        kb_id: int,
    ) -> bool:

        try:
            record = await session.get(KnowledgeBase, kb_id)

            if not record:
                return False

            await session.delete(record)
            await session.commit()

            return True

        except Exception as e:
            logger.error(f"[KnowledgeBase] delete error: {e}", exc_info=True)
            raise


    # ---- Delete By Document ---- #
    async def delete_by_document(
        self,
        session: AsyncSession,
        document_id: int,
    ) -> int:

        try:
            stmt = select(KnowledgeBase).where(
                KnowledgeBase.document_id == document_id
            )

            result = await session.execute(stmt)
            records = result.scalars().all()

            count = len(records)

            for r in records:
                await session.delete(r)

            await session.commit()

            return count

        except Exception as e:
            logger.error(f"[KnowledgeBase] delete_by_document error: {e}", exc_info=True)
            raise


    # ---- Full Text Search ---- #
    async def search_text(
        self,
        session: AsyncSession,
        query: str,
        subject_id: int | None = None,
        limit: int = 20,
    ) -> list[KnowledgeBase]:

        try:
            stmt = select(KnowledgeBase).where(
                KnowledgeBase.search_vector.match(query)
            )

            if subject_id:
                stmt = stmt.where(KnowledgeBase.subject_id == subject_id)

            stmt = stmt.limit(limit)

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"[KnowledgeBase] search_text error: {e}", exc_info=True)
            raise


    # ---- Semantic Search (Vector) ---- #
    async def search_vector(
        self,
        session: AsyncSession,
        embedding: list[float],
        subject_id: int | None = None,
        limit: int = 10,
    ) -> list[KnowledgeBase]:

        try:
            stmt = select(KnowledgeBase)

            if subject_id:
                stmt = stmt.where(KnowledgeBase.subject_id == subject_id)

            # cosine distance
            stmt = stmt.order_by(
                KnowledgeBase.embedding.cosine_distance(embedding)
            ).limit(limit)

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"[KnowledgeBase] search_vector error: {e}", exc_info=True)
            raise


    # ---- Hybrid Search (Text + Vector Ranking) ---- #
    async def hybrid_search(
        self,
        session: AsyncSession,
        query: str,
        embedding: list[float],
        subject_id: int | None = None,
        limit: int = 10,
    ) -> list[KnowledgeBase]:

        try:
            stmt = select(KnowledgeBase)

            if subject_id:
                stmt = stmt.where(KnowledgeBase.subject_id == subject_id)

            stmt = stmt.where(
                or_(
                    KnowledgeBase.search_vector.match(query),
                    KnowledgeBase.embedding.cosine_distance(embedding) < 0.3
                )
            )

            stmt = stmt.order_by(
                KnowledgeBase.importance_score.desc(),
                KnowledgeBase.quality_score.desc(),
            ).limit(limit)

            result = await session.execute(stmt)

            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"[KnowledgeBase] hybrid_search error: {e}", exc_info=True)
            raise


    # ---- Stats ---- #
    async def stats(
        self,
        session: AsyncSession,
        subject_id: int,
    ) -> dict:

        try:
            total = await session.execute(
                select(func.count()).where(
                    KnowledgeBase.subject_id == subject_id
                )
            )

            avg_quality = await session.execute(
                select(func.avg(KnowledgeBase.quality_score)).where(
                    KnowledgeBase.subject_id == subject_id
                )
            )

            avg_importance = await session.execute(
                select(func.avg(KnowledgeBase.importance_score)).where(
                    KnowledgeBase.subject_id == subject_id
                )
            )

            return {
                "total": total.scalar(),
                "avg_quality": float(avg_quality.scalar() or 0),
                "avg_importance": float(avg_importance.scalar() or 0),
            }

        except Exception as e:
            logger.error(f"[KnowledgeBase] stats error: {e}", exc_info=True)
            raise