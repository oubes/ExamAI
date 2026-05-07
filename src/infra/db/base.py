# ---- Imports ---- #
from sqlalchemy.orm import DeclarativeBase

# ---------- Base Class ---------- #
class Base(DeclarativeBase):
    pass


# ----- importing all models ----- #
from src.domains.identity.models import *

from src.domains.academic.models.enrollment import *
from src.domains.academic.models.exam import *
from src.domains.academic.models.question import *
from src.domains.academic.models.subject import *

from src.domains.assessment.models import *

from src.domains.knowledge.models import *

from src.domains.storage.models import *