"""Docling-backed chunking and ingestion for adaptive exam knowledge."""

# ---- Imports ---- #
from __future__ import annotations

import hashlib
import logging
import re
from pathlib import Path
from typing import Any, Iterable

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config.settings import Settings
from src.domains.knowledge.models import KnowledgeBase
from src.domains.knowledge.service import KnowledgeService
from src.infra.embedding.adapter import EmbeddingClient
from src.infra.embedding.service import EmbeddingService
from src.core.di.settings import get_settings

from .types import ChunkMetadata, KnowledgeChunk

try:
    from docling.document_converter import DocumentConverter
except ImportError:  # pragma: no cover - optional runtime dependency
    DocumentConverter = None


# ---- Logging ---- #
logger = logging.getLogger(__name__)


# -------------------- Knowledge Ingestion Chunker -------------------- #
class KnowledgeIngestionChunker:

    # ---- Constructor ---- #
    def __init__(
        self,
        *,
        knowledge_service: KnowledgeService | None = None,
        embedding_service: EmbeddingService | None = None,
        settings: Settings | None = None,
    ) -> None:
        self._knowledge_service = knowledge_service or KnowledgeService()
        self._settings = settings or get_settings()

        if embedding_service is not None:
            self._embedding_service = embedding_service
        else:
            self._embedding_service = EmbeddingService(
                EmbeddingClient(self._settings),
                self._settings,
            )

    # ---- Public API ---- #
    def chunk_pdf(
        self,
        pdf_path: str | Path,
    ) -> list[KnowledgeChunk]:

        source_path = Path(pdf_path).expanduser().resolve()

        if not source_path.exists():
            raise FileNotFoundError(f"PDF source not found: {source_path}")

        document = self._convert_document(source_path)
        document_id = self._derive_document_id(source_path)
        source_file = source_path.as_posix()

        chunks: list[KnowledgeChunk] = []
        heading_stack: list[tuple[int, str]] = []
        current_page = 0
        chunk_index = 0

        for text, level, page_number, label in self._iterate_text_items(document):
            if self._is_heading(text=text, level=level, label=label):
                heading_stack = self._update_heading_stack(heading_stack, text, level)
                if page_number is not None:
                    current_page = page_number
                continue

            section_title = heading_stack[-1][1] if heading_stack else self._default_title(source_path)
            main_heading = heading_stack[0][1] if heading_stack else section_title
            resolved_page = page_number or current_page or 0

            metadata = ChunkMetadata(
                document_id=document_id,
                source_file=source_file,
                page_number=resolved_page,
                section_title=section_title,
                main_heading=main_heading,
                chunk_index=chunk_index,
                content_hash=self._content_hash(document_id, chunk_index, text),
            )

            chunks.append(
                KnowledgeChunk(
                    content=text,
                    metadata=metadata,
                    summary=self._build_summary(text, section_title),
                    keywords=self._build_keywords(source_path, heading_stack, text),
                )
            )
            chunk_index += 1

            if page_number is not None:
                current_page = page_number

        logger.info(
            "[KnowledgeIngestionChunker] chunked pdf=%s chunks=%d",
            source_file,
            len(chunks),
        )

        return chunks

    async def ingest_pdf(
        self,
        session: AsyncSession,
        pdf_path: str | Path,
        subject_id: int,
    ) -> list[KnowledgeBase]:

        chunks = self.chunk_pdf(pdf_path)

        if not chunks:
            return []

        embeddings = await self._embedding_service.embed_batch(
            [chunk.content for chunk in chunks]
        )

        records: list[dict[str, Any]] = []

        for chunk, embedding in zip(chunks, embeddings, strict=False):
            search_text = self._build_search_text(chunk)

            records.append(
                {
                    "subject_id": subject_id,
                    "document_id": chunk.metadata.document_id,
                    "chunk_index": chunk.metadata.chunk_index,
                    "page_number": chunk.metadata.page_number,
                    "section_title": chunk.metadata.section_title,
                    "main_heading": chunk.metadata.main_heading,
                    "source_file": chunk.metadata.source_file,
                    "content_hash": chunk.metadata.content_hash,
                    "search_text": search_text,
                    "content": chunk.content,
                    "summary": chunk.summary,
                    "keywords": ", ".join(chunk.keywords) if chunk.keywords else None,
                    "source_type": "pdf",
                    "quality_score": 1.0,
                    "importance_score": 1.0,
                    "embedding": embedding,
                }
            )

        created = await self._knowledge_service.bulk_create(session, records)

        logger.info(
            "[KnowledgeIngestionChunker] ingested pdf=%s persisted_chunks=%d",
            Path(pdf_path).expanduser().resolve().as_posix(),
            len(created),
        )

        return created

    # ---- Document Conversion ---- #
    def _convert_document(self, source_path: Path) -> Any:
        if DocumentConverter is None:
            raise RuntimeError(
                "Docling is not installed. Add it to the environment to enable PDF chunking."
            )

        converter = DocumentConverter()
        result = converter.convert(str(source_path))
        return getattr(result, "document", result)

    # ---- Item Iteration ---- #
    def _iterate_text_items(self, document: Any) -> Iterable[tuple[str, int, int | None, str]]:
        for item, level in document.iterate_items():
            text = self._extract_text(item)

            if not text:
                continue

            page_number = self._extract_page_number(getattr(item, "prov", None))
            label = str(getattr(item, "label", "") or "").upper()

            yield text, level, page_number, label

    # ---- Heuristics ---- #
    def _is_heading(self, *, text: str, level: int, label: str) -> bool:
        if label in {"TITLE", "HEADING", "SECTION", "CHAPTER", "SUBTITLE"}:
            return True

        cleaned = text.strip()

        if not cleaned:
            return False

        if level <= 1 and len(cleaned) <= 180 and len(cleaned.split()) <= 24:
            return True

        if cleaned.isupper() and len(cleaned.split()) <= 12:
            return True

        if cleaned.endswith(":") and len(cleaned) <= 120:
            return True

        return False

    def _update_heading_stack(
        self,
        heading_stack: list[tuple[int, str]],
        heading_text: str,
        level: int,
    ) -> list[tuple[int, str]]:

        while heading_stack and heading_stack[-1][0] >= level:
            heading_stack.pop()

        heading_stack.append((level, heading_text.strip()))
        return heading_stack

    # ---- Extractors ---- #
    def _extract_text(self, item: Any) -> str:
        text = getattr(item, "text", None)

        if isinstance(text, str):
            return self._normalize_text(text)

        return ""

    def _extract_page_number(self, provenance: Any) -> int | None:
        if provenance is None:
            return None

        items = provenance if isinstance(provenance, (list, tuple)) else [provenance]

        for item in items:
            page_number = getattr(item, "page_no", None)

            if isinstance(page_number, int) and page_number > 0:
                return page_number

        return None

    # ---- Metadata Helpers ---- #
    def _derive_document_id(self, source_path: Path) -> int:
        digest = hashlib.sha256(source_path.as_posix().encode("utf-8")).digest()
        return int.from_bytes(digest[:8], byteorder="big", signed=False)

    def _content_hash(self, document_id: int, chunk_index: int, content: str) -> str:
        digest = hashlib.sha256(
            f"{document_id}:{chunk_index}:{self._normalize_text(content)}".encode("utf-8")
        ).hexdigest()

        return digest

    def _default_title(self, source_path: Path) -> str:
        return source_path.stem.replace("-", " ").replace("_", " ").strip() or "Document"

    def _build_summary(self, content: str, section_title: str) -> str:
        preview = self._normalize_text(content)[:220]
        if section_title:
            return f"{section_title}: {preview}"
        return preview

    def _build_keywords(
        self,
        source_path: Path,
        heading_stack: list[tuple[int, str]],
        content: str,
    ) -> list[str]:

        keywords: list[str] = [source_path.stem.replace("-", " ").replace("_", " ").strip()]

        for _, heading in heading_stack[:2]:
            if heading and heading not in keywords:
                keywords.append(heading)

        content_words = [
            word.strip(".,;:!?()[]{}\"'")
            for word in self._normalize_text(content).split()
            if len(word) > 5
        ]

        for word in content_words:
            if word.lower() not in {keyword.lower() for keyword in keywords}:
                keywords.append(word)

            if len(keywords) >= 8:
                break

        return [keyword for keyword in keywords if keyword]

    def _build_search_text(self, chunk: KnowledgeChunk) -> str:
        pieces = [
            chunk.metadata.main_heading,
            chunk.metadata.section_title,
            chunk.content,
        ]

        return self._normalize_text("\n".join(piece for piece in pieces if piece))

    def _normalize_text(self, text: str) -> str:
        return re.sub(r"\s+", " ", text or "").strip()
