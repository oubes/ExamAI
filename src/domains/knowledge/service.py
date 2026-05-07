# ---- imports ---- #
import logging

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.knowledge.models import KnowledgeBase


# ---- logging ---- #
logger = logging.getLogger(__name__)


# -------------------- knowledge service -------------------- #
class KnowledgeService:

    # ---- create chunk ---- #
    async def create(
        self,
        session: AsyncSession,
        data: dict,
    ) -> KnowledgeBase:

        try:
            logger.debug(
                f"[KnowledgeService] Creating chunk document_id={data.get('document_id')}"
            )

            record = KnowledgeBase(**data)

            session.add(record)

            await session.commit()
            await session.refresh(record)

            logger.debug(
                f"[KnowledgeService] Created chunk id={record.id}"
            )

            return record

        except Exception as e:
            logger.error(
                f"[KnowledgeService] Failed to create chunk: {str(e)}",
                exc_info=True,
            )
            raise

    # ---- bulk create chunks ---- #
    async def bulk_create(
        self,
        session: AsyncSession,
        records: list[dict],
    ) -> list[KnowledgeBase]:

        try:
            logger.debug(
                f"[KnowledgeService] Bulk creating chunks count={len(records)}"
            )

            instances = [
                KnowledgeBase(**record)
                for record in records
            ]

            session.add_all(instances)

            await session.commit()

            for instance in instances:
                await session.refresh(instance)

            logger.debug(
                f"[KnowledgeService] Bulk created chunks count={len(instances)}"
            )

            return instances

        except Exception as e:
            logger.error(
                f"[KnowledgeService] Failed bulk create: {str(e)}",
                exc_info=True,
            )
            raise

    # ---- get by id ---- #
    async def get_by_id(
        self,
        session: AsyncSession,
        record_id: int,
    ) -> KnowledgeBase | None:

        try:
            logger.debug(
                f"[KnowledgeService] Fetching chunk id={record_id}"
            )

            return await session.get(KnowledgeBase, record_id)

        except Exception as e:
            logger.error(
                f"[KnowledgeService] Failed to fetch chunk: {str(e)}",
                exc_info=True,
            )
            raise

    # ---- list by subject ---- #
    async def list_by_subject(
        self,
        session: AsyncSession,
        subject_id: int,
    ) -> list[KnowledgeBase]:

        try:
            logger.debug(
                f"[KnowledgeService] Listing chunks subject_id={subject_id}"
            )

            result = await session.execute(
                select(KnowledgeBase).where(
                    KnowledgeBase.subject_id == subject_id
                )
            )

            rows = result.scalars().all()

            return list(rows)

        except Exception as e:
            logger.error(
                f"[KnowledgeService] Failed to list chunks: {str(e)}",
                exc_info=True,
            )
            raise

    # ---- list by document ---- #
    async def list_by_document(
        self,
        session: AsyncSession,
        document_id: int,
    ) -> list[KnowledgeBase]:

        try:
            logger.debug(
                f"[KnowledgeService] Listing chunks document_id={document_id}"
            )

            result = await session.execute(
                select(KnowledgeBase).where(
                    KnowledgeBase.document_id == document_id
                )
            )

            rows = result.scalars().all()

            return list(rows)

        except Exception as e:
            logger.error(
                f"[KnowledgeService] Failed to list document chunks: {str(e)}",
                exc_info=True,
            )
            raise

    # ---- update chunk ---- #
    async def update(
        self,
        session: AsyncSession,
        record_id: int,
        updates: dict,
    ) -> KnowledgeBase:

        try:
            logger.debug(
                f"[KnowledgeService] Updating chunk id={record_id}"
            )

            record = await session.get(KnowledgeBase, record_id)

            if not record:
                raise ValueError("Chunk not found")

            for k, v in updates.items():
                setattr(record, k, v)

            await session.commit()
            await session.refresh(record)

            logger.debug(
                f"[KnowledgeService] Updated chunk id={record.id}"
            )

            return record

        except Exception as e:
            logger.error(
                f"[KnowledgeService] Failed to update chunk: {str(e)}",
                exc_info=True,
            )
            raise

    # ---- delete chunk ---- #
    async def delete(
        self,
        session: AsyncSession,
        record: KnowledgeBase,
    ) -> None:

        try:
            logger.debug(
                f"[KnowledgeService] Deleting chunk id={record.id}"
            )

            await session.delete(record)

            await session.commit()

        except Exception as e:
            logger.error(
                f"[KnowledgeService] Failed to delete chunk: {str(e)}",
                exc_info=True,
            )
            raise

    # ---- delete by document ---- #
    async def delete_by_document(
        self,
        session: AsyncSession,
        document_id: int,
    ) -> None:

        try:
            logger.debug(
                f"[KnowledgeService] Deleting document chunks document_id={document_id}"
            )

            await session.execute(
                delete(KnowledgeBase).where(
                    KnowledgeBase.document_id == document_id
                )
            )

            await session.commit()

        except Exception as e:
            logger.error(
                f"[KnowledgeService] Failed deleting document chunks: {str(e)}",
                exc_info=True,
            )
            raise

    # ---- count by subject ---- #
    async def count_by_subject(
        self,
        session: AsyncSession,
        subject_id: int,
    ) -> int:

        try:
            logger.debug(
                f"[KnowledgeService] Counting chunks subject_id={subject_id}"
            )

            result = await session.execute(
                select(KnowledgeBase).where(
                    KnowledgeBase.subject_id == subject_id
                )
            )

            rows = result.scalars().all()

            return len(rows)

        except Exception as e:
            logger.error(
                f"[KnowledgeService] Failed counting chunks: {str(e)}",
                exc_info=True,
            )
            raise