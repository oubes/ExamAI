# ----- IMPORTS ----- #
import os
from pydantic_settings import BaseSettings, SettingsConfigDict


# ----- SETTINGS ----- #
class Settings(BaseSettings):

    FILE_NAME: str = "Political_history_of_modern_Egypt.pdf"

    CHUNK_SIZE: int = 500

    TEMPERATURE: float = 0.0
    MAX_TOKENS: int = 300

    RECENT_CHUNKS_LIMIT: int = 5

    CHAPTER_THRESHOLD: float = 0.90
    TOPIC_THRESHOLD: float = 0.80
    DRIFT_THRESHOLD: float = 0.60

    BASE_DIR: str = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def get_file_path(self) -> str:
        return os.path.join(self.BASE_DIR, self.FILE_NAME)


# ----- SINGLETON ----- #
settings = Settings()