from pydantic_settings import BaseSettings, SettingsConfigDict

# ----- Application settings ---- #
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )
    
    # ---- Basic App settings ---- #
    app_name: str
    app_version: str
    debug: bool
    app_env: str
    
    # ---- Database settings ---- #
    