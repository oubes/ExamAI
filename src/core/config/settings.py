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
    app_host: str
    app_port: int
    
    @computed_field
    @property
    def app_url(self) -> str:
        return f"http://{self.app_host}:{self.app_port}"
    
    # ---------- Frontend settings ---------- #
    frontend_url: str = Field(..., alias="FRONTEND_URL")

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
    alibaba_model_temp: float = 0.2
    
    alibaba_llm_model_name: str = "qwen2.5-vl-72b-instruct"
    alibaba_llm_max_concurrent_requests: int = 5
    alibaba_llm_max_retries: int = 3
    alibaba_llm_base_delay: float = 1.0
    alibaba_llm_max_context_tokens: int = 4096
    
    alibaba_embeddings_model_name: str = "text-embedding-v3"
    alibaba_embeddings_max_concurrency: int = 5
    alibaba_embeddings_max_retries: int = 3
    alibaba_embeddings_base_delay: float = 1.0
    alibaba_embeddings_max_context_tokens: int = 4096
    alibaba_embeddings_dim: int = 1024


    # ---- Security settings ---- #
    jwt_secret_key: str = Field(..., alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    password_hash_algorithm: str = Field(default="argon2", alias="PASSWORD_HASH_ALGORITHM")
    access_token_expire_minutes: int = 5
    refresh_token_expire_days: int = 14
    min_password_length: int = 6
    max_password_length: int = 48
    
    # ---- Email settings ---- #
    smtp_host: str = Field(..., alias="SMTP_HOST")
    smtp_port: int = Field(..., alias="SMTP_PORT")
    smtp_user: str = Field(..., alias="SMTP_USER")
    smtp_password: str = Field(..., alias="SMTP_PASSWORD")
    smtp_from: str = Field(..., alias="SMTP_FROM")
    email_secret_key: str = Field(..., alias="EMAIL_SECRET_KEY")
    email_algorithm: str = Field(default="HS256", alias="EMAIL_ALGORITHM")
    email_verification_token_expire_minutes: int = 30
    
    # ---- Celery & Redis settings ---- #
    redis_broker_url: str = Field(..., alias="REDIS_BROKER_URL")
    redis_backend_url: str = Field(..., alias="REDIS_BACKEND_URL")
    
    # ---- Rate Limiting settings ---- #
    rate_limit_host: str = Field(..., alias="RATE_LIMIT_HOST")
    rate_limit_port: int = Field(..., alias="RATE_LIMIT_PORT")
    global_rate_limit: tuple = (30, 60) 
    rate_limits: dict = {
        "/api/v1/identity/login": (10, 10),
        "/api/v1/identity/register": (10, 10),
        "/api/v1/identity/reset-password/request": (10, 10),
    }
    
    # ---- Storage settings ---- #
    upload_dir: str = Field(default="storage/uploads", alias="UPLOAD_DIR")