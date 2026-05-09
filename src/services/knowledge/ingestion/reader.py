"""Readers for stored knowledge chunks."""

# ---- Imports ---- #
from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.knowledge.models import KnowledgeBase
from src.domains.knowledge.service import KnowledgeService

from .types import ChunkMetadata, KnowledgeChunk


# ---- Logging ---- #
logger = logging.getLogger(__name__)


# -------------------- Knowledge Chunk Reader -------------------- #
class KnowledgeChunkReader:

    # ---- Constructor ---- #
    def __init__(self, knowledge_service: KnowledgeService | None = None) -> None:
        self._knowledge_service = knowledge_service or KnowledgeService()

    # ---- Query Helpers ---- #
    async def list_by_document(
        self,
        session: AsyncSession,
        document_id: int,
    ) -> list[KnowledgeBase]:

        return await self._knowledge_service.list_by_document(session, document_id)

    async def list_by_subject(
        self,
        session: AsyncSession,
        subject_id: int,
    ) -> list[KnowledgeBase]:

        return await self._knowledge_service.list_by_subject(session, subject_id)

    # ---- Iterators ---- #
    async def iter_by_document(
        self,
        session: AsyncSession,
        document_id: int,
    ):

        for record in await self.list_by_document(session, document_id):
            yield self.to_chunk(record)

    async def iter_paragraphs(
        self,
        session: AsyncSession,
        document_id: int,
    ):

        async for chunk in self.iter_by_document(session, document_id):
            yield chunk

    # ---- Conversion ---- #
    def to_chunk(self, record: KnowledgeBase) -> KnowledgeChunk:
        metadata = ChunkMetadata(
            document_id=record.document_id,
            source_file=record.source_file,
            page_number=record.page_number,
            section_title=record.section_title or "",
            main_heading=record.main_heading or (record.section_title or ""),
            chunk_index=record.chunk_index,
            content_hash=record.content_hash,
        )

        related_question_ids = [
            relation.question_id
            for relation in getattr(record, "generated_questions", [])
            if getattr(relation, "question_id", None) is not None
        ]

        return KnowledgeChunk(
            content=record.content,
            metadata=metadata,
            summary=record.summary,
            keywords=[keyword.strip() for keyword in (record.keywords or "").split(",") if keyword.strip()],
            related_generated_question_ids=related_question_ids,
        )

    def prepare_for_llm(self, record: KnowledgeBase) -> dict[str, Any]:
        chunk = self.to_chunk(record)

        return {
            "document_id": chunk.metadata.document_id,
            "source_file": chunk.metadata.source_file,
            "page_number": chunk.metadata.page_number,
            "section_title": chunk.metadata.section_title,
            "main_heading": chunk.metadata.main_heading,
            "chunk_index": chunk.metadata.chunk_index,
            "content_hash": chunk.metadata.content_hash,
            "content": chunk.content,
            "summary": chunk.summary,
            "keywords": chunk.keywords,
            "related_generated_question_ids": chunk.related_generated_question_ids,
        }
