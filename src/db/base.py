from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass


# ----- importing all models ----- #
from src.db.models.identity import *
from src.db.models.academic import *
from src.db.models.assessment import *
from src.db.models.knowledge import *