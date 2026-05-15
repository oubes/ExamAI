# ---- Imports ---- #
from pathlib import Path
from uuid import UUID

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_core.documents import Document

# ---- Internal ---- #
from src.services.knowledge.reading.reader import PyMuPDFDocumentLoader
from src.services.knowledge.chunking.cleaner import TextCleaner
from src.services.knowledge.chunking.validator import TextValidator
from src.services.knowledge.chunking.toc_classifier import TOCClassifier
from src.services.knowledge.chunking.splitter import Splitter

from src.domain.storage.services.upload_file import UploadService
from src.domain.knowledge.services.knowledge_base import KnowledgeBaseService

from src.core.di.embedder import get_embedding_service
from src.core.di.llm import get_llm_service
from src.services.knowledge.models.summarizer import generate_summary


# ---- Logging ---- #
logger = logging.getLogger(__name__)


# ---- Reader ---- #
pdf_reader = PyMuPDFDocumentLoader()


# ---- Services ---- #
upload_service = UploadService()
knowledge_base_service = KnowledgeBaseService()


# ---- Pipeline ---- #
class KnowledgePipeline:

    def __init__(self):
        self.cleaner = TextCleaner()
        self.validator = TextValidator()
        self.toc_classifier = TOCClassifier()
        self.splitter = Splitter()

    # ---- Public API ---- #
    async def run(self, file_id: str, subject_id: str, session: AsyncSession):

        file_uuid = UUID(file_id)
        subject_uuid = UUID(subject_id)

        file_path = await self._resolve_file_path(file_uuid, session)
        documents = self._load_documents(file_path)

        embedding_service, llm_service = await self._init_services()

        chunks, total_chunks = self._build_chunks(documents)

        return await self._process_chunks(
            chunks=chunks,
            total_chunks=total_chunks,
            file_uuid=file_uuid,
            subject_id=subject_uuid,
            session=session,
            embedding_service=embedding_service,
            llm_service=llm_service,
        )

    # ---- File Resolution ---- #
    async def _resolve_file_path(self, file_uuid: UUID, session: AsyncSession) -> Path:

        file_info = await upload_service.get_by_id(session, file_uuid)

        if not file_info:
            raise ValueError("File not found")

        return Path(file_info.path)

    # ---- Load Documents ---- #
    def _load_documents(self, path: Path):
        return pdf_reader.load(file_path=path)

    # ---- Init Services ---- #
    async def _init_services(self):
        embedding_service = await get_embedding_service()
        llm_service = await get_llm_service()
        return embedding_service, llm_service

    # ---- Chunk Builder ---- #
    def _build_chunks(self, documents):
        chunks = []
        chunk_counter = 0

        for doc in documents:
            if not isinstance(doc, Document):
                continue

            cleaned = self.cleaner.clean(doc.page_content)

            if not self.validator.is_valid_text(cleaned, 30):
                continue

            parts = self.splitter.split(cleaned)

            for part in parts:
                if not self.validator.is_valid_text(part, 30):
                    continue

                chunk_counter += 1
                chunks.append((chunk_counter, doc, part))

        return chunks, len(chunks)

    # ---- Chunk Processor ---- #
    async def _process_chunks(
        self,
        chunks,
        total_chunks,
        file_uuid,
        subject_id,
        session,
        embedding_service,
        llm_service,
    ):

        processed_chunks = 0
        skipped_chunks = 0

        existing_rows = await knowledge_base_service.list_by_subject_and_document(
            session,
            subject_id,
            file_uuid
        )

        existing_indexes = {row.chunk_index for row in existing_rows}

        for i, (chunk_index, doc, part) in enumerate(chunks, start=1):

            try:

                if chunk_index in existing_indexes:
                    skipped_chunks += 1
                    print(f"[Skip] {i}/{total_chunks}")
                    continue

                meta = self.toc_classifier.enrich_metadata(doc)

                embedding = await embedding_service.embed(part)

                summary = await generate_summary(llm_service, part)

                payload = {
                    "subject_id": subject_id,
                    "document_id": file_uuid,
                    "chunk_index": chunk_index,
                    "content": part,
                    "summary": summary.get("summary", ""),
                    "embedding": embedding,
                    "metadata": meta,
                }

                await knowledge_base_service.create(session, payload)

                processed_chunks += 1

                # ---- ACCURATE PROGRESS ---- #
                print(
                    f"[Progress] {i}/{total_chunks} "
                    f"| inserted={processed_chunks} "
                    f"| skipped={skipped_chunks}"
                )

            except Exception:
                logger.exception("Chunk processing failed")
                continue

        return {
            "file_id": str(file_uuid),
            "subject_id": str(subject_id),
            "chunks_created": processed_chunks,
            "total_chunks": total_chunks,
            "skipped_chunks": skipped_chunks,
        }


# ---- DI ---- #
knowledge_pipeline = KnowledgePipeline()