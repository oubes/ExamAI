"""
scripts/router.py
-----------------
Exam Submission Processing Pipeline

This module receives a JSON exam submission payload and routes each question
to the appropriate processor based on its `question_type`. The dispatcher
pattern used here makes it trivial to plug in new question types (e.g. "essay",
"fill_in_the_blank", "coding") or swap in an AI grading agent without touching
the core routing logic.

Design overview
---------------
    JSON payload
        │
        ▼
    parse_submission()          ← validates & deserialises the raw dict
        │
        ▼
    process_submission()        ← iterates questions, delegates via DISPATCHER
        │
        ├──► process_mcq()          for question_type == "mcq"
        └──► process_open_ended()   for question_type == "open_ended"
        │
        ▼
    List[QuestionResult]        ← structured output
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Callable

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data models (plain dataclasses – swap for Pydantic if needed)
# ---------------------------------------------------------------------------


@dataclass
class Question:
    """Represents a single question extracted from the submission payload."""

    question_id: str
    question_type: str
    student_answer: Any
    max_score: float
    # Optional fields that may be populated for AI grading
    correct_answer: Any = field(default=None)
    rubric: str = field(default="")


@dataclass
class ExamSubmission:
    """Represents a full exam submission received from the API."""

    exam_id: str
    student_id: str
    submission_type: str
    submission_timestamp: str
    questions: list[Question]


@dataclass
class QuestionResult:
    """
    Full grading record for a single question.

    Carries both the original question metadata and the grading outcome so
    consumers of the pipeline never need to cross-reference a second object.
    """

    # ── Question metadata (mirrored from the input) ───────────────────────
    question_id: str
    question_type: str
    student_answer: Any
    max_score: float
    correct_answer: Any = field(default=None)
    rubric: str = field(default="")

    # ── Grading outcome ───────────────────────────────────────────────────
    score: float = field(default=0.0)
    grader: str = field(default="")   # which processor awarded the score
    notes: str = field(default="")

    def to_dict(self) -> dict:
        """Serialise the full record to a plain dict for API responses."""
        return {
            # --- question metadata ---
            "question_id": self.question_id,
            "question_type": self.question_type,
            "student_answer": self.student_answer,
            "correct_answer": self.correct_answer,
            "rubric": self.rubric,
            # --- grading outcome ---
            "score": self.score,
            "max_score": self.max_score,
            "grader": self.grader,
            "notes": self.notes,
        }


# ---------------------------------------------------------------------------
# Individual question processors
# ---------------------------------------------------------------------------


def process_mcq(question: Question) -> QuestionResult:
    """
    Grade a multiple-choice question.

    Scoring rule:
        - Full ``max_score`` awarded when ``student_answer`` matches the
          ``correct_answer`` (case-insensitive string comparison).
        - Zero points otherwise.

    Parameters
    ----------
    question:
        A :class:`Question` instance whose ``question_type`` is ``"mcq"``.

    Returns
    -------
    QuestionResult
        The grading result for this question.

    AI integration note
    -------------------
    For probabilistic / adaptive MCQ scoring (partial credit, confidence
    weighting) this function can delegate to an AI agent by calling:

        score = ai_client.grade_mcq(question)
    """
    correct = str(question.correct_answer or "").strip().upper()
    given = str(question.student_answer or "").strip().upper()

    if correct and given == correct:
        score = question.max_score
        notes = "Correct answer."
    elif not correct:
        # No key provided yet – placeholder score; AI agent or instructor review needed
        score = 0.0
        notes = "Answer key not provided; manual review required."
        logger.warning("MCQ %s has no correct_answer defined.", question.question_id)
    else:
        score = 0.0
        notes = f"Incorrect. Expected '{correct}', got '{given}'."

    logger.debug("MCQ %s → %.1f / %.1f", question.question_id, score, question.max_score)
    return QuestionResult(
        # question metadata
        question_id=question.question_id,
        question_type=question.question_type,
        student_answer=question.student_answer,
        correct_answer=question.correct_answer,
        rubric=question.rubric,
        max_score=question.max_score,
        # grading outcome
        score=score,
        grader="mcq_processor",
        notes=notes,
    )


def process_open_ended(question: Question) -> QuestionResult:
    """
    Grade an open-ended (free-text) question.

    In production this processor should call an AI grading agent.  The stub
    below assigns a placeholder score of 80 % of ``max_score`` so the pipeline
    can run end-to-end before the AI integration is wired up.

    Parameters
    ----------
    question:
        A :class:`Question` instance whose ``question_type`` is ``"open_ended"``.

    Returns
    -------
    QuestionResult
        The grading result for this question.

    AI integration note
    -------------------
    Replace the placeholder block with:

        from app.services.grading.ai_grader import grade_open_ended
        score, feedback = grade_open_ended(
            student_answer=question.student_answer,
            rubric=question.rubric,
            max_score=question.max_score,
        )

    The ``grade_open_ended`` service would call an LLM (e.g. GPT-4o, Gemini,
    or a fine-tuned grading model) and return a numeric score plus textual
    feedback.  The rubric or model answer can be stored alongside the question
    in the database and injected here before dispatching.
    """
    # ------------------------------------------------------------------
    # TODO: replace the placeholder below with the real AI grading call
    # ------------------------------------------------------------------
    placeholder_score = round(question.max_score * 0.8, 2)
    notes = (
        "Placeholder score (80 % of max). "
        "Wire up an AI grading agent to replace this."
    )

    logger.debug(
        "Open-ended %s → %.1f / %.1f (placeholder)",
        question.question_id,
        placeholder_score,
        question.max_score,
    )
    return QuestionResult(
        # question metadata
        question_id=question.question_id,
        question_type=question.question_type,
        student_answer=question.student_answer,
        correct_answer=question.correct_answer,
        rubric=question.rubric,
        max_score=question.max_score,
        # grading outcome
        score=placeholder_score,
        grader="open_ended_processor (placeholder)",
        notes=notes,
    )


# ---------------------------------------------------------------------------
# Dispatcher registry
# ---------------------------------------------------------------------------

# Maps question_type strings to their processor callables.
# To add a new type, simply register it here – no other code needs to change.
DISPATCHER: dict[str, Callable[[Question], QuestionResult]] = {
    "mcq": process_mcq,
    "open_ended": process_open_ended,
    # Future processors can be added here, e.g.:
    # "essay":              process_essay,
    # "fill_in_the_blank":  process_fill_in_the_blank,
    # "coding":             process_coding,
}


def _unknown_type_handler(question: Question) -> QuestionResult:
    """
    Fallback processor for unrecognised question types.

    Returns a zero-scored result and logs a warning so the unknown type is
    visible in monitoring without crashing the pipeline.
    """
    logger.warning(
        "Unknown question_type '%s' for question %s. Scoring 0.",
        question.question_type,
        question.question_id,
    )
    return QuestionResult(
        # question metadata
        question_id=question.question_id,
        question_type=question.question_type,
        student_answer=question.student_answer,
        correct_answer=question.correct_answer,
        rubric=question.rubric,
        max_score=question.max_score,
        # grading outcome
        score=0.0,
        grader="fallback",
        notes=f"Unrecognised question type: '{question.question_type}'.",
    )


# ---------------------------------------------------------------------------
# Core pipeline functions
# ---------------------------------------------------------------------------


def parse_submission(payload: dict) -> ExamSubmission:
    """
    Deserialise and validate a raw submission payload dict.

    Parameters
    ----------
    payload:
        The decoded JSON dict received from the API endpoint.

    Returns
    -------
    ExamSubmission
        A validated, typed submission object.

    Raises
    ------
    KeyError
        If a required top-level field is missing from the payload.
    """
    questions = [
        Question(
            question_id=q["question_id"],
            question_type=q["question_type"],
            student_answer=q.get("student_answer"),
            max_score=float(q.get("max_score", 0)),
            correct_answer=q.get("correct_answer"),
            rubric=q.get("rubric", ""),
        )
        for q in payload["questions"]
    ]

    return ExamSubmission(
        exam_id=payload["exam_id"],
        student_id=payload["student_id"],
        submission_type=payload.get("submission_type", "unknown"),
        submission_timestamp=payload.get("submission_timestamp", ""),
        questions=questions,
    )


def process_submission(submission: ExamSubmission) -> list[QuestionResult]:
    """
    Route every question in the submission to its processor and collect results.

    Parameters
    ----------
    submission:
        A parsed :class:`ExamSubmission` instance.

    Returns
    -------
    list[QuestionResult]
        One result object per question, in the same order as the submission.
    """
    results: list[QuestionResult] = []

    for question in submission.questions:
        # Look up the processor; fall back gracefully for unknown types
        processor = DISPATCHER.get(question.question_type, _unknown_type_handler)
        result = processor(question)
        results.append(result)

    logger.info(
        "Processed submission %s for student %s – %d questions graded.",
        submission.exam_id,
        submission.student_id,
        len(results),
    )
    return results


def run_pipeline(raw_json: str | dict) -> list[dict]:
    """
    End-to-end entry point: accept raw JSON (string or dict) and return
    a list of serialised result dicts ready for an API response.

    Parameters
    ----------
    raw_json:
        Either a JSON string or an already-parsed dict.

    Returns
    -------
    list[dict]
        One dict per question containing the full question metadata
        (``question_id``, ``question_type``, ``student_answer``,
        ``correct_answer``, ``rubric``, ``max_score``) plus the grading
        outcome (``score``, ``grader``, ``notes``).
    """
    payload: dict = json.loads(raw_json) if isinstance(raw_json, str) else raw_json
    submission = parse_submission(payload)
    results = process_submission(submission)
    return [r.to_dict() for r in results]


# ---------------------------------------------------------------------------
# Example – demonstrates the full pipeline
# ---------------------------------------------------------------------------

# if __name__ == "__main__":
#     logging.basicConfig(level=logging.DEBUG, format="%(levelname)s | %(message)s")

#     EXAMPLE_SUBMISSION: dict = {
#         "exam_id": "EXAM_2026_01",
#         "student_id": "STU_1024",
#         "submission_type": "scanned",
#         "questions": [
#             {
#                 "question_id": "Q1",
#                 "question_type": "open_ended",
#                 "student_answer": (
#                     "The algorithm minimizes the loss function using gradient descent."
#                 ),
#                 "max_score": 10,
#                 "rubric": "",
#             },
#             {
#                 "question_id": "Q2",
#                 "question_type": "mcq",
#                 "student_answer": "B",
#                 "correct_answer": "B",   # injected server-side; never from student payload
#                 "max_score": 5,
#             },
#         ],
#         "submission_timestamp": "2026-02-01T14:35:22",
#     }

#     print("\n--- Exam Submission Processor ---\n")
#     print("Input payload:")
#     print(json.dumps(EXAMPLE_SUBMISSION, indent=2))

#     results = run_pipeline(EXAMPLE_SUBMISSION)

#     print("\nFull grading results (all fields):")
#     print(json.dumps(results, indent=2))
