# ---- Standard Library ---- #
import logging
from typing import Any

# ---- External ---- #
from langchain_core.documents import Document

# ---- Internal ---- #
from src.services.knowledge.chunking.cleaner import TextCleaner
from src.services.knowledge.chunking.validator import TextValidator
from src.services.knowledge.chunking.toc_classifier import TOCClassifier
from src.services.knowledge.chunking.splitter import Splitter
from src.core.di.embedder import get_embedding_service
from src.core.di.settings import get_settings

# ---- Logging ---- #
logger = logging.getLogger(__name__)

# ---- Embedding Service ---- #
embedding_service = get_embedding_service()


# ---- Chunker ---- #
class Chunker:

    # ---- Initialization ---- #
    def __init__(
        self,
        config: Any,
        cleaner: TextCleaner,
        validator: TextValidator,
        toc_classifier: TOCClassifier,
        splitter: Splitter,
    ):
        self.cleaner = cleaner
        self.validator = validator
        self.toc_classifier = toc_classifier
        self.splitter = splitter

        self.min_length = getattr(config, "min_length", 30)

    # ---- Public API ---- #
    async def chunk_documents(
        self,
        documents: list[Document],
        doc_name: str,
    ) -> list[dict]:

        if not documents:
            logger.warning("No documents provided.")
            return []

        # ---- Normalize Nested Input ---- #
        if documents and isinstance(documents[0], list):
            documents = [
                doc
                for sublist in documents
                for doc in sublist
                if isinstance(doc, Document)
            ]

        chunks: list[dict] = []
        chunk_counter = 0

        for doc in documents:

            try:

                # ---- Type Safety ---- #
                if not isinstance(doc, Document):
                    logger.warning(
                        f"Skipping invalid document type: {type(doc)}"
                    )
                    continue

                raw_text = doc.page_content

                # ---- Pre-Cleaning ---- #
                cleaned_text = self.cleaner.clean(raw_text)

                # ---- Pre-Validation ---- #
                if not self.validator.is_valid_text(
                    cleaned_text,
                    self.min_length,
                ):
                    continue

                # ---- Metadata / Classification ---- #
                meta = self.toc_classifier.enrich_metadata(doc)

                # ---- Splitting ---- #
                parts = self.splitter.split(cleaned_text)

                if not parts:
                    continue

                for part in parts:

                    # ---- Post-Validation ---- #
                    if not self.validator.is_valid_text(
                        part,
                        self.min_length,
                    ):
                        continue

                    # ---- Embedding ---- #
                    embedding = await embedding_service.embed(part) # type: ignore

                    # ---- Chunk Build ---- #
                    chunks.append(
                        {
                            "content": part,
                            "doc_name": doc_name,
                            "metadata": meta,
                            "chunk_index": chunk_counter,
                            "raw_content": part,
                            "embedding": embedding,
                        }
                    )

                    chunk_counter += 1

            except Exception:
                logger.exception("Failed processing document")
                continue

        logger.info(
            f"[Chunker] Generated {len(chunks)} adaptive chunks"
        )

        return chunks
    
# ---- DI ---- #
chunker = Chunker(
    config=get_settings(),
    cleaner=TextCleaner(),
    validator=TextValidator(),
    toc_classifier=TOCClassifier(),
    splitter=Splitter(get_settings()),
)