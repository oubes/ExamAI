from typing import TypedDict, Optional, Any, Dict

class BaseState(TypedDict, total=False):
    msg: Optional[str]
    submission_id: Optional[str]
    student_id: Optional[str]
    exam_id: Optional[str]

class OCRState(TypedDict, total=False):
    ocr_result: Any

class TokenState(TypedDict, total=False):
    token_quality_score: Any
    processed_text: Any

class GradingState(TypedDict, total=False):
    grading_score: Any

class FeedbackState(TypedDict, total=False):
    feedback_text: Any

class SecurityState(TypedDict, total=False):
    security_flags: Any
    semantic_cache_hit: Any

class HITLState(TypedDict, total=False):
    hitl_review_notes: Any

class AdaptiveExamState(TypedDict, total=False):
    adaptive_exam_plan: Any

class AgentState(
    BaseState,
    OCRState,
    TokenState,
    GradingState,
    FeedbackState,
    SecurityState,
    HITLState,
    AdaptiveExamState
):
    extra: Dict[str, Any]