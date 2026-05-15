from pydantic_settings import BaseSettings, SettingsConfigDict

# ---- Settings Class ---- #
class Settings(BaseSettings):
    ingestion_chunk_size: int = 500
    ingestion_chunk_overlap: int = 50

settings = Settings()