# ---- Imports ---- #
from functools import lru_cache
from src.core.config.settings import Settings
import logging

# ---- logging ---- #
logger = logging.getLogger(__name__)

# ---- Settings ---- #
# @lru_cache(maxsize=1)
def get_settings():
    return Settings() # type: ignore