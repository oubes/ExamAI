# ----- importing all models ----- #
from src.domain.identity.models.session import UserSession
from src.domain.identity.models.user import User

from src.domain.adaptive_exam.models.generated_exam_question import GeneratedExamQuestion
from src.domain.adaptive_exam.models.generated_exam_session import GeneratedExamSession

from src.domain.attempts.models.answer import Answer
from src.domain.attempts.models.attempt import ExamAttempt
from src.domain.attempts.models.feedback import Feedback

from src.domain.knowledge.models.knowledge_base import KnowledgeBase

from src.domain.storage.models.upload_file import UploadFile

from src.domain.questions.models.question import Question
from src.domain.questions.models.question_skill import QuestionSkill
from src.domain.questions.models.model_answer import ModelAnswer
from src.domain.questions.models.option import QuestionOption
from src.domain.questions.models.chunk import DocumentChunk
from src.domain.questions.models.pipeline_job import PipelineJob

from src.domain.education.models.subject import Subject
from src.domain.education.models.chapter import Chapter
from src.domain.education.models.topic import Topic
from src.domain.education.models.skill import Skill
from src.domain.education.models.enrollment import Enrollment
from src.domain.education.models.exam import Exam