# ----- Imports ---- #
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, computed_field
from functools import lru_cache

# ----- Application settings ---- #
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )
    
    # ---- Basic App settings ---- #
    app_name: str
    app_description: str
    app_version: str
    debug: bool
    app_env: str
    
    # ---- Database settings ---- #
    postgres_host: str = Field(..., alias="POSTGRES_HOST")
    postgres_user: str = Field(..., alias="POSTGRES_USER")
    postgres_password: str = Field(..., alias="POSTGRES_PASSWORD")
    postgres_port: int = Field(..., alias="POSTGRES_PORT")
    postgres_db_name: str = Field(..., alias="POSTGRES_DB_NAME")
    
    @computed_field
    @property
    def postgres_full_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}"
            f"{self.postgres_password}@"
            f"{self.postgres_host}:"
            f"{self.postgres_port}/"
            f"{self.postgres_db_name}" 
        )


    # ---- LLM & Embedding settings ---- #
    alibaba_api_key: str = Field(..., alias="ALIBABA_API_KEY")
    alibaba_base_url: str = Field(..., alias="ALIBABA_BASE_URL")
    alibaba_model_name: str = "qwen2.5-vl-72b-instruct"
    alibaba_model_temp: float = 0.2
    
# ---- Instantiate settings ---- #
@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings() # type: ignore