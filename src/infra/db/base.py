# ---- Imports ---- #
from sqlalchemy.orm import DeclarativeBase

# ---------- Base Class ---------- #
class Base(DeclarativeBase):
    pass


# ----- importing all models ----- #
from src.domains.identity.models import *
from src.domains.academic.models import *
from src.domains.assessment.models import *
from src.domains.knowledge.models import *