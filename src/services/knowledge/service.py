# ---- Imports ---- #
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.di.embedder import get_embedding_service
from src.core.di.llm import get_llm_service
from src.domain.knowledge.models.knowledge_base import KnowledgeBase
from src.domain.knowledge.services.knowledge_base import (
    KnowledgeBaseService,
)
from src.services.knowledge.models.summarizer import generate_summary


# ---- Service ---- #
knowledge_base_service = KnowledgeBaseService()


# ---- Knowledge Base Manager ---- #
class KnowledgeBaseManager:

    # ---- Create ---- #
    async def create_chunk(
        self,
        session: AsyncSession,
        payload: dict,
    ) -> KnowledgeBase:

        return await knowledge_base_service.create(
            session=session,
            payload=payload,
        )

    # ---- Bulk Create ---- #
    async def bulk_create_chunks(
        self,
        session: AsyncSession,
        payloads: list[dict],
    ) -> list[KnowledgeBase]:

        return await knowledge_base_service.bulk_create(
            session=session,
            payloads=payloads,
        )

    # ---- Get By ID ---- #
    async def get_chunk(
        self,
        session: AsyncSession,
        record_id: UUID,
    ) -> KnowledgeBase | None:

        return await knowledge_base_service.get_by_id(
            session=session,
            record_id=record_id,
        )

    # ---- Exists ---- #
    async def chunk_exists(
        self,
        session: AsyncSession,
        record_id: UUID,
    ) -> bool:

        return await knowledge_base_service.exists(
            session=session,
            record_id=record_id,
        )

    # ---- List By Subject ---- #
    async def list_subject_chunks(
        self,
        session: AsyncSession,
        subject_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[KnowledgeBase]:

        return await knowledge_base_service.list_by_subject(
            session=session,
            subject_id=subject_id,
            limit=limit,
            offset=offset,
        )

    # ---- List By Subject And Document ---- #
    async def list_document_chunks(
        self,
        session: AsyncSession,
        subject_id: UUID,
        document_id: UUID,
        limit: int = 100,
    ) -> list[KnowledgeBase]:

        return await knowledge_base_service.list_by_subject_and_document(
            session=session,
            subject_id=subject_id,
            document_id=document_id,
            limit=limit,
        )

    # ---- List Chunks By Subject And Document ---- #
    async def list_chunks_by_subject_and_document(
        self,
        session: AsyncSession,
        subject_id: UUID,
        document_id: UUID,
    ) -> list[KnowledgeBase]:

        return await knowledge_base_service.list_by_subject_and_document(
            session=session,
            subject_id=subject_id,
            document_id=document_id,
        )

    # ---- Search ---- #
    async def search_chunks(
        self,
        session: AsyncSession,
        query: str,
        limit: int = 20,
    ) -> list[KnowledgeBase]:

        return await knowledge_base_service.search_text(
            session=session,
            query=query,
            limit=limit,
        )

    # ---- Delete ---- #
    async def delete_chunk(
        self,
        session: AsyncSession,
        record_id: UUID,
    ) -> bool:

        return await knowledge_base_service.delete(
            session=session,
            record_id=record_id,
        )

    # ---- Get Existing Chunk Indexes ---- #
    async def get_existing_chunk_indexes(
        self,
        session: AsyncSession,
        subject_id: UUID,
        document_id: UUID,
    ) -> set[int]:

        rows = await knowledge_base_service.list_by_subject_and_document(
            session=session,
            subject_id=subject_id,
            document_id=document_id,
        )

        return {
            int(row.chunk_index)
            for row in rows
        }



    # ---- Update Chunks By Subject And Document ---- #
    async def update_chunks_by_subject_and_document(
        self,
        session: AsyncSession,
        subject_id: UUID,
        document_id: UUID,
        chunk_id: UUID,
        payload: dict,
    ) -> int:

        return await knowledge_base_service.update_by_subject_document_and_chunk(
            session=session,
            subject_id=subject_id,
            document_id=document_id,
            chunk_id=chunk_id,
            payload=payload,
        )
        
    # ---- Update Chunk ---- #
    async def update_chunk(
        self,
        session: AsyncSession,
        chunk_id: UUID,
        payload: dict,
    ) -> int:

        # ---- Load existing chunk ---- #
        existing = await knowledge_base_service.get_by_id(
            session=session,
            record_id=chunk_id,
        )

        if not existing:
            raise ValueError("Chunk not found")

        # ---- Resolve content ---- #
        content_changed = "content" in payload
        new_content = payload.get("content", existing.content)

        # ---- Default reuse (no recompute) ---- #
        embedding = existing.embedding
        summary = {"summary": existing.summary}

        # ---- Recompute ONLY if content changed ---- #
        if content_changed:
            embedding_service = await get_embedding_service()
            llm_service = await get_llm_service()

            embedding = await embedding_service.embed(new_content)
            summary = await generate_summary(llm_service, new_content)

        # ---- Build update payload ---- #
        update_payload = {
            **payload,
            "content": new_content,
            "embedding": embedding,
            "summary": summary.get("summary", ""),
        }

        # ---- Persist ---- #
        return await knowledge_base_service.update_chunk(
            session=session,
            record_id=chunk_id,
            payload=update_payload,
        )

# ---- DI ---- #
knowledge_base_manager = KnowledgeBaseManager()