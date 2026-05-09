"""Adaptive exam question generation pipeline."""

# ---- Imports ---- #
from __future__ import annotations

import json
import logging
import re
import time
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.di.settings import Settings, get_settings
from src.domain.adaptive_exam.models.generated_exam_question import GeneratedExamQuestion
from src.domain.adaptive_exam.models.generated_exam_session import GeneratedExamSession
from src.domain.system.services.prompt_run import PromptRunService
from src.domains.academic.models.question import Question
from src.domains.academic.services.exam import ExamService
from src.infra.embedding.adapter import EmbeddingClient
from src.infra.embedding.service import EmbeddingService
from src.infra.llm.adapter import LLMClient
from src.infra.llm.service import LLMService

from .prompt_loader import render_prompt_template
from .reader import KnowledgeChunkReader
from .types import GeneratedQuestionDraft, KnowledgeChunk


# ---- Logging ---- #
logger = logging.getLogger(__name__)


# -------------------- Difficulty Mapping -------------------- #
DIFFICULTY_FITS: dict[str, float] = {
    "easy": 0.25,
    "medium": 0.50,
    "hard": 0.75,
    "deep_focus": 0.95,
    "deep-focus": 0.95,
}


# -------------------- Adaptive Question Pipeline -------------------- #
class AdaptiveExamQuestionPipeline:

    # ---- Constructor ---- #
    def __init__(
        self,
        *,
        llm_service: LLMService | None = None,
        embedding_service: EmbeddingService | None = None,
        reader: KnowledgeChunkReader | None = None,
        prompt_run_service: PromptRunService | None = None,
        exam_service: ExamService | None = None,
        settings: Settings | None = None,
        prompt_template_name: str = "adaptive_exam_question_generation.yaml",
    ) -> None:

        self._settings = settings or get_settings()
        self._prompt_template_name = prompt_template_name
        self._reader = reader or KnowledgeChunkReader()
        self._prompt_run_service = prompt_run_service or PromptRunService()
        self._exam_service = exam_service or ExamService()

        self._llm_service = llm_service or LLMService(
            LLMClient(self._settings),
            self._settings,
        )

        self._embedding_service = embedding_service or EmbeddingService(
            EmbeddingClient(self._settings),
            self._settings,
        )

    # ---- Public API ---- #
    async def generate_for_document(
        self,
        session: AsyncSession,
        *,
        generated_exam_session: GeneratedExamSession,
        document_id: int,
        exam_id: int | None = None,
        exam_title: str | None = None,
        questions_per_chunk: int = 4,
    ) -> list[GeneratedExamQuestion]:

        chunks = await self._reader.list_by_document(session, document_id)

        if not chunks:
            logger.info("[AdaptiveExamQuestionPipeline] no chunks found document_id=%s", document_id)
            return []

        active_exam_id = exam_id

        if active_exam_id is None:
            source_name = Path(chunks[0].source_file).stem.replace("_", " ").replace("-", " ")
            title = exam_title or f"Adaptive Egyptology Exam - {source_name or 'Generated'}"
            active_exam = await self._exam_service.create(
                session=session,
                subject_id=generated_exam_session.subject_id,
                title=title,
                time_limit=0,
            )
            active_exam_id = active_exam.id

        generated_rows: list[GeneratedExamQuestion] = []
        question_order = 0

        for record in chunks:
            chunk = self._reader.to_chunk(record)
            drafts = await self._generate_chunk_questions(
                session=session,
                chunk=chunk,
                questions_per_chunk=questions_per_chunk,
            )

            if not drafts:
                continue

            question_rows = []
            paired_rows: list[tuple[GeneratedQuestionDraft, Question]] = []

            for draft in drafts:
                question_text = draft.question.strip()

                if not question_text:
                    continue

                embedding = await self._embedding_service.embed(question_text)
                question_type = self._build_question_type(draft)

                question_rows.append(
                    Question(
                        exam_id=active_exam_id,
                        content=question_text,
                        type=question_type,
                        search_text=question_text,
                        embedding=embedding,
                    )
                )
                paired_rows.append((draft, question_rows[-1]))

            session.add_all(question_rows)
            await session.flush()

            generated_question_rows = []
            for draft, question in paired_rows:
                generated_question_rows.append(
                    GeneratedExamQuestion(
                        session_id=generated_exam_session.id,
                        knowledge_base_id=record.id,
                        question_id=question.id,
                        question_order=question_order,
                        selection_reason=self._build_selection_reason(draft),
                        predicted_difficulty_fit=self._difficulty_fit(draft.difficulty),
                    )
                )
                question_order += 1

            session.add_all(generated_question_rows)
            await session.flush()

            generated_rows.extend(generated_question_rows)

        await session.commit()

        return generated_rows

    # ---- Chunk Generation ---- #
    async def _generate_chunk_questions(
        self,
        session: AsyncSession,
        chunk: KnowledgeChunk,
        questions_per_chunk: int,
    ) -> list[GeneratedQuestionDraft]:

        rendered = render_prompt_template(
            self._prompt_template_name,
            {
                "source_file": chunk.metadata.source_file,
                "page_number": chunk.metadata.page_number,
                "main_heading": chunk.metadata.main_heading,
                "section_title": chunk.metadata.section_title,
                "chunk_index": chunk.metadata.chunk_index,
                "content_hash": chunk.metadata.content_hash,
                "content": chunk.content,
                "question_count": questions_per_chunk,
            },
        )

        messages = [
            {"role": "system", "content": rendered["system"]},
            {"role": "user", "content": rendered["user"]},
        ]

        prompt_text = self._serialize_messages(messages)
        start = time.perf_counter()

        response = await self._llm_service.generate(
            messages=messages,
            temperature=self._settings.alibaba_model_temp,
            max_tokens=1200,
        )

        latency_ms = (time.perf_counter() - start) * 1000.0
        drafts = self._parse_response(response)

        await self._prompt_run_service.create(
            session,
            model_name=self._model_name(),
            prompt=prompt_text,
            response=response,
            token_usage=0,
            latency_ms=latency_ms,
            confidence=self._average_confidence(drafts),
        )

        return drafts

    # ---- Parsing ---- #
    def _parse_response(self, response: str) -> list[GeneratedQuestionDraft]:
        payload = self._extract_json(response)

        if isinstance(payload, dict):
            items = payload.get("questions", [])
        else:
            items = payload

        drafts: list[GeneratedQuestionDraft] = []

        if not isinstance(items, list):
            return drafts

        for item in items:
            if not isinstance(item, dict):
                continue

            question_text = str(item.get("question", "")).strip()
            difficulty = self._normalize_difficulty(str(item.get("difficulty", "medium")))

            if not question_text:
                continue

            drafts.append(
                GeneratedQuestionDraft(
                    question=question_text,
                    difficulty=difficulty,
                    question_type=str(item.get("question_type", "comprehension")).strip() or "comprehension",
                    reasoning=str(item.get("reasoning", "")).strip() or None,
                    evidence=str(item.get("evidence", "")).strip() or None,
                    confidence=self._safe_float(item.get("confidence", 0.0)),
                )
            )

        return drafts

    def _extract_json(self, response: str) -> Any:
        cleaned = response.strip()

        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r"\s*```$", "", cleaned)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)

            if match:
                return json.loads(match.group(0))

        raise ValueError("LLM response did not contain valid JSON")

    # ---- Persistence Helpers ---- #
    def _build_question_type(self, draft: GeneratedQuestionDraft) -> str:
        return f"egyptology_{self._normalize_difficulty(draft.difficulty)}_{draft.question_type or 'comprehension'}"

    def _build_selection_reason(self, draft: GeneratedQuestionDraft) -> str:
        pieces = [
            f"difficulty={draft.difficulty}",
            f"type={draft.question_type}",
        ]

        if draft.reasoning:
            pieces.append(draft.reasoning)

        if draft.evidence:
            pieces.append(f"evidence={draft.evidence}")

        return " | ".join(pieces)

    def _difficulty_fit(self, difficulty: str) -> float:
        return DIFFICULTY_FITS.get(self._normalize_difficulty(difficulty), 0.50)

    # ---- Utility ---- #
    def _average_confidence(self, drafts: list[GeneratedQuestionDraft]) -> float:
        if not drafts:
            return 0.0

        return sum(draft.confidence for draft in drafts) / len(drafts)

    def _serialize_messages(self, messages: list[dict[str, str]]) -> str:
        return json.dumps(messages, ensure_ascii=False, indent=2)

    def _model_name(self) -> str:
        return getattr(self._llm_service, "_model", "unknown")

    def _normalize_difficulty(self, difficulty: str) -> str:
        normalized = difficulty.strip().lower().replace("-", "_")
        return normalized if normalized in DIFFICULTY_FITS else "medium"

    def _safe_float(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
