# ----- IMPORTS ----- #
from src.services.question.core.settings import settings


# ----- DIFFICULTY RESOLVER ----- #
def get_difficulty_config(level: str) -> dict:

    level = (level or "medium").lower().strip()

    return settings.DIFFICULTY_PROFILE.get(
        level,
        settings.DIFFICULTY_PROFILE["medium"]
    )