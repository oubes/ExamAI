# ----- IMPORTS ----- #
from uuid import UUID
from pydantic import BaseModel, Field


# ----- Option Response ----- #
class QuestionOptionResponse(BaseModel):

    id: UUID
    question_id: UUID
    option_text: str | None = None
    is_correct: bool
    order: int | None = None

    class Config:
        from_attributes = True


# ----- Model Answer Response ----- #
class ModelAnswerResponse(BaseModel):

    id: UUID
    question_id: UUID
    answer_text: str | None = None

    class Config:
        from_attributes = True


# ----- Question Bundle Response ----- #
class QuestionBundleResponse(BaseModel):

    id: UUID
    subject_id: UUID
    chapter_id: UUID
    topic_id: UUID

    content: str
    explanation: str | None = None

    type: str
    difficulty: int
    importance: int

    tags: str | None = None

    options: list[QuestionOptionResponse] | None = None
    model_answer: ModelAnswerResponse | None = None

    options_count: int
    has_model_answer: bool

    class Config:
        from_attributes = True


# ----- Question Bundle List Response ----- #
class QuestionBundleListResponse(BaseModel):

    id: UUID
    subject_id: UUID
    chapter_id: UUID
    topic_id: UUID

    content: str
    type: str

    difficulty: int
    importance: int

    tags: str | None = None

    options_count: int
    has_model_answer: bool

    class Config:
        from_attributes = True


# ----- Update Option Request ----- #
class UpdateOptionRequest(BaseModel):

    id: UUID | None = None
    option_text: str
    is_correct: bool = False
    order: int = 0


# ----- Question Update Request ----- #
class QuestionBundleUpdateRequest(BaseModel):

    content: str | None = None
    explanation: str | None = None

    difficulty: int | None = None
    importance: int | None = None

    tags: str | None = None

    model_answer: str | None = None
    options: list[UpdateOptionRequest] | None = None


# ----- Delete Response ----- #
class DeleteQuestionResponse(BaseModel):

    deleted: bool


# ----- Query ----- #
class QuestionListQuery(BaseModel):

    subject_id: UUID | None = None
    chapter_id: UUID | None = None
    topic_id: UUID | None = None

    limit: int = Field(default=50, le=200)
    offset: int = 0