# ---- Imports ----
from openai import AsyncOpenAI
from src.core.di.settings import Settings


# ---- LLM Client ----
class LLMClient:

    # ---- Constructor ----
    def __init__(self, settings: Settings):
        self._client = AsyncOpenAI(
            api_key=settings.alibaba_api_key,
            base_url=settings.alibaba_base_url,
        )
        self._model = settings.alibaba_model_name

    # ---- Get Client ----
    def get_client(self) -> AsyncOpenAI:
        return self._client

    # ---- Get Model ----
    def get_model(self) -> str:
        return self._model