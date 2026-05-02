# ----- Imports ---- #
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, computed_field

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
    
    postgres_orm_echo: bool = Field(default=False)
    postgres_pool_pre_ping: bool = Field(default=True)
    postgres_pool_size: int = Field(default=10)
    postgres_max_overflow: int = Field(default=20)
    postgres_pool_recycle: int = Field(default=3600)
    postgres_pool_timeout: int = Field(default=30)
    
    postgres_auto_commit: bool = Field(default=False)
    postgres_auto_flush: bool = Field(default=False)
    postgres_expire_on_commit: bool = Field(default=False)
    
    @computed_field
    @property
    def postgres_full_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:"
            f"{self.postgres_password}@"
            f"{self.postgres_host}:"
            f"{self.postgres_port}/"
            f"{self.postgres_db_name}"
        )


    # ---- LLM & Embedding settings ---- #
    alibaba_api_key: str = Field(..., alias="ALIBABA_API_KEY")
    alibaba_base_url: str = Field(..., alias="ALIBABA_BASE_URL")
    alibaba_model_name: str = Field(default="qwen2.5-vl-72b-instruct")
    alibaba_model_temp: float = Field(default=0.2)
    
    # ---- Security settings ---- #
    jwt_secret_key: str = Field(..., alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    password_hash_algorithm: str = Field(default="argon2", alias="PASSWORD_HASH_ALGORITHM")
    access_token_expire_minutes: int = Field(default=60, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=14, alias="REFRESH_TOKEN_EXPIRE_DAYS")
    min_password_length: int = Field(default=6, alias="MIN_PASSWORD_LENGTH")
    max_password_length: int = Field(default=48, alias="MAX_PASSWORD_LENGTH")