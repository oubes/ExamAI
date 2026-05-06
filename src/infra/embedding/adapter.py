# ---- Imports ----
import logging
from openai import AsyncOpenAI
from src.core.config.settings import Settings

# ---- Logger Initialization ----
logger = logging.getLogger(__name__)


# ---- Embedding Client ----
class EmbeddingClient:

    # ---- Constructor ----
    def __init__(self, settings: Settings):
        logger.debug("Initializing Async OpenAI EmbeddingClient")

        self._client = AsyncOpenAI(
            api_key=settings.alibaba_api_key,
            base_url=settings.alibaba_base_url,
        )

        self._model = settings.alibaba_embeddings_model_name

        logger.debug("Embedding client initialized")

    # ---- Get Client ----
    def get_client(self) -> AsyncOpenAI:
        return self._client

    # ---- Get Model ----
    def get_model(self) -> str:
        return self._model