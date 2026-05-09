"""Typed data structures for knowledge ingestion."""

# ---- Imports ---- #
from dataclasses import dataclass, field


# -------------------- Chunk Metadata -------------------- #
@dataclass(slots=True)
class ChunkMetadata:
    document_id: int
    source_file: str
    page_number: int
    section_title: str
    main_heading: str
    chunk_index: int
    content_hash: str


# -------------------- Knowledge Chunk -------------------- #
@dataclass(slots=True)
class KnowledgeChunk:
    content: str
    metadata: ChunkMetadata
    summary: str | None = None
    keywords: list[str] = field(default_factory=list)
    related_generated_question_ids: list[int] = field(default_factory=list)


# -------------------- Generated Question Draft -------------------- #
@dataclass(slots=True)
class GeneratedQuestionDraft:
    question: str
    difficulty: str
    question_type: str = "comprehension"
    reasoning: str | None = None
    evidence: str | None = None
    confidence: float = 0.0
